# app/models/appliance_model.py

import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import func, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from src.app.models.user_model import User
    from src.app.models.bill_model import Bill


class ApplianceCatalog(SQLModel, table=True):
    __tablename__ = "appliance_catalog"

    category_id: str = Field(primary_key=True, index=True)
    label: str = Field(unique=True)
    icon_emoji: str
    typical_wattage: int

    def __repr__(self) -> str:
        return f"<ApplianceCatalog(id='{self.category_id}', label='{self.label}')>"


class UserApplianceBase(SQLModel):
    appliance_catalog_id: Optional[str] = Field(
        default=None, foreign_key="appliance_catalog.category_id"
    )
    custom_name: str
    count: int = Field(default=1)
    custom_wattage: Optional[int] = Field(default=None)
    hours_per_day: float
    days_per_week: int
    brand: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    star_rating: Optional[int] = Field(default=None)
    purchase_year: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class UserAppliance(UserApplianceBase, table=True):
    __tablename__ = "user_appliances"

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
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    bill_id: uuid.UUID = Field(foreign_key="bills.id", index=True, nullable=False)

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

    user: "User" = Relationship(back_populates="user_appliances")
    bill: "Bill" = Relationship(back_populates="user_appliances")
    estimates: List["ApplianceEstimate"] = Relationship(back_populates="user_appliance")

    def __repr__(self) -> str:
        return f"<UserAppliance(id='{self.id}', user_id='{self.user_id}', custom_name='{self.custom_name}')>"


class ApplianceEstimateBase(SQLModel):
    estimated_kwh: float
    estimated_cost: float


class ApplianceEstimate(ApplianceEstimateBase, table=True):
    __tablename__ = "appliance_estimates"

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

    bill_id: uuid.UUID = Field(foreign_key="bills.id", index=True, nullable=False)
    user_appliance_id: uuid.UUID = Field(
        foreign_key="user_appliances.id", index=True, nullable=False
    )

    bill: "Bill" = Relationship(back_populates="estimates")
    user_appliance: "UserAppliance" = Relationship(back_populates="estimates")

    def __repr__(self) -> str:
        return f"<ApplianceEstimate(id='{self.id}', bill_id='{self.bill_id}')>"
