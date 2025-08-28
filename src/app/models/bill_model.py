# app/models/bill_model.py

import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, TYPE_CHECKING, List
from enum import Enum as PyEnum

from sqlalchemy import func, Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from src.app.models.user_model import User
    from src.app.models.appliance_model import ApplianceEstimate
    from src.app.models.insights_model import Insight


# --- CORRECTED ENUMS ---
class BillSource(str, PyEnum):
    PDF = "pdf"
    MANUAL = "manual"


class BillStatus(str, PyEnum):
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


# --- POPULATED BillBase ---
# This class contains all the fields that will be part of our API schemas.
class BillBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    billing_period_start: date = Field(nullable=False)
    billing_period_end: date = Field(nullable=False)
    kwh_total: float = Field(nullable=False)
    cost_total: float = Field(nullable=False)
    provider: str = Field(nullable=False)
    normalized_json: Dict[str, Any] = Field(sa_column=Column(JSONB), default={})

    # --- CORRECTED ENUM COLUMNS ---
    parse_status: BillStatus = Field(
        sa_column=Column(SAEnum(BillStatus), nullable=False),
        default=BillStatus.PROCESSING,
    )
    source_type: BillSource = Field(
        sa_column=Column(SAEnum(BillSource), nullable=False),
        default=BillSource.PDF,
    )

    file_uri: Optional[str] = Field(default=None)

    # --- CORRECTED parser_version and checksum ---
    parser_version: Optional[str] = Field(default=None)
    checksum: Optional[str] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )

class Bill(BillBase, table=True):
    __tablename__ = "bills"

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

    # RELATIONSHIPS
    user: "User" = Relationship(back_populates="bills")
    estimates: List["ApplianceEstimate"] = Relationship(back_populates="bill")
    insight: Optional["Insight"] = Relationship(back_populates="bill")

    def __repr__(self):
        return f"<Bill(id='{self.id}, user_id='{self.user_id}')>"
