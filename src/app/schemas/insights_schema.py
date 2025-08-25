# =========4.1 SCHEMA========
# import uuid
# from datetime import datetime
# from typing import Dict, Any, List, Optional
# from pydantic import BaseModel, Field, ConfigDict
# from enum import Enum


# class InsightStatus(str, Enum):
#     PENDING = "pending"
#     COMPLETED = "completed"
#     FAILED = "failed"


# class ConsumptionTrend(BaseModel):
#     """Schema for consumption trend data"""
#     month: str
#     kwh: float
#     cost: float
#     percentage_change: Optional[float] = None


# class ApplianceBreakdown(BaseModel):
#     """Schema for appliance consumption breakdown"""
#     appliance_name: str
#     category: str
#     kwh: float
#     cost: float
#     percentage_of_total: float
#     icon_emoji: str


# class Recommendation(BaseModel):
#     """Schema for energy-saving recommendations"""
#     id: str
#     title: str
#     description: str
#     potential_savings_kwh: float
#     potential_savings_cost: float
#     priority: str = Field(..., pattern="^(high|medium|low)$")
#     difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
#     action_type: str = Field(..., pattern="^(behavioral|upgrade|maintenance)$")
#     icon: str


# class CarbonFootprint(BaseModel):
#     """Schema for carbon footprint data"""
#     total_co2_kg: float
#     equivalent_trees_needed: int
#     comparison_to_avg: float
#     reduction_potential_kg: float


# class InsightBase(BaseModel):
#     """Base schema for insights"""
#     status: InsightStatus = InsightStatus.PENDING


# class InsightCreate(InsightBase):
#     """Schema for creating insights"""
#     bill_id: uuid.UUID
#     user_id: uuid.UUID


# class InsightResponse(InsightBase):
#     """Schema for insight response"""
#     id: uuid.UUID
#     bill_id: uuid.UUID
#     user_id: uuid.UUID
#     generated_at: datetime
#     structured_data: Dict[str, Any]
    
#     # Parsed structured data fields
#     summary: Optional[Dict[str, Any]] = None
#     consumption_trends: List[ConsumptionTrend] = []
#     appliance_breakdown: List[ApplianceBreakdown] = []
#     recommendations: List[Recommendation] = []
#     carbon_footprint: Optional[CarbonFootprint] = None
    
#     model_config = ConfigDict(from_attributes=True)


# class InsightDetailResponse(InsightResponse):
#     """Detailed insight response with all computed data"""
    
#     # Additional analytics
#     peak_usage_hours: List[int] = []
#     cost_per_kwh: float = Field(default=0.0)
#     comparison_with_similar_homes: Optional[Dict[str, Any]] = None
#     seasonal_patterns: Optional[Dict[str, Any]] = None
    
#     # Gamification elements
#     energy_score: int = Field(ge=0, le=100, default=0)
#     badges_earned: List[str] = []
#     improvement_from_last_month: Optional[float] = None
    
#     model_config = ConfigDict(from_attributes=True)


# class InsightSummaryResponse(BaseModel):
#     """Summary response for quick insights"""
#     bill_id: uuid.UUID
#     status: InsightStatus
#     key_findings: List[str]
#     top_recommendation: Optional[Recommendation] = None
#     total_savings_potential: float = Field(default=0.0)
#     energy_score: int = Field(ge=0, le=100, default=0)
    
    
    
    
    
# ============4.1 THINKING SCHEMA============
# # app/schemas/insight_schema.py

# import uuid
# from datetime import datetime
# from typing import Optional, List, Dict, Any
# from pydantic import BaseModel, Field, field_validator, ConfigDict
# from src.app.models.insights_model import InsightStatus
# from src.app.schemas.base_schema import PaginatedResponse


# class InsightBase(BaseModel):
#     """Base insight schema"""
#     status: InsightStatus = Field(default=InsightStatus.PENDING)
    

# class InsightCreate(InsightBase):
#     """Schema for creating insights"""
#     bill_id: uuid.UUID = Field(..., description="Associated bill ID")
#     user_id: uuid.UUID = Field(..., description="User ID")


# class InsightStructuredData(BaseModel):
#     """Structured data for insights"""
    
#     # Summary metrics
#     summary: Dict[str, Any] = Field(..., description="High-level summary")
    
#     # Energy breakdown
#     consumption_analysis: Dict[str, Any] = Field(..., description="Detailed consumption analysis")
#     appliance_breakdown: List[Dict[str, Any]] = Field(..., description="Appliance-wise breakdown")
    
#     # Recommendations
#     recommendations: List['RecommendationItem'] = Field(..., description="Actionable recommendations")
    
#     # Comparisons
#     peer_comparison: Optional[Dict[str, Any]] = Field(None, description="Comparison with similar households")
#     historical_comparison: Optional[Dict[str, Any]] = Field(None, description="Historical trends")
    
#     # Environmental impact
#     carbon_footprint: Dict[str, Any] = Field(..., description="Carbon footprint analysis")
    
#     # Cost optimization
#     cost_saving_opportunities: List[Dict[str, Any]] = Field(..., description="Cost saving opportunities")
    
#     # Anomalies
#     anomalies: Optional[List[Dict[str, Any]]] = Field(None, description="Detected anomalies")
    
#     # Predictions
#     next_month_prediction: Optional[Dict[str, Any]] = Field(None, description="Next month's prediction")


# class RecommendationItem(BaseModel):
#     """Individual recommendation item"""
#     id: str = Field(..., description="Unique recommendation ID")
#     category: str = Field(..., description="Category: efficiency, behavioral, upgrade, etc.")
#     priority: str = Field(..., description="Priority: high, medium, low")
#     title: str = Field(..., description="Recommendation title")
#     description: str = Field(..., description="Detailed description")
#     potential_savings_kwh: Optional[float] = Field(None, description="Potential kWh savings")
#     potential_savings_inr: Optional[float] = Field(None, description="Potential INR savings")
#     implementation_cost: Optional[float] = Field(None, description="Implementation cost if any")
#     payback_period_months: Optional[float] = Field(None, description="Payback period in months")
#     difficulty_level: str = Field(..., description="Implementation difficulty: easy, medium, hard")
#     action_items: List[str] = Field(..., description="Step-by-step action items")
    
#     @field_validator('priority')
#     @classmethod
#     def validate_priority(cls, v: str) -> str:
#         """Validate priority level"""
#         allowed = ['high', 'medium', 'low']
#         if v.lower() not in allowed:
#             raise ValueError(f'Priority must be one of {allowed}')
#         return v.lower()
    
#     @field_validator('difficulty_level')
#     @classmethod
#     def validate_difficulty(cls, v: str) -> str:
#         """Validate difficulty level"""
#         allowed = ['easy', 'medium', 'hard']
#         if v.lower() not in allowed:
#             raise ValueError(f'Difficulty must be one of {allowed}')
#         return v.lower()


# class InsightResponse(InsightBase):
#     """Schema for insight response"""
#     id: uuid.UUID
#     bill_id: uuid.UUID
#     user_id: uuid.UUID
#     structured_data: Dict[str, Any]
#     generated_at: datetime
    
#     # Metadata
#     version: Optional[str] = Field(None, description="Insight generation version")
#     processing_time_seconds: Optional[float] = Field(None, description="Processing time")
#     confidence_score: Optional[float] = Field(None, description="Overall confidence score")
    
#     model_config = ConfigDict(from_attributes=True)


# class InsightSummaryResponse(BaseModel):
#     """Summary insight for quick display"""
#     id: uuid.UUID
#     bill_id: uuid.UUID
#     status: InsightStatus
#     generated_at: datetime
    
#     # Key metrics
#     total_recommendations: int = Field(..., description="Total number of recommendations")
#     high_priority_recommendations: int = Field(..., description="Number of high priority recommendations")
#     potential_monthly_savings: float = Field(..., description="Total potential monthly savings in INR")
#     carbon_reduction_kg: float = Field(..., description="Potential carbon reduction in kg")
    
#     # Top recommendation
#     top_recommendation: Optional[RecommendationItem] = Field(None, description="Top recommendation")
    
#     model_config = ConfigDict(from_attributes=True)


# class InsightDetailResponse(InsightResponse):
#     """Detailed insight response with all related data"""
#     from src.app.schemas.bill_schema import BillSummaryResponse
    
#     bill: BillSummaryResponse = Field(..., description="Associated bill information")
    
#     # Enhanced structured data with proper typing
#     structured_insights: InsightStructuredData = Field(..., description="Properly structured insights")
    
#     # Interactive elements
#     action_plan: Optional[List[Dict[str, Any]]] = Field(None, description="Personalized action plan")
#     savings_calculator: Optional[Dict[str, Any]] = Field(None, description="Interactive savings calculator data")


# class InsightListResponse(PaginatedResponse):
#     """Paginated insight list response"""
#     items: List[InsightSummaryResponse]


# class InsightAnalyticsResponse(BaseModel):
#     """Analytics dashboard for insights"""
#     total_insights_generated: int
#     average_recommendations_per_insight: float
#     total_potential_savings: float
#     total_carbon_reduction: float
    
#     # Adoption metrics
#     recommendations_implemented: int
#     recommendations_pending: int
#     implementation_rate: float
    
#     # Trends
#     monthly_trend: List[Dict[str, Any]]
#     category_breakdown: Dict[str, int]
#     savings_achieved: Optional[float] = None


# class InsightFeedbackRequest(BaseModel):
#     """User feedback on insights"""
#     insight_id: uuid.UUID
#     helpful: bool = Field(..., description="Was this insight helpful?")
#     implemented_recommendations: Optional[List[str]] = Field(None, description="IDs of implemented recommendations")
#     feedback_text: Optional[str] = Field(None, max_length=1000, description="Additional feedback")
#     rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5")


# class InsightRegenerateRequest(BaseModel):
#     """Request to regenerate insights"""
#     bill_id: uuid.UUID
#     force_regenerate: bool = Field(default=False, description="Force regeneration even if exists")
#     include_historical: bool = Field(default=True, description="Include historical data in analysis")
#     advanced_mode: bool = Field(default=False, description="Use advanced AI analysis")