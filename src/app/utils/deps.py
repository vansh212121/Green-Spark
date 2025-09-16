import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, Request, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.app.core.config import settings
from src.app.core.security import token_manager, TokenType
from src.app.db.session import get_session
from src.app.models.user_model import User

from src.app.core.exceptions import (
    InvalidToken,
    NotAuthorized,
    ResourceNotFound,
    InactiveUser,
    UnverifiedUser,
    TokenRevoked,
    RateLimitExceeded,
)
from src.app.models.user_model import User, UserRole
from src.app.services.user_service import UserService
from src.app.services.rate_limit_service import (
    RateLimitService,
    rate_limit_service as _rate_limit_singleton,
)

logger = logging.getLogger(__name__)

# OAuth2 schemes
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", description="JWT Access Token"
)
# Optional scheme: does NOT auto-raise 401 if header missing
optional_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    description="JWT Access Token",
    auto_error=False,
)


# # ==== Service Providers (explicit for testability) ====
def get_user_service() -> UserService:
    return UserService()


def get_rate_limit_service() -> RateLimitService:
    return _rate_limit_singleton


# ================== CORE AUTHENTICATION ==================
async def _authenticate_user_from_token(
    request: Request,
    db: AsyncSession,
    token: str,
    user_svc: UserService,
    rate_limit_svc: RateLimitService,
) -> User:
    """
    Core auth routine: validates token, checks revocation, returns User.
    Applies auth-specific rate limiting by client IP on failure bursts.
    """
    client_ip = request.client.host if request.client else "unknown"

    # Brute-force protection (auth attempts)
    lockout_seconds = int(getattr(settings, "AUTH_LOCKOUT_SECONDS", 300))
    if await rate_limit_svc.is_auth_rate_limited(
        client_ip,
        max_attempts=5,
    ):
        raise RateLimitExceeded(
            detail="Too many failed authentication attempts.",
            retry_after=lockout_seconds,
        )

    # Verify token
    try:
        payload = await token_manager.verify_token(
            token, expected_type=TokenType.ACCESS
        )
        sub = payload.get("sub")
        if sub is None:
            raise InvalidToken(
                detail="Token subject (sub) is missing.", token_type="access"
            )
        user_id = uuid.UUID(sub)
    except InvalidToken:
        await rate_limit_svc.record_failed_auth_attempt(
            client_ip, lockout_duration=lockout_seconds
        )
        raise

    # Load user
    user = await user_svc.get_user_for_auth(db=db, user_id=user_id)
    if not user:
        # Treat unknown user as a not found (and not as auth failure) to avoid info leaks
        raise ResourceNotFound(resource_type="User", resource_id=str(user_id))

    # Token revocation check
    # We only compare if token has iat; if missing, treat as invalid token.
    iat = payload.get("iat")
    if iat is None:
        await rate_limit_svc.record_failed_auth_attempt(
            client_ip, lockout_duration=lockout_seconds
        )
        raise InvalidToken(detail="Token is missing 'iat' claim.", token_type="access")

    # if user.tokens_valid_from_utc:
    #     token_issued_at = datetime.fromtimestamp(iat, tz=timezone.utc)
    #     if token_issued_at < user.tokens_valid_from_utc:
    #         await rate_limit_svc.record_failed_auth_attempt(
    #             client_ip, lockout_duration=lockout_seconds
    #         )
    #         raise TokenRevoked()

    if user.tokens_valid_from_utc:
        token_issued_at = datetime.fromtimestamp(iat, tz=timezone.utc)

        # Defensively handle the type from the cache
        revocation_timestamp = user.tokens_valid_from_utc
        if isinstance(revocation_timestamp, str):
            revocation_timestamp = datetime.fromisoformat(revocation_timestamp)

        # Now, both are guaranteed to be datetime objects
        if token_issued_at < revocation_timestamp:
            await rate_limit_svc.record_failed_auth_attempt(client_ip)
            raise TokenRevoked()

    # Success path: clear failures and attach to request
    await rate_limit_svc.clear_failed_auth_attempts(client_ip)
    request.state.user = user
    request.state.user_id = str(user.id)
    return user


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_session),
    token: str = Depends(reusable_oauth2),
    user_svc: UserService = Depends(get_user_service),
    rate_limit_svc: RateLimitService = Depends(get_rate_limit_service),
) -> User:
    """Primary authentication dependency. Validates JWT and returns current user."""
    return await _authenticate_user_from_token(
        request, db, token, user_svc, rate_limit_svc
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        logger.warning(
            "Inactive user attempted access",
            extra={"user_id": str(current_user.id), "user_email": current_user.email},
        )
        raise InactiveUser()
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Ensure the current user is verified."""
    if not current_user.is_verified:
        logger.info(
            "Unverified user attempted access",
            extra={"user_id": str(current_user.id), "user_email": current_user.email},
        )
        raise UnverifiedUser()
    return current_user


class RoleChecker:
    """
    Dependency class for role-based access control.
    Uses hierarchical role checking based on UserRole enum priorities.
    """

    def __init__(self, required_role: UserRole):
        self.required_role = required_role

    def __call__(
        self, request: Request, current_user: User = Depends(get_current_active_user)
    ) -> User:
        """Check if user has sufficient role privileges."""

        # 1. Explicitly convert the current user's role (which might be a string)
        current_user_role_enum = UserRole(current_user.role)

        # 2. Compare the integer priorities directly. This is foolproof.
        if current_user_role_enum.priority < self.required_role.priority:
            logger.warning(
                "Insufficient privileges for user.",
                extra={
                    "user_id": str(current_user.id),
                    "user_role": current_user.role,
                    "required_role": self.required_role.value,
                    "path": request.url.path,
                },
            )
            raise NotAuthorized(
                f"Insufficient privileges. A role of '{self.required_role.value}' or higher is required."
            )

        return current_user


# Role-based dependency instances
require_user = RoleChecker(UserRole.USER)
require_admin = RoleChecker(UserRole.ADMIN)


# ================== RATE LIMITING ==================
class RateLimitChecker:
    """
    Dependency for rate limiting. Delegates actual limiting logic to service layer.
    """

    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        identifier_type: str = "ip",  # "ip" or "user"
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.identifier_type = identifier_type

    async def __call__(
        self,
        request: Request,
        rate_limit_svc: RateLimitService = Depends(get_rate_limit_service),
    ):
        """Check rate limits using service layer."""
        if self.identifier_type == "user":
            user = getattr(request.state, "user", None)
            identifier = (
                f"user:{user.id}"
                if user
                else f"ip:{request.client.host if request.client else 'unknown'}"
            )
        else:
            identifier = f"ip:{request.client.host if request.client else 'unknown'}"

        if await rate_limit_svc.is_rate_limited(
            identifier, self.max_requests, self.window_seconds
        ):
            logger.warning(f"Rate limit exceeded for {identifier}")
            raise RateLimitExceeded(
                detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds.",
                retry_after=self.window_seconds,
            )


# Preconfigured instances
rate_limit_auth = RateLimitChecker(
    max_requests=5, window_seconds=60, identifier_type="ip"
)
rate_limit_api = RateLimitChecker(
    max_requests=35, window_seconds=60, identifier_type="user"
)
rate_limit_heavy = RateLimitChecker(
    max_requests=10, window_seconds=60, identifier_type="user"
)
rate_limit_refresh = RateLimitChecker(
    max_requests=3, window_seconds=86400, identifier_type="user"
)


# ================== UTILITY DEPS ==================
class PaginationParams:
    """Pagination parameters for list endpoints."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(
            20,
            ge=1,
            le=int(getattr(settings, "MAX_PAGE_SIZE", 100)),
            description="Page size",
        ),
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


async def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(
        20,
        ge=1,
        le=int(getattr(settings, "MAX_PAGE_SIZE", 100)),
        description="Page size",
    ),
) -> PaginationParams:
    """Get pagination parameters as a dependency."""
    return PaginationParams(page=page, size=size)


# ================== HEALTH CHECK ==================
async def get_health_status() -> Dict[str, Any]:
    """Health check dependency. Delegate to a service if checks are complex."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": getattr(settings, "APP_VERSION", "unknown"),
    }


# ================== REQUEST CONTEXT ==================
def _client_ip_from_headers(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    xri = request.headers.get("x-real-ip")
    if xri:
        return xri.strip()
    return request.client.host if request.client else "unknown"


async def get_request_context(request: Request) -> dict:
    """Extract common request context information."""
    return {
        "client_ip": getattr(request.state, "client_ip", None)
        or _client_ip_from_headers(request),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "path": request.url.path,
        "method": request.method,
        "request_id": getattr(request.state, "request_id", None),
        "user_id": getattr(request.state, "user_id", None),
    }


# ================== OPTIONAL AUTH ==================
async def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_session),
    token: Optional[str] = Depends(optional_oauth2),
    user_svc: UserService = Depends(get_user_service),
    rate_limit_svc: RateLimitService = Depends(get_rate_limit_service),
) -> Optional[User]:
    """
    Optional authentication - returns None if no valid token.
    Useful for endpoints that work for both authenticated and anonymous users.
    """
    if not token:
        return None
    try:
        return await _authenticate_user_from_token(
            request, db, token, user_svc, rate_limit_svc
        )
    except (InvalidToken, ResourceNotFound, TokenRevoked):
        return None
