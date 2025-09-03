# app/schemas/insight_schema.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum
from src.app.core.exceptions import ValidationError


# --- ENUMS for Consistency ---


class InsightTrend(str, Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


class InsightStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Nested Schemas for the Insight Report ---
class InsightCreate(BaseModel):
    bill_id: uuid.UUID
    user_id: uuid.UUID

class InsightKPIs(BaseModel):
    kwh_total: float = Field(..., ge=0)
    cost_total: float = Field(..., ge=0)
    kwh_change_percent: Optional[float] = None  # % change vs previous
    cost_change_percent: Optional[float] = None
    trend: InsightTrend

    @field_validator("kwh_change_percent", "cost_change_percent")
    def validate_percentage(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-100 <= v <= 1000):
            raise ValidationError("Percentage change must be between -100 and 1000")
        return v


class InsightApplianceBreakdown(BaseModel):
    appliance_name: str = Field(..., min_length=1, max_length=200)
    estimated_kwh: float = Field(..., ge=0)
    percentage_of_total: float = Field(..., ge=0, le=100)

    @field_validator("appliance_name")
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValidationError("appliance_name cannot be empty")
        return v


class InsightRecommendation(BaseModel):
    priority: int = Field(..., ge=1, le=3, description="1=high, 2=medium, 3=low")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)

    @field_validator("title", "description")
    def strip_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValidationError("Field cannot be empty or only spaces")
        return v


# --- The Main V1 Response Schema ---


class InsightResponee(BaseModel):
    """
    The response schema for a completed Insight Report.
    This is the data that will be stored in the 'structured_data' JSON field.
    """

    bill_id: uuid.UUID
    generated_at: datetime
    kpis: InsightKPIs
    consumption_breakdown: List[InsightApplianceBreakdown]
    recommendations: List[InsightRecommendation]

    @model_validator(mode="after")
    def validate_breakdown_total(self) -> "InsightResponee":
        total_percentage = sum(
            b.percentage_of_total for b in self.consumption_breakdown
        )
        if total_percentage > 100.5:  # allow a tiny rounding margin
            raise ValidationError(
                "Sum of appliance percentage_of_total cannot exceed 100"
            )
        return self


class InsightStatusResponse(BaseModel):
    """A simple schema to return the status of an insight generation task."""

    bill_id: uuid.UUID
    status: InsightStatus
