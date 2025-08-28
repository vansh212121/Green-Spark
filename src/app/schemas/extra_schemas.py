# # app/schemas/bill_schema.py

# =======4.1 schema========
# import uuid
# from datetime import datetime, date
# from typing import Dict, Any, Optional, List
# from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
# from enum import Enum


# class BillSource(str, Enum):
#     PDF = "pdf"
#     MANUAL = "manual"


# class BillStatus(str, Enum):
#     PROCESSING = "processing"
#     SUCCESS = "success"
#     FAILED = "failed"


# class BillBase(BaseModel):
#     """Base schema for bill data"""
#     billing_period_start: date
#     billing_period_end: date
#     kwh_total: float = Field(..., gt=0, description="Total kWh consumed")
#     cost_total: float = Field(..., ge=0, description="Total cost in INR")
#     provider: str = Field(..., min_length=1, max_length=100)

#     @model_validator(mode='after')
#     def validate_billing_period(self) -> 'BillBase':
#         if self.billing_period_end <= self.billing_period_start:
#             raise ValueError('Billing period end must be after billing period start')

#         # Check if period is reasonable (not more than 3 months)
#         days_diff = (self.billing_period_end - self.billing_period_start).days
#         if days_diff > 90:
#             raise ValueError('Billing period cannot exceed 90 days')

#         return self


# class BillCreate(BillBase):
#     """Schema for creating a new bill"""
#     source_type: BillSource = BillSource.PDF
#     file_uri: Optional[str] = None

#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "billing_period_start": "2024-01-01",
#                 "billing_period_end": "2024-01-31",
#                 "kwh_total": 450.5,
#                 "cost_total": 3500.00,
#                 "provider": "TATA Power",
#                 "source_type": "pdf"
#             }
#         }
#     )


# class BillManualCreate(BillBase):
#     """Schema for manually creating a bill"""
#     source_type: BillSource = Field(default=BillSource.MANUAL, frozen=True)

#     # Additional fields for manual entry
#     connection_number: Optional[str] = Field(None, max_length=50)
#     meter_number: Optional[str] = Field(None, max_length=50)
#     sanctioned_load: Optional[float] = Field(None, gt=0)
#     tariff_category: Optional[str] = Field(None, max_length=50)

#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "billing_period_start": "2024-01-01",
#                 "billing_period_end": "2024-01-31",
#                 "kwh_total": 450.5,
#                 "cost_total": 3500.00,
#                 "provider": "TATA Power",
#                 "connection_number": "12345678",
#                 "meter_number": "MTR123456",
#                 "sanctioned_load": 3.0,
#                 "tariff_category": "Domestic"
#             }
#         }
#     )


# class BillUpdate(BaseModel):
#     """Schema for updating bill data"""
#     billing_period_start: Optional[date] = None
#     billing_period_end: Optional[date] = None
#     kwh_total: Optional[float] = Field(None, gt=0)
#     cost_total: Optional[float] = Field(None, ge=0)
#     provider: Optional[str] = Field(None, min_length=1, max_length=100)

#     @model_validator(mode='after')
#     def validate_billing_period(self) -> 'BillUpdate':
#         if self.billing_period_start and self.billing_period_end:
#             if self.billing_period_end <= self.billing_period_start:
#                 raise ValueError('Billing period end must be after billing period start')
#         return self


# class BillResponse(BillBase):
#     """Schema for bill response"""
#     id: uuid.UUID
#     user_id: uuid.UUID
#     parse_status: BillStatus
#     source_type: BillSource
#     file_uri: Optional[str]
#     normalized_json: Dict[str, Any]
#     parser_version: Optional[str]
#     checksum: Optional[str]
#     created_at: datetime

#     # Computed fields
#     days_in_period: int = Field(default=0)
#     daily_avg_kwh: float = Field(default=0.0)
#     daily_avg_cost: float = Field(default=0.0)

#     @model_validator(mode='after')
#     def compute_fields(self) -> 'BillResponse':
#         self.days_in_period = (self.billing_period_end - self.billing_period_start).days
#         if self.days_in_period > 0:
#             self.daily_avg_kwh = round(self.kwh_total / self.days_in_period, 2)
#             self.daily_avg_cost = round(self.cost_total / self.days_in_period, 2)
#         return self

#     model_config = ConfigDict(from_attributes=True)


# class BillDetailResponse(BillResponse):
#     """Detailed bill response with relationships"""
#     estimates: List['ApplianceEstimateResponse'] = []
#     insight: Optional['InsightResponse'] = None

#     model_config = ConfigDict(from_attributes=True)


# class BillListResponse(BaseModel):
#     """Schema for paginated bill list"""
#     total: int
#     page: int
#     page_size: int
#     bills: List[BillResponse]

#     # Summary statistics
#     total_kwh: float = Field(default=0.0)
#     total_cost: float = Field(default=0.0)
#     avg_monthly_kwh: float = Field(default=0.0)
#     avg_monthly_cost: float = Field(default=0.0)


# class BillUploadResponse(BaseModel):
#     """Response after bill upload"""
#     bill_id: uuid.UUID
#     status: BillStatus
#     message: str
#     estimated_processing_time: int = Field(default=30, description="Estimated processing time in seconds")


# ========OPUS 4.1 THINKING SCHEMA===========
# app/schemas/bill_schema.py

# import uuid
# from datetime import date, datetime
# from typing import Optional, List, Dict, Any
# from decimal import Decimal
# from pydantic import BaseModel, Field, field_validator, ConfigDict
# from src.app.models.bill_model import BillSource, BillStatus
# from src.app.schemas.base_schema import PaginatedResponse


# class BillBase(BaseModel):
#     """Base bill schema"""
#     billing_period_start: date = Field(..., description="Billing period start date")
#     billing_period_end: date = Field(..., description="Billing period end date")
#     kwh_total: float = Field(..., gt=0, description="Total kWh consumed")
#     cost_total: float = Field(..., gt=0, description="Total cost in INR")
#     provider: str = Field(..., min_length=1, max_length=100, description="Electricity provider")

#     @field_validator('billing_period_end')
#     @classmethod
#     def validate_billing_period(cls, v: date, info) -> date:
#         """Validate billing period dates"""
#         if 'billing_period_start' in info.data and v <= info.data['billing_period_start']:
#             raise ValueError('Billing period end must be after start date')
#         return v

#     @field_validator('kwh_total', 'cost_total')
#     @classmethod
#     def validate_positive_values(cls, v: float) -> float:
#         """Ensure positive values for consumption and cost"""
#         if v <= 0:
#             raise ValueError('Value must be positive')
#         return round(v, 2)


# class BillCreateManual(BillBase):
#     """Schema for manually creating a bill"""
#     source_type: BillSource = Field(default=BillSource.MANUAL)

#     # Optional additional fields for manual entry
#     connection_number: Optional[str] = Field(None, max_length=50, description="Connection/Account number")
#     meter_number: Optional[str] = Field(None, max_length=50, description="Meter number")
#     sanctioned_load: Optional[float] = Field(None, gt=0, description="Sanctioned load in kW")
#     tariff_category: Optional[str] = Field(None, max_length=50, description="Tariff category")

#     # Breakdown fields (optional)
#     fixed_charges: Optional[float] = Field(None, ge=0, description="Fixed charges")
#     energy_charges: Optional[float] = Field(None, ge=0, description="Energy charges")
#     taxes: Optional[float] = Field(None, ge=0, description="Taxes and duties")
#     other_charges: Optional[float] = Field(None, ge=0, description="Other charges")


# class BillUploadPDF(BaseModel):
#     """Schema for PDF bill upload"""
#     file_name: str = Field(..., description="Original file name")
#     file_size: int = Field(..., gt=0, le=10485760, description="File size in bytes (max 10MB)")
#     file_content_type: str = Field(..., pattern="^application/pdf$", description="MIME type")

#     @field_validator('file_size')
#     @classmethod
#     def validate_file_size(cls, v: int) -> int:
#         """Validate file size"""
#         if v > 10 * 1024 * 1024:  # 10MB
#             raise ValueError('File size exceeds 10MB limit')
#         return v


# class BillUpdate(BaseModel):
#     """Schema for updating bill information"""
#     billing_period_start: Optional[date] = None
#     billing_period_end: Optional[date] = None
#     kwh_total: Optional[float] = Field(None, gt=0)
#     cost_total: Optional[float] = Field(None, gt=0)
#     provider: Optional[str] = Field(None, min_length=1, max_length=100)

#     model_config = ConfigDict(validate_assignment=True)


# class BillResponse(BillBase):
#     """Schema for bill response"""
#     id: uuid.UUID
#     user_id: uuid.UUID
#     source_type: BillSource
#     parse_status: BillStatus
#     file_uri: Optional[str]
#     normalized_json: Dict[str, Any]
#     parser_version: Optional[str]
#     checksum: Optional[str]
#     created_at: datetime

#     # Calculated fields
#     consumption_per_day: Optional[float] = Field(None, description="Average daily consumption")
#     cost_per_unit: Optional[float] = Field(None, description="Cost per kWh")
#     billing_days: Optional[int] = Field(None, description="Number of days in billing period")

#     # Related data counts
#     estimates_count: Optional[int] = Field(None, description="Number of appliance estimates")
#     has_insights: Optional[bool] = Field(None, description="Whether insights are available")

#     model_config = ConfigDict(from_attributes=True)

#     @field_validator('normalized_json', mode='before')
#     @classmethod
#     def ensure_dict(cls, v: Any) -> Dict[str, Any]:
#         """Ensure normalized_json is always a dict"""
#         if v is None:
#             return {}
#         if isinstance(v, str):
#             import json
#             try:
#                 return json.loads(v)
#             except json.JSONDecodeError:
#                 return {}
#         return v


# class BillDetailResponse(BillResponse):
#     """Detailed bill response with related data"""
#     from src.app.schemas.appliance_schema import ApplianceEstimateResponse
#     from src.app.schemas.insight_schema import InsightSummaryResponse

#     estimates: Optional[List[ApplianceEstimateResponse]] = Field(None, description="Appliance estimates")
#     insight: Optional[InsightSummaryResponse] = Field(None, description="Associated insights")

#     # Comparison data
#     previous_bill: Optional['BillSummaryResponse'] = Field(None, description="Previous bill for comparison")
#     year_ago_bill: Optional['BillSummaryResponse'] = Field(None, description="Bill from same month last year")


# class BillSummaryResponse(BaseModel):
#     """Summary bill information for listings"""
#     id: uuid.UUID
#     billing_period_start: date
#     billing_period_end: date
#     kwh_total: float
#     cost_total: float
#     provider: str
#     parse_status: BillStatus
#     created_at: datetime
#     has_insights: bool = False

#     model_config = ConfigDict(from_attributes=True)


# class BillListResponse(PaginatedResponse):
#     """Paginated bill list response"""
#     items: List[BillSummaryResponse]

#     # Aggregated statistics
#     total_kwh: Optional[float] = Field(None, description="Total kWh across all bills")
#     total_cost: Optional[float] = Field(None, description="Total cost across all bills")
#     average_monthly_kwh: Optional[float] = Field(None, description="Average monthly consumption")
#     average_monthly_cost: Optional[float] = Field(None, description="Average monthly cost")


# class BillComparisonResponse(BaseModel):
#     """Bill comparison response"""
#     current_bill: BillResponse
#     previous_bill: Optional[BillResponse]

#     # Comparison metrics
#     kwh_change: Optional[float] = Field(None, description="Change in kWh consumption")
#     kwh_change_percentage: Optional[float] = Field(None, description="Percentage change in kWh")
#     cost_change: Optional[float] = Field(None, description="Change in cost")
#     cost_change_percentage: Optional[float] = Field(None, description="Percentage change in cost")

#     # Trends
#     trend: Optional[str] = Field(None, description="Trend direction: up, down, or stable")
#     recommendation: Optional[str] = Field(None, description="Brief recommendation based on comparison")


# class BillStatisticsResponse(BaseModel):
#     """Bill statistics response"""
#     total_bills: int
#     total_kwh: float
#     total_cost: float
#     average_monthly_kwh: float
#     average_monthly_cost: float
#     highest_consumption_month: Optional[str]
#     lowest_consumption_month: Optional[str]

#     # Time-based breakdowns
#     monthly_breakdown: Optional[List[Dict[str, Any]]] = Field(None, description="Monthly consumption breakdown")
#     seasonal_analysis: Optional[Dict[str, Any]] = Field(None, description="Seasonal consumption patterns")


# class BillParseResultResponse(BaseModel):
#     """Response after bill parsing"""
#     bill_id: uuid.UUID
#     status: BillStatus
#     message: str
#     parsed_data: Optional[Dict[str, Any]] = Field(None, description="Parsed bill data")
#     errors: Optional[List[str]] = Field(None, description="Parsing errors if any")
#     confidence_score: Optional[float] = Field(None, description="Parsing confidence score")
# # app/schemas/bill_schema.py

# =======4.1 schema========
# import uuid
# from datetime import datetime, date
# from typing import Dict, Any, Optional, List
# from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
# from enum import Enum


# class BillSource(str, Enum):
#     PDF = "pdf"
#     MANUAL = "manual"


# class BillStatus(str, Enum):
#     PROCESSING = "processing"
#     SUCCESS = "success"
#     FAILED = "failed"


# class BillBase(BaseModel):
#     """Base schema for bill data"""
#     billing_period_start: date
#     billing_period_end: date
#     kwh_total: float = Field(..., gt=0, description="Total kWh consumed")
#     cost_total: float = Field(..., ge=0, description="Total cost in INR")
#     provider: str = Field(..., min_length=1, max_length=100)

#     @model_validator(mode='after')
#     def validate_billing_period(self) -> 'BillBase':
#         if self.billing_period_end <= self.billing_period_start:
#             raise ValueError('Billing period end must be after billing period start')

#         # Check if period is reasonable (not more than 3 months)
#         days_diff = (self.billing_period_end - self.billing_period_start).days
#         if days_diff > 90:
#             raise ValueError('Billing period cannot exceed 90 days')

#         return self


# class BillCreate(BillBase):
#     """Schema for creating a new bill"""
#     source_type: BillSource = BillSource.PDF
#     file_uri: Optional[str] = None

#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "billing_period_start": "2024-01-01",
#                 "billing_period_end": "2024-01-31",
#                 "kwh_total": 450.5,
#                 "cost_total": 3500.00,
#                 "provider": "TATA Power",
#                 "source_type": "pdf"
#             }
#         }
#     )


# class BillManualCreate(BillBase):
#     """Schema for manually creating a bill"""
#     source_type: BillSource = Field(default=BillSource.MANUAL, frozen=True)

#     # Additional fields for manual entry
#     connection_number: Optional[str] = Field(None, max_length=50)
#     meter_number: Optional[str] = Field(None, max_length=50)
#     sanctioned_load: Optional[float] = Field(None, gt=0)
#     tariff_category: Optional[str] = Field(None, max_length=50)

#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "billing_period_start": "2024-01-01",
#                 "billing_period_end": "2024-01-31",
#                 "kwh_total": 450.5,
#                 "cost_total": 3500.00,
#                 "provider": "TATA Power",
#                 "connection_number": "12345678",
#                 "meter_number": "MTR123456",
#                 "sanctioned_load": 3.0,
#                 "tariff_category": "Domestic"
#             }
#         }
#     )


# class BillUpdate(BaseModel):
#     """Schema for updating bill data"""
#     billing_period_start: Optional[date] = None
#     billing_period_end: Optional[date] = None
#     kwh_total: Optional[float] = Field(None, gt=0)
#     cost_total: Optional[float] = Field(None, ge=0)
#     provider: Optional[str] = Field(None, min_length=1, max_length=100)

#     @model_validator(mode='after')
#     def validate_billing_period(self) -> 'BillUpdate':
#         if self.billing_period_start and self.billing_period_end:
#             if self.billing_period_end <= self.billing_period_start:
#                 raise ValueError('Billing period end must be after billing period start')
#         return self


# class BillResponse(BillBase):
#     """Schema for bill response"""
#     id: uuid.UUID
#     user_id: uuid.UUID
#     parse_status: BillStatus
#     source_type: BillSource
#     file_uri: Optional[str]
#     normalized_json: Dict[str, Any]
#     parser_version: Optional[str]
#     checksum: Optional[str]
#     created_at: datetime

#     # Computed fields
#     days_in_period: int = Field(default=0)
#     daily_avg_kwh: float = Field(default=0.0)
#     daily_avg_cost: float = Field(default=0.0)

#     @model_validator(mode='after')
#     def compute_fields(self) -> 'BillResponse':
#         self.days_in_period = (self.billing_period_end - self.billing_period_start).days
#         if self.days_in_period > 0:
#             self.daily_avg_kwh = round(self.kwh_total / self.days_in_period, 2)
#             self.daily_avg_cost = round(self.cost_total / self.days_in_period, 2)
#         return self

#     model_config = ConfigDict(from_attributes=True)


# class BillDetailResponse(BillResponse):
#     """Detailed bill response with relationships"""
#     estimates: List['ApplianceEstimateResponse'] = []
#     insight: Optional['InsightResponse'] = None

#     model_config = ConfigDict(from_attributes=True)


# class BillListResponse(BaseModel):
#     """Schema for paginated bill list"""
#     total: int
#     page: int
#     page_size: int
#     bills: List[BillResponse]

#     # Summary statistics
#     total_kwh: float = Field(default=0.0)
#     total_cost: float = Field(default=0.0)
#     avg_monthly_kwh: float = Field(default=0.0)
#     avg_monthly_cost: float = Field(default=0.0)


# class BillUploadResponse(BaseModel):
#     """Response after bill upload"""
#     bill_id: uuid.UUID
#     status: BillStatus
#     message: str
#     estimated_processing_time: int = Field(default=30, description="Estimated processing time in seconds")


# ========OPUS 4.1 THINKING SCHEMA===========
# app/schemas/bill_schema.py

# import uuid
# from datetime import date, datetime
# from typing import Optional, List, Dict, Any
# from decimal import Decimal
# from pydantic import BaseModel, Field, field_validator, ConfigDict
# from src.app.models.bill_model import BillSource, BillStatus
# from src.app.schemas.base_schema import PaginatedResponse


# class BillBase(BaseModel):
#     """Base bill schema"""
#     billing_period_start: date = Field(..., description="Billing period start date")
#     billing_period_end: date = Field(..., description="Billing period end date")
#     kwh_total: float = Field(..., gt=0, description="Total kWh consumed")
#     cost_total: float = Field(..., gt=0, description="Total cost in INR")
#     provider: str = Field(..., min_length=1, max_length=100, description="Electricity provider")

#     @field_validator('billing_period_end')
#     @classmethod
#     def validate_billing_period(cls, v: date, info) -> date:
#         """Validate billing period dates"""
#         if 'billing_period_start' in info.data and v <= info.data['billing_period_start']:
#             raise ValueError('Billing period end must be after start date')
#         return v

#     @field_validator('kwh_total', 'cost_total')
#     @classmethod
#     def validate_positive_values(cls, v: float) -> float:
#         """Ensure positive values for consumption and cost"""
#         if v <= 0:
#             raise ValueError('Value must be positive')
#         return round(v, 2)


# class BillCreateManual(BillBase):
#     """Schema for manually creating a bill"""
#     source_type: BillSource = Field(default=BillSource.MANUAL)

#     # Optional additional fields for manual entry
#     connection_number: Optional[str] = Field(None, max_length=50, description="Connection/Account number")
#     meter_number: Optional[str] = Field(None, max_length=50, description="Meter number")
#     sanctioned_load: Optional[float] = Field(None, gt=0, description="Sanctioned load in kW")
#     tariff_category: Optional[str] = Field(None, max_length=50, description="Tariff category")

#     # Breakdown fields (optional)
#     fixed_charges: Optional[float] = Field(None, ge=0, description="Fixed charges")
#     energy_charges: Optional[float] = Field(None, ge=0, description="Energy charges")
#     taxes: Optional[float] = Field(None, ge=0, description="Taxes and duties")
#     other_charges: Optional[float] = Field(None, ge=0, description="Other charges")


# class BillUploadPDF(BaseModel):
#     """Schema for PDF bill upload"""
#     file_name: str = Field(..., description="Original file name")
#     file_size: int = Field(..., gt=0, le=10485760, description="File size in bytes (max 10MB)")
#     file_content_type: str = Field(..., pattern="^application/pdf$", description="MIME type")

#     @field_validator('file_size')
#     @classmethod
#     def validate_file_size(cls, v: int) -> int:
#         """Validate file size"""
#         if v > 10 * 1024 * 1024:  # 10MB
#             raise ValueError('File size exceeds 10MB limit')
#         return v


# class BillUpdate(BaseModel):
#     """Schema for updating bill information"""
#     billing_period_start: Optional[date] = None
#     billing_period_end: Optional[date] = None
#     kwh_total: Optional[float] = Field(None, gt=0)
#     cost_total: Optional[float] = Field(None, gt=0)
#     provider: Optional[str] = Field(None, min_length=1, max_length=100)

#     model_config = ConfigDict(validate_assignment=True)


# class BillResponse(BillBase):
#     """Schema for bill response"""
#     id: uuid.UUID
#     user_id: uuid.UUID
#     source_type: BillSource
#     parse_status: BillStatus
#     file_uri: Optional[str]
#     normalized_json: Dict[str, Any]
#     parser_version: Optional[str]
#     checksum: Optional[str]
#     created_at: datetime

#     # Calculated fields
#     consumption_per_day: Optional[float] = Field(None, description="Average daily consumption")
#     cost_per_unit: Optional[float] = Field(None, description="Cost per kWh")
#     billing_days: Optional[int] = Field(None, description="Number of days in billing period")

#     # Related data counts
#     estimates_count: Optional[int] = Field(None, description="Number of appliance estimates")
#     has_insights: Optional[bool] = Field(None, description="Whether insights are available")

#     model_config = ConfigDict(from_attributes=True)

#     @field_validator('normalized_json', mode='before')
#     @classmethod
#     def ensure_dict(cls, v: Any) -> Dict[str, Any]:
#         """Ensure normalized_json is always a dict"""
#         if v is None:
#             return {}
#         if isinstance(v, str):
#             import json
#             try:
#                 return json.loads(v)
#             except json.JSONDecodeError:
#                 return {}
#         return v


# class BillDetailResponse(BillResponse):
#     """Detailed bill response with related data"""
#     from src.app.schemas.appliance_schema import ApplianceEstimateResponse
#     from src.app.schemas.insight_schema import InsightSummaryResponse

#     estimates: Optional[List[ApplianceEstimateResponse]] = Field(None, description="Appliance estimates")
#     insight: Optional[InsightSummaryResponse] = Field(None, description="Associated insights")

#     # Comparison data
#     previous_bill: Optional['BillSummaryResponse'] = Field(None, description="Previous bill for comparison")
#     year_ago_bill: Optional['BillSummaryResponse'] = Field(None, description="Bill from same month last year")


# class BillSummaryResponse(BaseModel):
#     """Summary bill information for listings"""
#     id: uuid.UUID
#     billing_period_start: date
#     billing_period_end: date
#     kwh_total: float
#     cost_total: float
#     provider: str
#     parse_status: BillStatus
#     created_at: datetime
#     has_insights: bool = False

#     model_config = ConfigDict(from_attributes=True)


# class BillListResponse(PaginatedResponse):
#     """Paginated bill list response"""
#     items: List[BillSummaryResponse]

#     # Aggregated statistics
#     total_kwh: Optional[float] = Field(None, description="Total kWh across all bills")
#     total_cost: Optional[float] = Field(None, description="Total cost across all bills")
#     average_monthly_kwh: Optional[float] = Field(None, description="Average monthly consumption")
#     average_monthly_cost: Optional[float] = Field(None, description="Average monthly cost")


# class BillComparisonResponse(BaseModel):
#     """Bill comparison response"""
#     current_bill: BillResponse
#     previous_bill: Optional[BillResponse]

#     # Comparison metrics
#     kwh_change: Optional[float] = Field(None, description="Change in kWh consumption")
#     kwh_change_percentage: Optional[float] = Field(None, description="Percentage change in kWh")
#     cost_change: Optional[float] = Field(None, description="Change in cost")
#     cost_change_percentage: Optional[float] = Field(None, description="Percentage change in cost")

#     # Trends
#     trend: Optional[str] = Field(None, description="Trend direction: up, down, or stable")
#     recommendation: Optional[str] = Field(None, description="Brief recommendation based on comparison")


# class BillStatisticsResponse(BaseModel):
#     """Bill statistics response"""
#     total_bills: int
#     total_kwh: float
#     total_cost: float
#     average_monthly_kwh: float
#     average_monthly_cost: float
#     highest_consumption_month: Optional[str]
#     lowest_consumption_month: Optional[str]

#     # Time-based breakdowns
#     monthly_breakdown: Optional[List[Dict[str, Any]]] = Field(None, description="Monthly consumption breakdown")
#     seasonal_analysis: Optional[Dict[str, Any]] = Field(None, description="Seasonal consumption patterns")


# class BillParseResultResponse(BaseModel):
#     """Response after bill parsing"""
#     bill_id: uuid.UUID
#     status: BillStatus
#     message: str
#     parsed_data: Optional[Dict[str, Any]] = Field(None, description="Parsed bill data")
#     errors: Optional[List[str]] = Field(None, description="Parsing errors if any")
#     confidence_score: Optional[float] = Field(None, description="Parsing confidence score")
