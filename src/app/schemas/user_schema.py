import re
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import uuid

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)
from src.app.core.exceptions import ValidationError
from src.app.models.user_model import UserRole


class UserBase(BaseModel):
    first_name: str = Field(
        ...,
        min_length=2,
        max_length=25,
        description="User's first name",
        examples=["John"],
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=25,
        description="User's full name",
        examples=["Doe"],
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=25,
        description="Unique username",
    )
    email: EmailStr = Field(
        ..., description="User's email address", examples=["user@example.com"]
    )
    timezone: str = Field(
        ...,
        examples=["Delhi/Mumbai"],
        description="User's City",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValidationError(
                "Username can only contain letters, numbers, underscores and hyphens"
            )
        return v.lower().strip()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        """Validate and clean names."""
        return " ".join(v.strip().split())


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=30,
        description="Strong password",
        examples=["SecurePass123!"],
    )

    @field_validator("password")
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

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe21",
                "password": "SecurePass123!",
                "timezone": "Delhi/Mumbai",
            }
        }
    )


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=25,
        description="User's New First name",
        examples=["John"],
    )
    last_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=25,
        description="User's New Last name",
        examples=["Doe"],
    )
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=25,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique username",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValidationError(
                "Username can only contain letters, numbers, underscores and hyphens"
            )
        return v.lower().strip()

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        """Validate and clean names."""
        return " ".join(v.strip().split())

    @model_validator(mode="before")
    @classmethod
    def validate_at_least_one_field(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure at least one field is provided for update."""
        if isinstance(values, dict) and not any(v is not None for v in values.values()):
            raise ValidationError("At least one field must be provided for update")
        return values


# ======== Response Schemas =========
class UserResponse(UserBase):
    """Basic user response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="User ID")
    role: UserRole = Field(..., description="User role")
    is_verified: bool = Field(..., description="Email verification status")
    is_active: bool = Field(..., description="Account active status")
    created_at: datetime = Field(..., description="Registration timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# ======== List and Search Schemas =========
class UserListResponse(BaseModel):
    """Response for paginated user list."""

    items: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., ge=0, description="Total number of users")
    page: int = Field(..., ge=1, description="Current page number")
    pages: int = Field(..., ge=0, description="Total number of pages")
    size: int = Field(..., ge=1, le=100, description="Number of items per page")

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class UserSearchParams(BaseModel):
    """Parameters for searching users."""

    search: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Search in email, username, full name",
    )
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_verified: Optional[bool] = Field(
        None, description="Filter by verification status"
    )
    timezone: Optional[str] = Field(None, description="User's City")
    created_after: Optional[date] = Field(
        None, description="Filter users created after this date"
    )
    created_before: Optional[date] = Field(
        None, description="Filter users created before this date"
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "UserSearchParams":
        """Ensure date range is valid."""
        if self.created_after and self.created_before:
            if self.created_after > self.created_before:
                raise ValidationError("created_after must be before created_before")
        return self


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    # Response schemas
    "UserResponse",
    "UserBasicResponse",
    "UserPublicResponse",
    # List schemas
    "UserListResponse",
    # List and Search Schemas
    "UserSearchParams",
]
