import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from src.app.core.exceptions import ValidationError


class TokenRefresh(BaseModel):
    """Schema for requesting a new token pair using a refresh token."""

    refresh_token: str = Field(..., description="A valid refresh token.")


# ========= Password Management Schemas ===========
class UserPasswordChange(BaseModel):
    """Schema for changing password (authenticated users)."""

    current_password: str = Field(..., description="current password")
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=30,
        description="Strong password",
        examples=["SecurePass123!"],
    )

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValidationError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValidationError(
                "Password must contain at least one special character"
            )
        return v

    @model_validator(mode="after")
    def validate_new_password_is_different(self) -> "UserPasswordChange":
        if self.current_password == self.new_password:
            raise ValidationError("New password must be different from the current one")
        return self


class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset email."""

    email: EmailStr = Field(
        ..., description="The email address to send the reset link to."
    )


class PasswordResetConfirm(BaseModel):
    """Schema for confirming a password reset with a token."""

    token: str = Field(..., description="The password reset token from the email.")
    new_password: str = Field(
        ..., min_length=8, description="The desired new password."
    )
    confirm_password: str = Field(..., description="Confirmation of the new password.")

    @model_validator(mode="after")
    def check_passwords_match(self) -> "PasswordResetConfirm":
        """Ensures that the new password and confirmation match."""
        pw1 = self.new_password
        pw2 = self.confirm_password
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValidationError("Passwords do not match")
        return self

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValidationError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValidationError(
                "Password must contain at least one special character"
            )
        return v


# ------EMAIL--------
class EmailChangeRequest(BaseModel):
    """Schema for a user to request an email change."""

    new_email: EmailStr = Field(..., description="The desired new email address.")


class EmailChangeConfirm(BaseModel):
    """Schema to confirm the email change with a token."""

    token: str = Field(
        ..., description="The email change confirmation token from the email."
    )


class EmailVerificationRequest(BaseModel):
    """Schema for requesting an email verification link."""

    email: EmailStr = Field(
        ..., description="The email address to send the verification link to."
    )
