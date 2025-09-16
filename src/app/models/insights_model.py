# app/models/insight_model.py

import uuid
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING, Optional
from enum import Enum as PyEnum

from sqlalchemy import func, Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from src.app.models.user_model import User
    from src.app.models.bill_model import Bill


class InsightStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class InsightBase(SQLModel):
    status: InsightStatus = Field(
        sa_column=Column(SAEnum(InsightStatus), nullable=False),
        default=InsightStatus.PENDING,
    )
    # This field stores the entire, rich JSON payload for the Smart Insights page.
    structured_data: Dict[str, Any] = Field(sa_column=Column(JSONB), default=None)


class Insight(InsightBase, table=True):
    __tablename__ = "insights"

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
    # A bill should only ever have one insight record.
    bill_id: uuid.UUID = Field(
        foreign_key="bills.id", index=True, unique=True, nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)

    generated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )

    # Relationships
    bill: Optional["Bill"] = Relationship(back_populates="insight")
    user: Optional["User"] = Relationship(back_populates="insights")

    def __repr__(self):
        return f"<Insight(id='{self.id}, bill_id='{self.bill_id}')>"
