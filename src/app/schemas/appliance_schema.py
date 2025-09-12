import uuid
import re
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, List
from datetime import datetime, date
from src.app.core.exceptions import ValidationError


class UserApplianceBase(BaseModel):
    """Base schema for Appliances"""

    appliance_catalog_id: str = Field(..., description="Appliance_catalog ID")
    custom_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User-defined name for the appliance",
    )
    count : int = Field(
        ...,
        ge=0,
        description="Number of appliances user owns"
    )
    custom_wattage: int = Field(
        ...,
        gt=0,
        le=50000,
        description="User-specified wattage (overrides catalog value)",
    )
    hours_per_day: float = Field(
        ...,
        ge=0,
        le=24,
        description="Average hours of operation per day",
    )
    days_per_week: int = Field(
        ...,
        ge=0,
        le=7,
        description="Days per week the appliance is used",
    )
    brand: Optional[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Appliance manufacturer brand",
    )
    model: Optional[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Appliance model number",
    )
    star_rating: Optional[int] = Field(
        ...,
        ge=1,
        le=5,
        description="Star rating of your appliance from 1 to 5",
    )
    purchase_year: Optional[int] = Field(
        ..., description="Year user purcahsed this applaince"
    )
    notes: Optional[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Add some additional notes for the applaince",
    )

    @field_validator("custom_name", "brand", "model")
    def strip_and_validate_strings(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValidationError("This field cannot be empty or just spaces")
        return v

    @field_validator("purchase_year")
    def validate_purchase_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v < 1990 or v > current_year:
            raise ValidationError(
                f"purchase_year must be between 1990 and {current_year}"
            )
        return v

    @field_validator("star_rating")
    def validate_star_rating(cls, v: int) -> int:
        if v not in [1, 2, 3, 4, 5]:
            raise ValidationError("star_rating must be an integer between 1 and 5")
        return v

    @field_validator("custom_wattage")
    def validate_custom_wattage(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v % 10 != 0:
            raise ValidationError("custom_wattage should be in multiples of 10")
        return v

    # -------------------------
    # MODEL VALIDATORS
    # -------------------------

    @model_validator(mode="after")
    def validate_wattage(self) -> "UserApplianceBase":
        if not self.appliance_catalog_id and not self.custom_wattage:
            raise ValidationError(
                "Either appliance_catalog_id or custom_wattage must be provided"
            )
        return self

    @model_validator(mode="after")
    def validate_usage(self) -> "UserApplianceBase":
        if self.hours_per_day == 0 and self.days_per_week > 0:
            raise ValidationError("If hours_per_day is 0, days_per_week must also be 0")
        if self.hours_per_day > 0 and self.days_per_week == 0:
            raise ValidationError("If days_per_week is 0, hours_per_day must also be 0")
        return self


class UserApplianceCreate(UserApplianceBase):
    """Schema for creating appliance"""

    @model_validator(mode="after")
    def check_wattage_source(self) -> "UserApplianceCreate":
        # When creating, user must either pick a catalog item or provide a custom wattage.
        if not self.appliance_catalog_id and not self.custom_wattage:
            raise ValidationError(
                "Either an appliance type from the catalog or a custom wattage must be provided."
            )
        return self


class UserApplianceUpdate(BaseModel):
    """Base schema for Appliances"""

    appliance_catalog_id: Optional[str] = Field(None, description="catalog ID")
    custom_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="User-defined name for the appliance",
    )
    count : Optional[int] = Field(
        None,
        ge=0,
        description="Number of appliances user owns"
    )
    custom_wattage: Optional[int] = Field(
        None,
        gt=0,
        le=50000,
        description="User-specified wattage (overrides catalog value)",
    )
    hours_per_day: Optional[float] = Field(
        None,
        ge=0,
        le=24,
        description="Average hours of operation per day",
    )
    days_per_week: Optional[int] = Field(
        None,
        ge=0,
        le=7,
        description="Days per week the appliance is used",
    )
    brand: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Appliance manufacturer brand",
    )
    model: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Appliance model number",
    )
    star_rating: Optional[int] = Field(
        ...,
        ge=1,
        le=5,
        description="Star rating of your appliance from 1 to 5",
    )
    purchase_year: Optional[int] = Field(
        None, description="Year user purcahsed this applaince"
    )
    notes: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Add some additional notes for the applaince",
    )

    @field_validator("custom_name", "brand", "model", "notes")
    def strip_and_validate_strings(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValidationError("This field cannot be empty or just spaces")
        return v

    @field_validator("purchase_year")
    def validate_purchase_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v < 1990 or v > current_year:
            raise ValidationError(
                f"purchase_year must be between 1990 and {current_year}"
            )
        return v

    @field_validator("star_rating")
    def validate_star_rating(cls, v: int) -> int:
        if v not in [1, 2, 3, 4, 5]:
            raise ValidationError("star_rating must be an integer between 1 and 5")
        return v

    @field_validator("custom_wattage")
    def validate_custom_wattage(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v % 10 != 0:
            raise ValidationError("custom_wattage should be in multiples of 10")
        return v

    # -------------------------
    # MODEL VALIDATORS
    # -------------------------
    @model_validator(mode="before")
    def at_least_one_field(cls, values):
        if not any(values.values()):
            raise ValidationError("At least one field must be provided for an update.")
        return values

    @model_validator(mode="after")
    def validate_wattage(self) -> "UserApplianceBase":
        if not self.appliance_catalog_id and not self.custom_wattage:
            raise ValidationError(
                "Either appliance_catalog_id or custom_wattage must be provided"
            )
        return self

    @model_validator(mode="after")
    def validate_usage(self) -> "UserApplianceUpdate":
        if self.hours_per_day == 0 and self.days_per_week > 0:
            raise ValidationError("If hours_per_day is 0, days_per_week must also be 0")
        if self.hours_per_day > 0 and self.days_per_week == 0:
            raise ValidationError("If days_per_week is 0, hours_per_day must also be 0")
        return self


# ===========Response Schemas============
class UserApplianceResponse(UserApplianceBase):
    """Response schema for Appliance"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Appliance ID")
    user_id: uuid.UUID = Field(..., description="User ID")
    bill_id: uuid.UUID = Field(..., description="Bill ID")
    appliance_catalog_id: str = Field(..., description="Catalog ID")
    created_at: datetime = Field(..., description="Registration timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# ===========ESTIMATE SCHEMAS=============
class ApplianceEstimateBase(BaseModel):
    """Base schema for appliance estimates"""

    estimated_kwh: float = Field(..., ge=0)
    estimated_cost: float = Field(..., ge=0)


class ApplianceEstimateResponse(ApplianceEstimateBase):
    """Schema for creating appliance estimates"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Appliance estimate ID")
    bill_id: uuid.UUID = Field(..., description="Bill ID")
    user_appliance_id: uuid.UUID = Field(..., description="user_appliance ID")


class UserApplianceDetailedResponse(UserApplianceResponse):
    """Detailed response for an appliance"""

    # One appliance can have multiple estimates
    estimates: List[ApplianceEstimateResponse] = Field(
        default_factory=list,
        description="List of usage estimates for this appliance"
    )



# ======== List and Search Schemas =========
class UserApplianceListResponse(BaseModel):
    """Response for paginated user list."""

    items: List[UserApplianceDetailedResponse] = Field(
        ..., description="List of appliances"
    )
    total: int = Field(..., ge=0, description="Total number of appliances")
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


class UserApplianceSearchParams(BaseModel):
    """Parameters for searching users."""

    search: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Search in custom_name, brand",
    )
    user_id: Optional[uuid.UUID] = Field(None, description="Filter by user_id")
    bill_id: Optional[uuid.UUID] = Field(None, description="Filter by bill_id")
    appliance_catalog_id: Optional[uuid.UUID] = Field(
        None, description="Filter by appliance_catalog_id"
    )

    created_after: Optional[date] = Field(
        None, description="Filter users created after this date"
    )
    created_before: Optional[date] = Field(
        None, description="Filter users created before this date"
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "UserApplianceSearchParams":
        """Ensure date range is valid."""
        if self.created_after and self.created_before:
            if self.created_after > self.created_before:
                raise ValidationError("created_after must be before created_before")
        return self


# ===========Catalog Schemas============
class ApplianceCatalogCreate(BaseModel):
    """Create catalog schema"""

    category_id: str = Field(..., description="catalog_id")
    label: str = Field(..., min_length=1, max_length=500, description="Label name")
    icon_emoji: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Emoji or short icon text to represent a label",
    )
    typical_wattage: int = Field(
        ...,
        gt=0,
        le=50000,
        description="Average wattage of the appliance in watts",
    )

    # Field validators
    @field_validator("icon_emoji")
    def strip_and_validate_strings(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValidationError("This field cannot be empty or only spaces")
        return v

    @field_validator("icon_emoji")
    def validate_emoji(cls, v: str) -> str:
        # very loose check: one emoji or short text allowed
        if len(v) > 2 and not re.match(r"^[\w\s-]+$", v):
            raise ValidationError("icon_emoji must be a single emoji or short text")
        return v


class ApplianceCatalogUpdate(BaseModel):
    """Update catalog schema"""

    catalog_id: str = Field(..., description="catalog_id")
    label: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Label name"
    )
    icon_emoji: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Emoji or short icon text to represent a label",
    )
    typical_wattage: Optional[int] = Field(
        None,
        gt=0,
        le=50000,
        description="Average wattage of the appliance in watts",
    )

    # Field validators
    @field_validator("label", "icon_emoji")
    def strip_and_validate_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValidationError("This field cannot be empty or only spaces")
        return v

    @field_validator("icon_emoji")
    def validate_emoji(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) > 2 and not re.match(r"^[\w\s-]+$", v):
            raise ValidationError("icon_emoji must be a single emoji or short text")
        return v

    # Model validator
    @model_validator(mode="before")
    def at_least_one_field(cls, values):
        if not any(values.values()):
            raise ValidationError("At least one field must be provided for an update")
        return values


class ApplianceCatalogResponse(BaseModel):
    """Response schema for catalog"""

    model_config = ConfigDict(from_attributes=True)

    category_id: str = Field(..., description="Catalog ID")
    label: str = Field(..., min_length=1, max_length=500, description="Label name")
    icon_emoji: str = Field(
        ..., min_length=1, max_length=50, description="emoji to represent a label"
    )
    typical_wattage: int = Field(..., description="an average wattage")


__all__ = [
    "UserApplianceBase",
    "UserApplianceCreate",
    "UserApplianceUpdate",
    "UserApplianceResponse",
    "UserApplianceListResponse",
    "UserApplianceSearchParams",
    "ApplianceEstimateBase",
    "ApplianceEstimateResponse",
    "UserApplianceDetailedResponse",
]
