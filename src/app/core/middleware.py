from __future__ import annotations

import ipaddress
import logging
import time
import uuid
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders, State
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.security import SecurityHeaders

# logger = logging.getLogger(__name__)
logger = logging.getLogger("uvicorn.error")


def _get_header(scope: Scope, name: str) -> Optional[str]:
    target = name.lower().encode()
    for k, v in scope.get("headers", []):
        if k.lower() == target:
            try:
                return v.decode()
            except Exception:
                return None
    return None


def _parse_query_params(scope: Scope) -> List[Tuple[str, str]]:
    try:
        from urllib.parse import parse_qsl

        query_string = scope.get("query_string", b"")
        return parse_qsl(query_string.decode("utf-8", "ignore"), keep_blank_values=True)
    except Exception:
        return []


def _sanitize_params(
    params: List[Tuple[str, str]], mask_fields: Set[str]
) -> Dict[str, Any]:
    masked = {}
    for k, v in params:
        if k.lower() in mask_fields:
            masked[k] = "***"
        else:
            masked[k] = v
    return masked


def _client_ip(scope: Scope, trust_forwarded: bool, trusted_proxies: List[str]) -> str:
    client_host = (scope.get("client") or ("unknown", 0))[0]
    if not trust_forwarded:
        return client_host

    def _is_trusted(ip: str) -> bool:
        try:
            ip_addr = ipaddress.ip_address(ip)
            for net in trusted_proxies:
                try:
                    if ip_addr in ipaddress.ip_network(net, strict=False):
                        return True
                except Exception:
                    # allow single IPs too
                    if ip == net:
                        return True
        except Exception:
            pass
        return False

    # Only trust forwarded headers if the immediate client is a trusted proxy
    if not _is_trusted(client_host):
        return client_host

    # RFC 7239 Forwarded header
    fwd = _get_header(scope, "Forwarded")
    if fwd:
        # Forwarded: for=1.2.3.4, for="[2001:db8:cafe::17]"
        for part in fwd.split(";"):
            for item in part.split(","):
                item = item.strip()
                if item.lower().startswith("for="):
                    val = item[4:].strip().strip('"')
                    # Remove IPv6 brackets if present
                    if val.startswith("[") and val.endswith("]"):
                        val = val[1:-1]
                    return val

    # X-Forwarded-For (first IP is the original client)
    xff = _get_header(scope, "X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()

    # X-Real-IP
    xri = _get_header(scope, "X-Real-IP")
    if xri:
        return xri.strip()

    return client_host


class ProfessionalLoggingMiddleware:
    """
    ASGI logging middleware with:
    - Request ID propagation (accepts X-Request-ID or X-Correlation-ID).
    - Proxy-aware client IP (optional trusted proxies).
    - Sanitized query params.
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[Set[str]] = None,
        request_id_header: str = "X-Request-ID",
        accept_request_id_headers: Iterable[str] = ("X-Request-ID", "X-Correlation-ID"),
        mask_query_params: Optional[Set[str]] = None,
        trust_forwarded_headers: bool = False,
        trusted_proxies: Optional[List[str]] = None,
    ) -> None:
        self.app = app
        self.exclude_paths = exclude_paths or {
            "/health",
            "/metrics",
            "/favicon.ico",
            "/docs",
            "/redoc",
            "/openapi.json",
        }
        self.request_id_header = request_id_header
        self.accept_request_id_headers = tuple(accept_request_id_headers)
        self.mask_query_params = {
            "password",
            "passwd",
            "secret",
            "token",
            "access_token",
            "refresh_token",
            "authorization",
            "api_key",
            "apikey",
            "client_secret",
            "key",
        }
        if mask_query_params:
            self.mask_query_params |= {m.lower() for m in mask_query_params}

        self.trust_forwarded_headers = trust_forwarded_headers
        self.trusted_proxies = trusted_proxies or []

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path") or ""
        method = scope.get("method") or "GET"
        should_log = path not in self.exclude_paths

        if "state" not in scope:
            scope["state"] = {}

        incoming_request_id = None
        for h in self.accept_request_id_headers:
            incoming_request_id = incoming_request_id or _get_header(scope, h)

        request_id = incoming_request_id or str(uuid.uuid4())

        # Directly set the attribute on the state object provided by the framework
        scope["state"]["request_id"] = request_id

        # Sanitize query params for logging
        params = _sanitize_params(_parse_query_params(scope), self.mask_query_params)
        client_ip = _client_ip(
            scope,
            trust_forwarded=self.trust_forwarded_headers,
            trusted_proxies=self.trusted_proxies,
        )
        user_agent = _get_header(scope, "User-Agent") or "unknown"

        # Pre-log
        if should_log:
            content_length = _get_header(scope, "Content-Length")
            try:
                content_len_int = int(content_length) if content_length else None
            except Exception:
                content_len_int = None

            if content_len_int and content_len_int > getattr(
                settings, "MAX_REQUEST_SIZE", 10 * 1024 * 1024
            ):
                logger.warning(
                    "Large request detected",
                    extra={
                        "request_id": request_id,
                        "content_length": content_len_int,
                        "path": path,
                    },
                )

            logger.info(
                "Incoming request",
                extra={
                    "request_id": request_id,
                    "client_ip": client_ip,
                    "method": method,
                    "path": path,
                    "query_params": params or None,
                    "user_agent": user_agent,
                    "scheme": scope.get("scheme", "http"),
                    "host": _get_header(scope, "host"),
                },
            )

        start = time.perf_counter()

        # Intercept send to inject X-Request-ID and capture status/size
        status_code = 500
        response_bytes = 0

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, response_bytes
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                headers = MutableHeaders(raw=message.setdefault("headers", []))
                headers[self.request_id_header] = request_id
            elif message["type"] == "http.response.body":
                body = message.get("body", b"") or b""
                response_bytes += len(body)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            # Error will be handled by exception handlers. Still log timing here.
            duration_ms = (time.perf_counter() - start) * 1000
            if should_log:
                logger.error(
                    "Request failed",
                    extra={
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "process_time_ms": round(duration_ms, 2),
                    },
                    exc_info=True,
                )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        if should_log:
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": status_code,
                    "process_time_ms": round(duration_ms, 2),
                    "response_size": response_bytes or None,
                },
            )


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(raw=message.setdefault("headers", []))

                # ✅ preserve CORS headers set earlier
                # (they will already exist here if CORSMiddleware added them)

                # Add your own security headers without nuking others
                for k, v in SecurityHeaders.get_headers().items():
                    if k not in headers:  # don't overwrite
                        headers[k] = v

                if scope.get("scheme") == "https":
                    headers.setdefault(
                        "Strict-Transport-Security",
                        "max-age=31536000; includeSubDomains; preload",
                    )

                content_type = headers.get("content-type", "")
                if content_type and "text/html" in content_type.lower():
                    headers.setdefault(
                        "Content-Security-Policy",
                        "default-src 'self'; "
                        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                        "img-src 'self' data: https://fastapi.tiangolo.com; "
                        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
                    )
                else:
                    headers.setdefault(
                        "Content-Security-Policy",
                        "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
                    )

                state = scope.get("state")
                if state and hasattr(state, "request_id"):
                    headers["X-Request-ID"] = getattr(state, "request_id")

            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestSizeLimitMiddleware:
    """
    Rejects requests with Content-Length greater than `max_size`.
    Note:
      - If Content-Length is missing (e.g., chunked), this middleware won't enforce the size.
        Use your reverse proxy (Nginx/Envoy) to enforce body size in those cases.
    """

    def __init__(self, app: ASGIApp, max_size: int = 10 * 1024 * 1024) -> None:
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_length = _get_header(scope, "Content-Length")
        try:
            received_size = int(content_length) if content_length else None
        except Exception:
            received_size = None

        if received_size is not None and received_size > self.max_size:
            # Keep error shape consistent with the rest of the API
            state = scope.get("state")
            request_id = (
                getattr(state, "request_id", None) if isinstance(state, State) else None
            )

            headers = {}
            if request_id:
                headers["X-Request-ID"] = request_id

            response = JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": f"Request payload exceeds maximum size of {self.max_size} bytes",
                        "status_code": 413,
                        "context": {
                            "max_size": self.max_size,
                            "received_size": received_size,
                        },
                    }
                },
                headers=headers,
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


def register_middlewares(app: FastAPI) -> None:
    """
    Register all application middlewares.

    Correct Middleware Order Strategy:
      1. Logging/Error Handling (as outermost to catch everything).
      2. CORS (must run early to handle preflight OPTIONS requests and add headers).
      3. Trusted Host (can run after CORS).
      4. Security Headers.
      5. GZip compression.
      6. Request Size Limit (as innermost to reject large bodies before they are processed).
    """
    allowed_hosts = _get_allowed_hosts()
    cors_origins = _get_cors_origins()

    # 1) Logging (outermost)
    exclude_paths = getattr(
        settings,
        "LOGGING_EXCLUDE_PATHS",
        {"/health", "/metrics", "/favicon.ico", "/docs", "/redoc", "/openapi.json"},
    )
    trusted_proxies = []
    if getattr(settings, "TRUSTED_PROXIES", None):
        trusted_proxies = [
            p.strip() for p in settings.TRUSTED_PROXIES.split(",") if p.strip()
        ]

    app.add_middleware(
        ProfessionalLoggingMiddleware,
        exclude_paths=set(exclude_paths),
        trust_forwarded_headers=bool(
            getattr(settings, "TRUST_FORWARDER_HEADERS", False)
        )
        or bool(getattr(settings, "TRUST_FORWARDED_HEADERS", False)),
        trusted_proxies=trusted_proxies,
    )

    # 2) CORS
    allow_credentials = True
    if any(o == "*" for o in cors_origins):
        allow_credentials = False
        logger.warning(
            "CORS: '*' detected; forcing allow_credentials=False for compliance"
        )

    cors_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    cors_headers = ["*"]
    expose_headers = ["X-Request-ID", "Retry-After", "Content-Disposition"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=cors_methods,
        allow_headers=cors_headers,
        expose_headers=expose_headers,
    )

    # 3) Trusted Host
    if allowed_hosts and "*" not in allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    else:
        logger.warning(
            "TrustedHostMiddleware disabled: ALLOWED_HOSTS contains '*' or is not configured"
        )

    # 4) Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # 5) GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 6) Request size limit
    max_request_size = int(getattr(settings, "MAX_REQUEST_SIZE", 10 * 1024 * 1024))
    app.add_middleware(RequestSizeLimitMiddleware, max_size=max_request_size)

    logger.info("All middlewares registered successfully with corrected order")


def _get_allowed_hosts() -> List[str]:
    """Validate and return allowed hosts configuration."""
    if not getattr(settings, "ALLOWED_HOSTS", None):
        logger.warning("ALLOWED_HOSTS not configured, using restrictive default")
        return ["localhost", "127.0.0.1"]

    hosts = [h.strip() for h in settings.ALLOWED_HOSTS.split(",") if h.strip()]
    if not hosts:
        logger.warning(
            "ALLOWED_HOSTS is empty after parsing, using restrictive default"
        )
        return ["localhost", "127.0.0.1"]

    logger.info(f"Configured allowed hosts: {hosts}")
    return hosts


def _get_cors_origins() -> List[str]:
    """Validate, normalize, and expand CORS origins configuration."""
    raw = getattr(settings, "CORS_ORIGINS", None)
    if not raw:
        logger.warning("CORS_ORIGINS not configured, using restrictive default")
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]

    # 1) Split and normalize
    origins = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    logger.info(f"CORS_ORIGINS configured: {origins}")

    # 2) Expand localhost ↔ 127.0.0.1
    expanded = set(origins)
    for origin in list(origins):
        if "localhost" in origin:
            expanded.add(origin.replace("localhost", "127.0.0.1"))
        if "127.0.0.1" in origin:
            expanded.add(origin.replace("127.0.0.1", "localhost"))

    # 3) Warn on '*' + credentials
    if "*" in expanded:
        logger.warning(
            "CORS: '*' detected. Remember: Access-Control-Allow-Origin will be suppressed "
            "if allow_credentials=True. Consider using explicit origins instead."
        )

    final = sorted(expanded)
    logger.info(f"CORS_ORIGINS final (after expansion): {final}")
    return final
