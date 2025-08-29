# # ==========4.1 SCHEMA==========
# # app/schemas/appliance_schema.py
# import uuid
# from datetime import datetime
# from typing import Optional, List
# from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


# class ApplianceCatalogBase(BaseModel):
#     """Base schema for appliance catalog"""
#     category_id: str = Field(..., min_length=1, max_length=50)
#     label: str = Field(..., min_length=1, max_length=100)
#     icon_emoji: str = Field(..., min_length=1, max_length=10)
#     typical_wattage: int = Field(..., gt=0, le=10000)


# class ApplianceCatalogResponse(ApplianceCatalogBase):
#     """Response schema for appliance catalog"""
    
#     # Additional computed fields
#     typical_monthly_kwh: float = Field(default=0.0)
#     typical_monthly_cost: float = Field(default=0.0)
    
#     @model_validator(mode='after')
#     def compute_typical_usage(self) -> 'ApplianceCatalogResponse':
#         # Assuming 4 hours/day average usage
#         self.typical_monthly_kwh = round((self.typical_wattage * 4 * 30) / 1000, 2)
#         # Assuming ₹8 per kWh average
#         self.typical_monthly_cost = round(self.typical_monthly_kwh * 8, 2)
#         return self
    
#     model_config = ConfigDict(from_attributes=True)


# class UserApplianceBase(BaseModel):
#     """Base schema for user appliances"""
#     custom_name: str = Field(..., min_length=1, max_length=100)
#     appliance_catalog_id: Optional[str] = None
#     count: int = Field(default=1, ge=1, le=100)
#     custom_wattage: Optional[int] = Field(None, gt=0, le=10000)
#     hours_per_day: float = Field(..., ge=0, le=24)
#     days_per_week: int = Field(..., ge=0, le=7)
    
#     # Optional detailed info
#     brand: Optional[str] = Field(None, max_length=50)
#     model: Optional[str] = Field(None, max_length=100)
#     star_rating: Optional[str] = Field(None, pattern="^[1-5](\\.5)?$")
#     purchase_year: Optional[int] = Field(None, ge=1990, le=2030)
#     notes: Optional[str] = Field(None, max_length=500)
    
#     @field_validator('custom_name')
#     @classmethod
#     def validate_custom_name(cls, v: str) -> str:
#         return v.strip()
    
#     @model_validator(mode='after')
#     def validate_wattage(self) -> 'UserApplianceBase':
#         if not self.appliance_catalog_id and not self.custom_wattage:
#             raise ValueError('Either appliance_catalog_id or custom_wattage must be provided')
#         return self


# class UserApplianceCreate(UserApplianceBase):
#     """Schema for creating user appliances"""
    
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "custom_name": "Living Room AC",
#                 "appliance_catalog_id": "ac_split_1_5ton",
#                 "count": 1,
#                 "hours_per_day": 8,
#                 "days_per_week": 7,
#                 "brand": "LG",
#                 "model": "MS-Q18YNZA",
#                 "star_rating": "5",
#                 "purchase_year": 2023
#             }
#         }
#     )


# class UserApplianceUpdate(BaseModel):
#     """Schema for updating user appliances"""
#     custom_name: Optional[str] = Field(None, min_length=1, max_length=100)
#     count: Optional[int] = Field(None, ge=1, le=100)
#     custom_wattage: Optional[int] = Field(None, gt=0, le=10000)
#     hours_per_day: Optional[float] = Field(None, ge=0, le=24)
#     days_per_week: Optional[int] = Field(None, ge=0, le=7)
#     brand: Optional[str] = Field(None, max_length=50)
#     model: Optional[str] = Field(None, max_length=100)
#     star_rating: Optional[str] = Field(None, pattern="^[1-5](\\.5)?$")
#     purchase_year: Optional[int] = Field(None, ge=1990, le=2030)
#     notes: Optional[str] = Field(None, max_length=500)


# class UserApplianceResponse(UserApplianceBase):
#     """Response schema for user appliances"""
#     id: uuid.UUID
#     user_id: uuid.UUID
#     created_at: datetime
#     updated_at: datetime
    
#     # Computed fields
#     estimated_monthly_kwh: float = Field(default=0.0)
#     estimated_monthly_cost: float = Field(default=0.0)
#     effective_wattage: int = Field(default=0)
    
#     @model_validator(mode='after')
#     def compute_estimates(self) -> 'UserApplianceResponse':
#         # Determine effective wattage
#         self.effective_wattage = self.custom_wattage or 0  # Should be fetched from catalog
        
#         # Calculate monthly estimates
#         days_per_month = (self.days_per_week / 7) * 30
#         total_hours = self.hours_per_day * days_per_month * self.count
#         self.estimated_monthly_kwh = round((self.effective_wattage * total_hours) / 1000, 2)
#         self.estimated_monthly_cost = round(self.estimated_monthly_kwh * 8, 2)  # ₹8/kWh avg
        
#         return self
    
#     model_config = ConfigDict(from_attributes=True)


# class ApplianceEstimateBase(BaseModel):
#     """Base schema for appliance estimates"""
#     estimated_kwh: float = Field(..., ge=0)
#     estimated_cost: float = Field(..., ge=0)


# class ApplianceEstimateCreate(ApplianceEstimateBase):
#     """Schema for creating appliance estimates"""
#     bill_id: uuid.UUID
#     user_appliance_id: uuid.UUID


# class ApplianceEstimateResponse(ApplianceEstimateBase):
#     """Response schema for appliance estimates"""
#     id: uuid.UUID
#     bill_id: uuid.UUID
#     user_appliance_id: uuid.UUID
    
#     # Related appliance info (joined from user_appliance)
#     appliance_name: Optional[str] = None
#     appliance_category: Optional[str] = None
#     percentage_of_bill: float = Field(default=0.0)
    
#     model_config = ConfigDict(from_attributes=True)


# class ApplianceEstimateDetailResponse(ApplianceEstimateResponse):
#     """Detailed response for appliance estimates"""
#     user_appliance: Optional[UserApplianceResponse] = None
    
#     # Comparison data
#     vs_last_month: Optional[float] = None
#     vs_similar_appliances: Optional[float] = None
#     efficiency_rating: Optional[str] = None
    
#     model_config = ConfigDict(from_attributes=True)


# class UserApplianceListResponse(BaseModel):
#     """Response for user appliance list"""
#     total: int
#     appliances: List[UserApplianceResponse]
    
#     # Summary statistics
#     total_estimated_kwh: float = Field(default=0.0)
#     total_estimated_cost: float = Field(default=0.0)
#     top_consumers: List[Dict[str, Any]] = []


# class ApplianceBulkCreateRequest(BaseModel):
#     """Request schema for bulk creating appliances"""
#     appliances: List[UserApplianceCreate]
    
#     @field_validator('appliances')
#     @classmethod
#     def validate_appliances_count(cls, v: List) -> List:
#         if len(v) > 50:
#             raise ValueError('Cannot create more than 50 appliances at once')
#         return v


# class ApplianceCategoryGroup(BaseModel):
#     """Schema for grouped appliance categories"""
#     category: str
#     icon: str
#     appliances: List[ApplianceCatalogResponse]
#     typical_home_count: int = Field(default=0)
    
    
    
    
# ===========4.1 THINKING SCHEMA===========
# # app/schemas/appliance_schema.py

# import uuid
# from datetime import datetime
# from typing import Optional, List, Dict, Any
# from pydantic import BaseModel, Field, field_validator, ConfigDict
# from src.app.schemas.base_schema import PaginatedResponse


# class ApplianceCatalogBase(BaseModel):
#     """Base appliance catalog schema"""
#     category_id: str = Field(..., min_length=1, max_length=50, description="Category ID")
#     label: str = Field(..., min_length=1, max_length=100, description="Display label")
#     icon_emoji: str = Field(..., description="Icon emoji")
#     typical_wattage: int = Field(..., gt=0, description="Typical wattage")


# class ApplianceCatalogResponse(ApplianceCatalogBase):
#     """Appliance catalog response"""
#     # Additional computed fields
#     typical_monthly_kwh: Optional[float] = Field(None, description="Typical monthly consumption")
#     efficiency_tips: Optional[List[str]] = Field(None, description="Efficiency tips for this category")
    
#     model_config = ConfigDict(from_attributes=True)


# class UserApplianceBase(BaseModel):
#     """Base user appliance schema"""
#     appliance_catalog_id: Optional[str] = Field(None, description="Reference to catalog")
#     custom_name: str = Field(..., min_length=1, max_length=100, description="Custom appliance name")
#     count: int = Field(default=1, ge=1, le=100, description="Number of units")
#     custom_wattage: Optional[int] = Field(None, gt=0, le=10000, description="Custom wattage if different")
#     hours_per_day: float = Field(..., ge=0, le=24, description="Usage hours per day")
#     days_per_week: int = Field(..., ge=0, le=7, description="Usage days per week")
#     brand: Optional[str] = Field(None, max_length=50, description="Brand name")
#     model: Optional[str] = Field(None, max_length=50, description="Model number")
#     star_rating: Optional[str] = Field(None, pattern="^[1-5](\\.5)?$", description="Energy star rating")
#     purchase_year: Optional[int] = Field(None, ge=1990, le=2030, description="Purchase year")
#     notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
#     @field_validator('hours_per_day')
#     @classmethod
#     def validate_hours(cls, v: float) -> float:
#         """Validate hours per day"""
#         if v < 0 or v > 24:
#             raise ValueError('Hours per day must be between 0 and 24')
#         return round(v, 1)
    
#     @field_validator('days_per_week')
#     @classmethod
#     def validate_days(cls, v: int) -> int:
#         """Validate days per week"""
#         if v < 0 or v > 7:
#             raise ValueError('Days per week must be between 0 and 7')
#         return v
    
#     @field_validator('star_rating')
#     @classmethod
#     def validate_star_rating(cls, v: Optional[str]) -> Optional[str]:
#         """Validate star rating"""
#         if v is None:
#             return v
#         valid_ratings = ['1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']
#         if v not in valid_ratings:
#             raise ValueError(f'Star rating must be one of {valid_ratings}')
#         return v


# class UserApplianceCreate(UserApplianceBase):
#     """Schema for creating user appliance"""
#     pass


# class UserApplianceUpdate(BaseModel):
#     """Schema for updating user appliance"""
#     custom_name: Optional[str] = Field(None, min_length=1, max_length=100)
#     count: Optional[int] = Field(None, ge=1, le=100)
#     custom_wattage: Optional[int] = Field(None, gt=0, le=10000)
#     hours_per_day: Optional[float] = Field(None, ge=0, le=24)
#     days_per_week: Optional[int] = Field(None, ge=0, le=7)
#     brand: Optional[str] = Field(None, max_length=50)
#     model: Optional[str] = Field(None, max_length=50)
#     star_rating: Optional[str] = Field(None, pattern="^[1-5](\\.5)?$")
#     purchase_year: Optional[int] = Field(None, ge=1990, le=2030)
#     notes: Optional[str] = Field(None, max_length=500)
    
#     model_config = ConfigDict(validate_assignment=True)


# class UserApplianceResponse(UserApplianceBase):
#     """User appliance response"""
#     id: uuid.UUID
#     user_id: uuid.UUID
#     created_at: datetime
#     updated_at: datetime
    
#     # Calculated fields
#     effective_wattage: int = Field(..., description="Effective wattage (custom or from catalog)")
#     estimated_daily_kwh: float = Field(..., description="Estimated daily consumption")
#     estimated_monthly_kwh: float = Field(..., description="Estimated monthly consumption")
#     estimated_monthly_cost: Optional[float] = Field(None, description="Estimated monthly cost")
    
#     # Related catalog info
#     catalog_info: Optional[ApplianceCatalogResponse] = Field(None, description="Catalog information")
    
#     # Usage analytics
#     usage_pattern: Optional[str] = Field(None, description="Usage pattern: heavy, moderate, light")
#     efficiency_score: Optional[float] = Field(None, description="Efficiency score 0-100")
    
#     model_config = ConfigDict(from_attributes=True)


# class UserApplianceSummaryResponse(BaseModel):
#     """Summary response for appliance listings"""
#     id: uuid.UUID
#     custom_name: str
#     count: int
#     hours_per_day: float
#     days_per_week: int
#     estimated_monthly_kwh: float
#     created_at: datetime
    
#     model_config = ConfigDict(from_attributes=True)


# class UserApplianceListResponse(PaginatedResponse):
#     """Paginated user appliance list"""
#     items: List[UserApplianceSummaryResponse]
    
#     # Aggregated stats
#     total_appliances: int
#     total_estimated_monthly_kwh: float
#     total_estimated_monthly_cost: Optional[float] = None
    
#     # Category breakdown
#     category_breakdown: Optional[Dict[str, int]] = Field(None, description="Appliances by category")


# class ApplianceEstimateBase(BaseModel):
#     """Base appliance estimate schema"""
#     estimated_kwh: float = Field(..., ge=0, description="Estimated kWh consumption")
#     estimated_cost: float = Field(..., ge=0, description="Estimated cost in INR")
    
#     @field_validator('estimated_kwh', 'estimated_cost')
#     @classmethod
#     def round_values(cls, v: float) -> float:
#         """Round to 2 decimal places"""
#         return round(v, 2)


# class ApplianceEstimateCreate(ApplianceEstimateBase):
#     """Schema for creating appliance estimate"""
#     bill_id: uuid.UUID = Field(..., description="Associated bill ID")
#     user_appliance_id: uuid.UUID = Field(..., description="Associated user appliance ID")


# class ApplianceEstimateResponse(ApplianceEstimateBase):
#     """Appliance estimate response"""
#     id: uuid.UUID
#     bill_id: uuid.UUID
#     user_appliance_id: uuid.UUID
    
#     # Related appliance info
#     appliance: UserApplianceSummaryResponse = Field(..., description="Appliance information")
    
#     # Analysis
#     percentage_of_total: float = Field(..., description="Percentage of total bill")
#     cost_per_day: float = Field(..., description="Average cost per day")
#     comparison_to_average: Optional[str] = Field(None, description="Comparison to average usage")
    
#     model_config = ConfigDict(from_attributes=True)


# class ApplianceEstimateBulkCreate(BaseModel):
#     """Schema for bulk creating estimates for a bill"""
#     bill_id: uuid.UUID
#     estimates: List[Dict[str, Any]] = Field(..., description="List of estimates to create")


# class ApplianceUsageAnalyticsResponse(BaseModel):
#     """Analytics for appliance usage"""
#     appliance_id: uuid.UUID
#     appliance_name: str
    
#     # Time series data
#     daily_usage: List[Dict[str, Any]] = Field(..., description="Daily usage pattern")
#     monthly_trend: List[Dict[str, Any]] = Field(..., description="Monthly usage trend")
    
#     # Comparisons
#     peer_comparison: Dict[str, Any] = Field(..., description="Comparison with similar households")
#     efficiency_analysis: Dict[str, Any] = Field(..., description="Efficiency analysis")
    
#     # Recommendations
#     optimization_tips: List[str] = Field(..., description="Optimization recommendations")
#     upgrade_suggestions: Optional[List[Dict[str, Any]]] = Field(None, description="Upgrade suggestions")
    
#     # Cost analysis
#     lifetime_cost: float = Field(..., description="Estimated lifetime cost")
#     potential_savings: float = Field(..., description="Potential savings with optimization")


# class ApplianceBulkImportRequest(BaseModel):
#     """Request for bulk importing appliances"""
#     appliances: List[UserApplianceCreate] = Field(..., min_items=1, max_items=50)
    
#     @field_validator('appliances')
#     @classmethod
#     def validate_unique_names(cls, v: List[UserApplianceCreate]) -> List[UserApplianceCreate]:
#         """Ensure unique appliance names"""
#         names = [a.custom_name for a in v]
#         if len(names) != len(set(names)):
#             raise ValueError('Appliance names must be unique')
#         return v


# class ApplianceBulkImportResponse(BaseModel):
#     """Response for bulk import"""
#     success_count: int
#     failed_count: int
#     created_appliances: List[UserApplianceResponse]
#     errors: Optional[List[Dict[str, Any]]] = None






# app/schemas/appliance_schemas.py
"""
Appliance Management Schemas for GreenSpark Energy Management System
Production-ready Pydantic schemas with comprehensive validation and features
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from pydantic import (
    BaseModel, 
    Field, 
    validator, 
    root_validator,
    constr,
    conint,
    confloat,
    HttpUrl,
    EmailStr
)


# ==================== ENUMS ====================

class ApplianceStatus(str, Enum):
    """Appliance operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    BROKEN = "broken"
    STORED = "stored"
    DISPOSED = "disposed"


class EnergyEfficiencyRating(str, Enum):
    """Energy Star and EU energy efficiency ratings"""
    A_PLUS_PLUS_PLUS = "A+++"
    A_PLUS_PLUS = "A++"
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    NOT_RATED = "not_rated"


class ApplianceLocation(str, Enum):
    """Common household locations for appliances"""
    KITCHEN = "kitchen"
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    BATHROOM = "bathroom"
    GARAGE = "garage"
    BASEMENT = "basement"
    ATTIC = "attic"
    OFFICE = "office"
    LAUNDRY_ROOM = "laundry_room"
    OUTDOOR = "outdoor"
    OTHER = "other"


class UsagePattern(str, Enum):
    """Appliance usage patterns"""
    CONTINUOUS = "continuous"  # 24/7 operation
    DAILY = "daily"  # Used every day
    WEEKLY = "weekly"  # Used few times a week
    OCCASIONAL = "occasional"  # Rarely used
    SEASONAL = "seasonal"  # Summer/Winter only
    SCHEDULED = "scheduled"  # Specific time patterns


class SmartCapability(str, Enum):
    """Smart home integration capabilities"""
    NONE = "none"
    WIFI = "wifi"
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    BLUETOOTH = "bluetooth"
    MATTER = "matter"
    HOMEKIT = "homekit"
    ALEXA = "alexa"
    GOOGLE_HOME = "google_home"


class MaintenanceType(str, Enum):
    """Types of maintenance activities"""
    CLEANING = "cleaning"
    FILTER_REPLACEMENT = "filter_replacement"
    INSPECTION = "inspection"
    REPAIR = "repair"
    CALIBRATION = "calibration"
    SOFTWARE_UPDATE = "software_update"
    OTHER = "other"


# ==================== BASE SCHEMAS ====================

class ApplianceBaseSchema(BaseModel):
    """Base schema with common appliance fields"""
    
    custom_name: constr(min_length=1, max_length=100) = Field(
        ...,
        description="User-defined name for the appliance",
        example="Kitchen Refrigerator"
    )
    appliance_catalog_id: Optional[str] = Field(
        None,
        description="Reference to appliance catalog for predefined types",
        example="refrigerator_standard"
    )
    brand: Optional[constr(max_length=50)] = Field(
        None,
        description="Appliance manufacturer brand",
        example="Samsung"
    )
    model: Optional[constr(max_length=100)] = Field(
        None,
        description="Appliance model number",
        example="RF28R7351SR"
    )
    serial_number: Optional[constr(max_length=100)] = Field(
        None,
        description="Unique serial number for warranty and service",
        regex="^[A-Z0-9-]+$"
    )
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
            UUID: lambda v: str(v)
        }


class UsageDetailsSchema(BaseModel):
    """Schema for appliance usage patterns and details"""
    
    hours_per_day: confloat(ge=0, le=24) = Field(
        ...,
        description="Average hours of operation per day",
        example=8.5
    )
    days_per_week: conint(ge=0, le=7) = Field(
        ...,
        description="Days per week the appliance is used",
        example=7
    )
    usage_pattern: UsagePattern = Field(
        UsagePattern.DAILY,
        description="General usage pattern"
    )
    seasonal_months: Optional[List[conint(ge=1, le=12)]] = Field(
        None,
        description="Months when appliance is actively used (1=Jan, 12=Dec)",
        example=[6, 7, 8, 9]
    )
    peak_hours: Optional[List[conint(ge=0, le=23)]] = Field(
        None,
        description="Hours of day when appliance typically runs (24-hour format)",
        example=[18, 19, 20]
    )
    
    @validator('seasonal_months')
    def validate_seasonal_months(cls, v):
        if v and len(v) > 12:
            raise ValueError("Cannot have more than 12 months")
        if v:
            return sorted(list(set(v)))  # Remove duplicates and sort
        return v


class PowerSpecificationSchema(BaseModel):
    """Schema for appliance power and energy specifications"""
    
    custom_wattage: Optional[conint(gt=0, le=50000)] = Field(
        None,
        description="User-specified wattage (overrides catalog value)",
        example=1500
    )
    standby_wattage: Optional[conint(ge=0, le=1000)] = Field(
        None,
        description="Power consumption in standby mode",
        example=5
    )
    voltage: Optional[conint(ge=100, le=480)] = Field(
        None,
        description="Operating voltage",
        example=120
    )
    amperage: Optional[confloat(gt=0, le=100)] = Field(
        None,
        description="Current draw in amperes",
        example=12.5
    )
    energy_efficiency_rating: Optional[EnergyEfficiencyRating] = Field(
        None,
        description="Official energy efficiency rating"
    )
    annual_kwh_estimate: Optional[confloat(gt=0)] = Field(
        None,
        description="Manufacturer's estimated annual consumption in kWh",
        example=450.0
    )


# ==================== APPLIANCE CATALOG SCHEMAS ====================

class ApplianceCatalogResponse(BaseModel):
    """Response schema for appliance catalog items"""
    
    category_id: str = Field(..., description="Unique identifier for appliance category")
    label: str = Field(..., description="Display name for the appliance type")
    icon_emoji: str = Field(..., description="Emoji icon for UI display")
    typical_wattage: int = Field(..., description="Average power consumption in watts")
    category_group: Optional[str] = Field(None, description="Higher-level grouping")
    description: Optional[str] = Field(None, description="Detailed description")
    energy_saving_tips: Optional[List[str]] = Field(None, description="Tips for reducing consumption")
    typical_lifespan_years: Optional[int] = Field(None, description="Expected appliance lifespan")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "category_id": "refrigerator_standard",
                "label": "Refrigerator (Standard)",
                "icon_emoji": "🧊",
                "typical_wattage": 150,
                "category_group": "Kitchen Appliances",
                "description": "Standard household refrigerator",
                "energy_saving_tips": [
                    "Keep temperature between 37-40°F",
                    "Clean coils regularly",
                    "Check door seals"
                ],
                "typical_lifespan_years": 15
            }
        }


# ==================== USER APPLIANCE SCHEMAS ====================

class UserApplianceCreate(ApplianceBaseSchema, UsageDetailsSchema, PowerSpecificationSchema):
    """Schema for creating a new user appliance"""
    
    count: conint(ge=1, le=100) = Field(
        1,
        description="Number of identical appliances",
        example=1
    )
    location: Optional[ApplianceLocation] = Field(
        None,
        description="Location of the appliance in the home"
    )
    custom_location: Optional[constr(max_length=50)] = Field(
        None,
        description="Custom location if 'other' is selected"
    )
    purchase_date: Optional[date] = Field(
        None,
        description="Date of purchase for warranty tracking"
    )
    purchase_price: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Purchase price for depreciation tracking"
    )
    warranty_end_date: Optional[date] = Field(
        None,
        description="Warranty expiration date"
    )
    installation_date: Optional[date] = Field(
        None,
        description="Date appliance was installed/first used"
    )
    notes: Optional[constr(max_length=500)] = Field(
        None,
        description="Additional notes or comments"
    )
    tags: Optional[List[constr(max_length=30)]] = Field(
        None,
        max_items=10,
        description="User-defined tags for organization"
    )
    smart_capabilities: Optional[List[SmartCapability]] = Field(
        None,
        description="Smart home integration capabilities"
    )
    is_smart_controlled: bool = Field(
        False,
        description="Whether appliance is connected to smart home system"
    )
    image_url: Optional[HttpUrl] = Field(
        None,
        description="URL to appliance image"
    )
    
    @root_validator
    def validate_location(cls, values):
        location = values.get('location')
        custom_location = values.get('custom_location')
        
        if location == ApplianceLocation.OTHER and not custom_location:
            raise ValueError("Custom location is required when location is 'other'")
        
        if location != ApplianceLocation.OTHER and custom_location:
            values['custom_location'] = None  # Clear custom location if not needed
        
        return values
    
    @validator('warranty_end_date')
    def validate_warranty_date(cls, v, values):
        purchase_date = values.get('purchase_date')
        if v and purchase_date and v < purchase_date:
            raise ValueError("Warranty end date cannot be before purchase date")
        return v
    
    @validator('tags')
    def clean_tags(cls, v):
        if v:
            # Remove duplicates and clean whitespace
            return list(set(tag.strip().lower() for tag in v if tag.strip()))
        return v


class UserApplianceUpdate(BaseModel):
    """Schema for updating an existing appliance (all fields optional)"""
    
    custom_name: Optional[constr(min_length=1, max_length=100)] = None
    brand: Optional[constr(max_length=50)] = None
    model: Optional[constr(max_length=100)] = None
    serial_number: Optional[constr(max_length=100)] = None
    count: Optional[conint(ge=1, le=100)] = None
    
    # Usage details
    hours_per_day: Optional[confloat(ge=0, le=24)] = None
    days_per_week: Optional[conint(ge=0, le=7)] = None
    usage_pattern: Optional[UsagePattern] = None
    seasonal_months: Optional[List[conint(ge=1, le=12)]] = None
    peak_hours: Optional[List[conint(ge=0, le=23)]] = None
    
    # Power specifications
    custom_wattage: Optional[conint(gt=0, le=50000)] = None
    standby_wattage: Optional[conint(ge=0, le=1000)] = None
    voltage: Optional[conint(ge=100, le=480)] = None
    amperage: Optional[confloat(gt=0, le=100)] = None
    energy_efficiency_rating: Optional[EnergyEfficiencyRating] = None
    annual_kwh_estimate: Optional[confloat(gt=0)] = None
    
    # Additional details
    location: Optional[ApplianceLocation] = None
    custom_location: Optional[constr(max_length=50)] = None
    status: Optional[ApplianceStatus] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    warranty_end_date: Optional[date] = None
    installation_date: Optional[date] = None
    notes: Optional[constr(max_length=500)] = None
    tags: Optional[List[constr(max_length=30)]] = None
    smart_capabilities: Optional[List[SmartCapability]] = None
    is_smart_controlled: Optional[bool] = None
    image_url: Optional[HttpUrl] = None
    
    class Config:
        use_enum_values = True


class UserApplianceResponse(BaseModel):
    """Complete response schema for a user appliance"""
    
    id: UUID
    user_id: UUID
    appliance_catalog_id: Optional[str]
    
    # Basic info
    custom_name: str
    brand: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    count: int
    status: ApplianceStatus = ApplianceStatus.ACTIVE
    
    # Usage details
    hours_per_day: float
    days_per_week: int
    usage_pattern: UsagePattern
    seasonal_months: Optional[List[int]]
    peak_hours: Optional[List[int]]
    
    # Power specifications
    custom_wattage: Optional[int]
    calculated_wattage: int  # Either custom or from catalog
    standby_wattage: Optional[int]
    voltage: Optional[int]
    amperage: Optional[float]
    energy_efficiency_rating: Optional[EnergyEfficiencyRating]
    annual_kwh_estimate: Optional[float]
    
    # Location
    location: Optional[ApplianceLocation]
    custom_location: Optional[str]
    display_location: str  # Computed field
    
    # Dates and warranty
    purchase_date: Optional[date]
    purchase_price: Optional[Decimal]
    warranty_end_date: Optional[date]
    installation_date: Optional[date]
    is_under_warranty: bool  # Computed field
    appliance_age_days: Optional[int]  # Computed field
    
    # Smart features
    smart_capabilities: Optional[List[SmartCapability]]
    is_smart_controlled: bool
    
    # Metadata
    notes: Optional[str]
    tags: Optional[List[str]]
    image_url: Optional[HttpUrl]
    
    # Calculated fields
    estimated_daily_kwh: float
    estimated_weekly_kwh: float
    estimated_monthly_kwh: float
    estimated_annual_kwh: float
    estimated_monthly_cost: Optional[float]  # Requires electricity rate
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_maintenance_date: Optional[datetime]
    next_maintenance_due: Optional[date]
    
    # Related data (optional, populated when needed)
    catalog_info: Optional[ApplianceCatalogResponse]
    maintenance_history_count: int = 0
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174000",
                "custom_name": "Kitchen Fridge",
                "brand": "Samsung",
                "model": "RF28R7351SR",
                "count": 1,
                "status": "active",
                "hours_per_day": 24,
                "days_per_week": 7,
                "calculated_wattage": 150,
                "estimated_monthly_kwh": 108,
                "estimated_monthly_cost": 15.12,
                "is_under_warranty": True,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class UserApplianceListResponse(BaseModel):
    """Paginated list response for user appliances"""
    
    items: List[UserApplianceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    # Summary statistics
    summary: Optional["ApplianceSummaryStats"] = None


# ==================== FILTERING AND QUERY SCHEMAS ====================

class ApplianceFilterSchema(BaseModel):
    """Schema for filtering appliances"""
    
    status: Optional[List[ApplianceStatus]] = Field(None, description="Filter by status")
    location: Optional[List[ApplianceLocation]] = Field(None, description="Filter by location")
    tags: Optional[List[str]] = Field(None, description="Filter by tags (OR condition)")
    brand: Optional[str] = Field(None, description="Filter by brand (partial match)")
    is_smart_controlled: Optional[bool] = Field(None, description="Filter smart appliances")
    is_under_warranty: Optional[bool] = Field(None, description="Filter by warranty status")
    min_wattage: Optional[int] = Field(None, ge=0, description="Minimum wattage")
    max_wattage: Optional[int] = Field(None, le=50000, description="Maximum wattage")
    usage_pattern: Optional[List[UsagePattern]] = Field(None, description="Filter by usage pattern")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in name/brand/model")
    
    @validator('search')
    def clean_search(cls, v):
        if v:
            return v.strip()
        return v


class ApplianceSortSchema(BaseModel):
    """Schema for sorting appliances"""
    
    sort_by: str = Field(
        "created_at",
        description="Field to sort by",
        regex="^(custom_name|brand|created_at|updated_at|calculated_wattage|estimated_monthly_kwh|purchase_date)$"
    )
    sort_order: str = Field(
        "desc",
        description="Sort order",
        regex="^(asc|desc)$"
    )


class PaginationSchema(BaseModel):
    """Schema for pagination parameters"""
    
    page: conint(ge=1) = Field(1, description="Page number")
    page_size: conint(ge=1, le=100) = Field(20, description="Items per page")


# ==================== BULK OPERATIONS SCHEMAS ====================

class BulkApplianceCreate(BaseModel):
    """Schema for creating multiple appliances at once"""
    
    appliances: List[UserApplianceCreate] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of appliances to create"
    )
    
    @validator('appliances')
    def validate_unique_names(cls, v):
        names = [app.custom_name for app in v]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate appliance names not allowed in bulk creation")
        return v


class BulkApplianceUpdate(BaseModel):
    """Schema for updating multiple appliances"""
    
    appliance_ids: List[UUID] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="IDs of appliances to update"
    )
    update_data: UserApplianceUpdate = Field(
        ...,
        description="Update data to apply to all selected appliances"
    )


class BulkOperationResponse(BaseModel):
    """Response for bulk operations"""
    
    success_count: int
    failure_count: int
    total_count: int
    successful_ids: List[UUID]
    failed_ids: List[UUID]
    errors: Optional[Dict[str, str]] = None


# ==================== ANALYTICS AND STATISTICS SCHEMAS ====================

class ApplianceSummaryStats(BaseModel):
    """Summary statistics for user's appliances"""
    
    total_appliances: int
    total_items: int  # Sum of all counts
    active_appliances: int
    smart_appliances: int
    
    # Energy statistics
    total_daily_kwh: float
    total_monthly_kwh: float
    total_annual_kwh: float
    estimated_monthly_cost: Optional[float]
    
    # Breakdown by location
    appliances_by_location: Dict[str, int]
    
    # Breakdown by status
    appliances_by_status: Dict[str, int]
    
    # Top consumers
    top_energy_consumers: List[Dict[str, Any]]
    
    # Maintenance
    appliances_needing_maintenance: int
    appliances_under_warranty: int
    
    # Age statistics
    average_age_days: Optional[float]
    oldest_appliance_id: Optional[UUID]
    newest_appliance_id: Optional[UUID]


class EnergyConsumptionTrend(BaseModel):
    """Energy consumption trend data"""
    
    period: str  # "daily", "weekly", "monthly", "yearly"
    timestamp: datetime
    total_kwh: float
    total_cost: Optional[float]
    appliance_breakdown: Dict[UUID, float]  # appliance_id -> kwh


class ApplianceUsageReport(BaseModel):
    """Detailed usage report for an appliance"""
    
    appliance_id: UUID
    appliance_name: str
    reporting_period_start: date
    reporting_period_end: date
    
    # Usage metrics
    total_runtime_hours: float
    average_daily_hours: float
    days_used: int
    
    # Energy metrics
    total_kwh_consumed: float
    average_daily_kwh: float
    peak_usage_hour: Optional[int]
    
    # Cost metrics
    total_cost: Optional[float]
    average_daily_cost: Optional[float]
    
    # Comparisons
    vs_catalog_typical: Optional[float]  # Percentage difference
    vs_similar_users: Optional[float]  # Percentage difference
    
    # Recommendations
    energy_saving_potential_kwh: Optional[float]
    recommended_actions: List[str]






