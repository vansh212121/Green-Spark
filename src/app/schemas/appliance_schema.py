# ==========4.1 SCHEMA==========
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
