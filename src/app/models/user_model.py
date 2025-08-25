# app/models/user_model.py
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum
from sqlalchemy import func, Column, String, DateTime
from sqlalchemy.dialects.postgresql import (
    UUID as PG_UUID,
)
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from src.app.models.bill_model import Bill
    from src.app.models.appliance_model import UserAppliance
    from src.app.models.insights_model import Insight


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"

    @property
    def priority(self) -> int:
        priorities = {self.USER: 1, self.ADMIN: 2}
        return priorities.get(self, 0)

    def __lt__(self, other: "UserRole") -> bool:
        if not isinstance(other, UserRole):
            return NotImplemented
        return self.priority < other.priority


# This is the base model. It contains all the fields that are common
class UserBase(SQLModel):
    email: str = Field(
        sa_column=Column(String(200), unique=True, nullable=False, index=True)
    )
    first_name: str = Field(index=True)
    last_name: str
    username: str = Field(
        sa_column=Column(String(25), nullable=False, index=True, unique=True)
    )
    role: UserRole = Field(
        sa_column=Column(SAEnum(UserRole), nullable=False, index=True),
        default=UserRole.USER,
    )
    # --- ADDED timezone field ---
    timezone: str = Field(default="Asia/Mumbai", nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)


# This is the database table model.
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(
            PG_UUID(as_uuid=True),
            server_default=func.gen_random_uuid(),
            primary_key=True,
            index=True,
            nullable=False,
        ),
    )

    hashed_password: str = Field(nullable=False, exclude=True)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )
    tokens_valid_from_utc: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # RELATIONSHIPS
    bills: List["Bill"] = Relationship(back_populates="user")
    user_appliances: List["UserAppliance"] = Relationship(back_populates="user")
    insights: List["Insight"] = Relationship(back_populates="user")

    # --- Computed properties (data-focused) ---
    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:
        return f"<User(id='{self.id}', email='{self.email}')>"
