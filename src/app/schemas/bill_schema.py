import uuid
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from src.app.models.bill_model import BillSource, BillStatus
from src.app.core.exceptions import ValidationError
from src.app.schemas.appliance_schema import UserApplianceDetailedResponse


class BillBase(BaseModel):
    """Base bill schema"""

    billing_period_start: date = Field(..., description="Starting Bill period")
    billing_period_end: date = Field(..., description="Ending Bill period")
    kwh_total: float = Field(..., gt=0, description="Total kWh consumed")
    cost_total: float = Field(..., ge=0, description="Total cost in INR")
    provider: str = Field(..., min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_billing_period(self) -> "BillBase":
        if self.billing_period_end <= self.billing_period_start:
            raise ValidationError(
                "Billing period end must be after billing period start"
            )

        # Check if period is reasonable (not more than 3 months)
        days_diff = (self.billing_period_end - self.billing_period_start).days
        if days_diff > 90:
            raise ValidationError("Billing period cannot exceed 90 days")

        return self


# class BillUploadRequest(BaseModel):
#     """Schema for requesting a file upload URL."""

#     filename: str = Field(
#         ..., description="The name of the file being uploaded, e.g., 'july_bill.pdf'."
#     )
#     source_type: str = Field(
#         ..., description="The MIME type of the file, e.g., 'application/pdf or manual'."
#     )


# class BillConfirmRequest(BaseModel):
#     """Schema for confirming a file upload is complete."""


#     file_uri: str = Field(
#         ...,
#         description="The file URI that was returned from the initial /upload endpoint.",
#     )
class BillUploadRequest(BaseModel):
    """Schema for Step 1: Requesting a file upload URL."""

    filename: str = Field(
        ..., description="The name of the file being uploaded, e.g., 'july_bill.pdf'."
    )
    # Using 'content_type' is more accurate for the file's MIME type.
    content_type: str = Field(
        ..., description="The MIME type of the file, e.g., 'application/pdf'."
    )


class BillUploadResponse(BaseModel):
    """Schema for Step 2: The response from the server with the secure URL."""

    upload_url: str = Field(
        ..., description="The secure, one-time URL to PUT the file to."
    )
    file_uri: str = Field(
        ..., description="The final, permanent URI of the file in our storage."
    )


class BillConfirmRequest(BaseModel):
    """Schema for Step 3: Confirming a file upload is complete."""

    file_uri: str = Field(
        ..., description="The file URI returned from the /upload endpoint."
    )


class BillResponse(BillBase):
    """Response class for bill apis"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Bill ID")
    user_id: uuid.UUID = Field(..., description="User ID")
    source_type: BillSource = Field(
        ..., description="The MIME type of the file, e.g., 'application/pdf or manual'."
    )
    confidence_score: Optional[float] = Field(
        None, description="Parsing confidence score"
    )
    parse_status: BillStatus = Field(..., description="Bill parsing Status")
    created_at: datetime = Field(..., description="Registration timestamp")
    errors: Optional[List[str]] = Field(None, description="Parsing errors if any")


# ==========Normalized Schema==============
# --- Nested Schemas for the Golden Record ---
class NormalizedAccount(BaseModel):
    consumer_id: str
    meter_id: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None


class NormalizedPeriod(BaseModel):
    start: date
    end: date
    bill_date: Optional[date] = None
    due_date: Optional[date] = None


class NormalizedReadings(BaseModel):
    previous: Optional[float] = None
    current: Optional[float] = None


class NormalizedConsumption(BaseModel):
    readings: NormalizedReadings
    total_kwh: float


class NormalizedChargeItem(BaseModel):
    name: str
    amount: float


class NormalizedBillingSummary(BaseModel):
    net_current_demand: float
    subsidy: Optional[float] = 0.0
    arrears: Optional[float] = 0.0
    adjustments: Optional[float] = 0.0
    total_payable: float


class NormalizedTariffSlab(BaseModel):
    # e.g., "upto_kwh": 100, "rate": 3.50
    description: str  # e.g., "0-100 kWh"
    rate: float


class NormalizedTariff(BaseModel):
    plan_code: Optional[str] = None
    slabs: List[NormalizedTariffSlab]


# --- The Main Golden Record Schema ---
class NormalizedBillSchema(BaseModel):
    """
    The definitive, structured format for a parsed electricity bill.
    This is what is stored in the `normalized_json` field.
    """

    version: str = "1.1"
    discom: str
    account: NormalizedAccount
    period: NormalizedPeriod
    technical_details: Optional[Dict[str, Any]] = None
    consumption: NormalizedConsumption
    charges_breakdown: List[NormalizedChargeItem]
    billing_summary: NormalizedBillingSummary
    totals: Dict[str, Any]  # e.g., {"cost": 2210.0, "currency": "INR"}
    tariff: Optional[NormalizedTariff] = None


class BillDetailedResponse(BillResponse):
    """Detailed response for bill"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    details: Optional[NormalizedBillSchema] = Field(
        None,
        alias="normalized_json",
        validation_alias="normalized_json",  # 👈 ensures it maps correctly
        description="Structured normalized bill data",
    )
    user_appliances: List[UserApplianceDetailedResponse] = Field(
        default_factory=list, description="List of bills for the user"
    )


class BillListResponse(BaseModel):
    """Response for paginated user list."""

    items: List[BillResponse] = Field(..., description="List of bills")
    total: int = Field(..., ge=0, description="Total number of bills")
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


class BillUserListResponse(BaseModel):
    """Response for paginated user list."""

    model_config = ConfigDict(from_attributes=True)

    items: List[BillDetailedResponse] = Field(..., description="List of bills")
    total: int = Field(..., ge=0, description="Total number of bills")
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


class BillSearchParams(BaseModel):
    """Parameters for searching users."""

    search: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Search in provider, source_type",
    )
    user_id: Optional[uuid.UUID] = Field(None, description="Filter by user_id")
    created_after: Optional[date] = Field(
        None, description="Filter users created after this date"
    )
    created_before: Optional[date] = Field(
        None, description="Filter users created before this date"
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "BillSearchParams":
        """Ensure date range is valid."""
        if self.created_after and self.created_before:
            if self.created_after > self.created_before:
                raise ValidationError("created_after must be before created_before")
        return self


__all__ = [
    # BillsSchemas
    "BillBase",
    "BillUploadRequest",
    "BillConfirmRequest",
    # NormalizedBillSchemas
    "NormalizedAccount",
    "NormalizedPeriod",
    "NormalizedReadings",
    "NormalizedConsumption",
    "NormalizedChargeItem",
    "NormalizedBillingSummary",
    "NormalizedTariffSlab",
    "NormalizedTariff",
    "NormalizedBillSchema"
    # Responses
    "BillResponse",
    "BillDetailedResponse",
    "BillListResponse",
    "BillSearchParams",
]
