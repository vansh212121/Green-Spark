import logging
import secrets
import re
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from src.app.core.config import settings
from src.app.core.exceptions import (
    InternalServerError,
    InvalidToken,
    TokenExpired,
    TokenRevoked,
    TokenTypeInvalid,
)
from src.app.db.redis_conn import redis_client


# --- Setup ---
logger = logging.getLogger(__name__)


# ---- Enums & Config ----
class TokenType(str, Enum):
    """Defines the types of tokens the system can issue."""

    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change"


def _aud_list(aud: Union[str, List[str]]) -> Union[str, List[str]]:
    """Normalize audience to jose-acceptable type."""
    if isinstance(aud, str) and "," in aud:
        return [a.strip() for a in aud.split(",") if a.strip()]
    return aud


class SecurityConfig:
    """Validates and holds all security-related configurations."""

    JWT_SECRET_KEY: str = settings.JWT_SECRET
    JWT_ALGORITHM: str = getattr(settings, "JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)
    )
    TOKEN_ISSUER: str = getattr(settings, "TOKEN_ISSUER", "my-app")
    TOKEN_AUDIENCE: Union[str, List[str]] = _aud_list(
        getattr(settings, "TOKEN_AUDIENCE", "my-app:users")
    )
    ENABLE_TOKEN_BLACKLIST: bool = bool(
        getattr(settings, "ENABLE_TOKEN_BLACKLIST", True)
    )
    REDIS_FAIL_SECURE: bool = bool(getattr(settings, "REDIS_FAIL_SECURE", True))
    JWT_LEEWAY_SECONDS: int = int(
        getattr(settings, "JWT_LEEWAY_SECONDS", 10)
    )  # clock skew leeway

    @classmethod
    def validate(cls) -> None:
        if not cls.JWT_SECRET_KEY or len(cls.JWT_SECRET_KEY) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be configured and be at least 32 characters long."
            )


SecurityConfig.validate()


# ---- Password Management ----
class PasswordManager:
    """Encapsulates all password hashing and verification logic (Argon2 preferred)."""

    pwd_context = CryptContext(
        schemes=["argon2", "bcrypt"],
        deprecated="auto",
        argon2__time_cost=2,
        argon2__memory_cost=51200,  # ~50MB
        argon2__parallelism=2,
    )

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a plain-text password."""
        try:
            return cls.pwd_context.hash(password)
        except Exception:
            logger.critical("Password hashing failed.", exc_info=True)
            raise InternalServerError(detail="Could not process password.")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a hash."""
        try:
            return cls.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            logger.warning(
                "Password verification failed due to a malformed hash or other error."
            )
            return False

    @classmethod
    def needs_rehash(cls, hashed_password: str) -> bool:
        """Check if a hash needs to be updated to the latest parameters."""
        return cls.pwd_context.needs_update(hashed_password)

    @classmethod
    def upgrade_hash_if_needed(
        cls, plain_password: str, hashed_password: str
    ) -> Tuple[bool, str]:
        """
        Verify and transparently re-hash to stronger params if needed.
        Returns (upgraded, hash).
        """
        if not cls.verify_password(plain_password, hashed_password):
            return False, hashed_password
        if cls.needs_rehash(hashed_password):
            return True, cls.hash_password(plain_password)
        return False, hashed_password


# ---- Token Management ----
class TokenManager:
    """Low-level token operations - creation, verification, revocation/blacklist."""

    config = SecurityConfig

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _ts(dt: datetime) -> int:
        return int(dt.timestamp())

    def _default_expiry(self, token_type: TokenType) -> timedelta:
        if token_type == TokenType.ACCESS:
            return timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)
        if token_type == TokenType.REFRESH:
            return timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)
        return timedelta(hours=1)

    def create_token(
        self,
        subject: Union[str, int],
        token_type: TokenType,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a JWT with specified type and claims."""
        now = self._now_utc()
        expires_delta = expires_delta or self._default_expiry(token_type)
        exp = now + expires_delta

        claims: Dict[str, Any] = {
            "sub": str(subject),
            "exp": self._ts(exp),
            "iat": self._ts(now),
            "nbf": self._ts(now),
            "iss": self.config.TOKEN_ISSUER,
            "aud": self.config.TOKEN_AUDIENCE,
            "jti": str(uuid.uuid4()),
            "type": token_type.value,
        }
        if additional_claims:
            claims.update(additional_claims)

        return jwt.encode(
            claims, self.config.JWT_SECRET_KEY, algorithm=self.config.JWT_ALGORITHM
        )

    # Convenience issuers
    def issue_access_token(self, subject: Union[str, int], **kwargs: Any) -> str:
        return self.create_token(subject, TokenType.ACCESS, **kwargs)

    def issue_refresh_token(self, subject: Union[str, int], **kwargs: Any) -> str:
        return self.create_token(subject, TokenType.REFRESH, **kwargs)

    def issue_pair(self, subject: Union[str, int]) -> Dict[str, str]:
        """Issue access and refresh token pair."""
        return {
            "access_token": self.issue_access_token(subject),
            "refresh_token": self.issue_refresh_token(subject),
            "token_type": "bearer",
        }

    async def verify_token(
        self, token: str, expected_type: TokenType
    ) -> Dict[str, Any]:
        """Verify and decode a JWT; validate iss/aud/exp/nbf; check type and blacklist."""
        if not token:
            raise InvalidToken("Token cannot be empty.")

        try:
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                algorithms=[self.config.JWT_ALGORITHM],
                audience=self.config.TOKEN_AUDIENCE,
                issuer=self.config.TOKEN_ISSUER,
                options={"leeway": self.config.JWT_LEEWAY_SECONDS},
            )

            token_type = payload.get("type")
            if token_type != expected_type.value:
                raise TokenTypeInvalid(
                    f"Expected '{expected_type.value}' token, but got '{token_type}'.",
                    expected=expected_type.value,
                    received=token_type,
                )

            if self.config.ENABLE_TOKEN_BLACKLIST:
                jti = payload.get("jti")
                if not jti:
                    raise InvalidToken("Token is missing the required 'jti' claim.")
                if await self.is_token_revoked(jti):
                    raise TokenRevoked()

            return payload

        except jwt.ExpiredSignatureError:
            raise TokenExpired() from None

        # 2. Specifically catch other known JWT errors
        except JWTError as e:
            raise InvalidToken(f"Token signature or claims are invalid: {e}") from e

        # 3. Catch ANY other exception (like "Not enough segments", etc.)
        #    and wrap it in our standard InvalidToken error to prevent a 500.
        except Exception as e:
            logger.warning(f"Token decode failed with an unexpected error: {e}")
            raise InvalidToken("Token is invalid or malformed.") from e

    # ---- Blacklist operations ----
    async def revoke_token(self, token: str, reason: str = "Revoked") -> bool:
        """Revoke a token by extracting its JTI and calculating TTL in Redis."""
        if not self.config.ENABLE_TOKEN_BLACKLIST:
            return False

        if redis_client is None:
            # Decide on fail-secure behavior
            if self.config.REDIS_FAIL_SECURE:
                logger.error(
                    "Redis unavailable; cannot revoke token in fail-secure mode."
                )
            return False

        try:
            # Decode without verifying signature/exp to read claims
            payload = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if not jti or not exp:
                return False

            remaining_time = exp - self._ts(self._now_utc())
            if remaining_time <= 0:
                return True  # Already expired

            key = f"revoked_token:{jti}"
            await redis_client.set(key, reason, ex=remaining_time)
            logger.info(f"Token revoked: {jti}")
            return True
        except Exception:
            logger.error("Failed to revoke token.", exc_info=True)
            return False

    async def revoke_by_jti(
        self, jti: str, exp_ts: int, reason: str = "Revoked"
    ) -> bool:
        """Revoke by JTI directly when claims already parsed."""
        if not self.config.ENABLE_TOKEN_BLACKLIST or not jti:
            return False
        if redis_client is None:
            if self.config.REDIS_FAIL_SECURE:
                logger.error(
                    "Redis unavailable; cannot revoke by JTI in fail-secure mode."
                )
            return False
        try:
            remaining_time = exp_ts - self._ts(self._now_utc())
            if remaining_time <= 0:
                return True
            key = f"revoked_token:{jti}"
            await redis_client.set(key, reason, ex=remaining_time)
            return True
        except Exception:
            logger.error("Failed to revoke token by JTI.", exc_info=True)
            return False

    async def is_token_revoked(self, jti: str) -> bool:
        """Check if a token's JTI is blacklisted."""
        if not self.config.ENABLE_TOKEN_BLACKLIST:
            return False

        if redis_client is None:
            msg = "Token validation service unavailable"
            logger.error("Redis client is None in is_token_revoked.")
            if self.config.REDIS_FAIL_SECURE:
                # Fail-secure: reject tokens if we can't check revocation
                raise InternalServerError(msg)
            return False

        try:
            key = f"revoked_token:{jti}"
            exists = await redis_client.exists(key)
            return bool(exists)
        except Exception:
            logger.error(
                "Failed to check token revocation status in Redis.", exc_info=True
            )
            if self.config.REDIS_FAIL_SECURE:
                raise InternalServerError("Token validation service unavailable")
            return False

    @staticmethod
    def decode_token_unsafe(token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification - for utility purposes only."""
        try:
            return jwt.decode(
                token, "", options={"verify_signature": False, "verify_exp": False}
            )
        except Exception:
            return None

    @staticmethod
    def get_jti(token: str) -> Optional[str]:
        """Extract JTI from token without verification."""
        data = TokenManager.decode_token_unsafe(token)
        return data.get("jti") if data else None


# ---- Security Utilities ----
def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure, URL-safe random token."""
    return secrets.token_urlsafe(length)


def constant_time_compare(val1: str, val2: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks."""
    return secrets.compare_digest(val1 or "", val2 or "")


# ---- Singleton Instances ----
password_manager = PasswordManager()
token_manager = TokenManager()


class SecurityHeaders:
    """Centralized definition of security headers for API responses."""

    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Return a dictionary of recommended baseline security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }
