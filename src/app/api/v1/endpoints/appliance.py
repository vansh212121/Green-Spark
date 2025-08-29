# app/api/v1/endpoints/appliance_router.py
"""
Appliance Router - API Layer
Handles HTTP requests/responses for appliance management
Production-ready implementation with comprehensive error handling and documentation
"""

from typing import Optional, List, Dict, Any
from datetime import date
import uuid
import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    Path,
    Body,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.database import get_session
from src.app.core.auth import get_current_user, require_admin
from src.app.core.exceptions import (
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    BusinessLogicError,
    DatabaseError,
    ConflictError,
)
from src.app.models.user_model import User
from src.app.services.appliance_service import ApplianceService
from src.app.schemas.appliance_schemas import (
    UserApplianceCreate,
    UserApplianceUpdate,
    UserApplianceResponse,
    UserApplianceDetailedResponse,
    UserApplianceListResponse,
    UserApplianceSearchParams,
    ApplianceEstimateResponse,
)
from src.app.models.appliance_model import ApplianceCatalog
from src.app.core.rate_limiter import RateLimiter
from src.app.core.monitoring import track_request_duration, increment_counter

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/appliances",
    tags=["Appliances"],
    responses={
        401: {"description": "Unauthorized - Authentication required"},
        403: {"description": "Forbidden - Insufficient permissions"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        429: {"description": "Too many requests"},
        500: {"description": "Internal server error"},
    },
)

# Rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


# ==================== DEPENDENCIES ====================


async def get_appliance_service(
    session: AsyncSession = Depends(get_session),
) -> ApplianceService:
    """
    Dependency to get appliance service instance.

    Args:
        session: Database session from dependency

    Returns:
        ApplianceService instance
    """
    return ApplianceService(session)


async def validate_appliance_id(
    appliance_id: uuid.UUID = Path(..., description="Appliance UUID")
) -> uuid.UUID:
    """
    Validate and return appliance ID from path parameter.

    Args:
        appliance_id: UUID from path

    Returns:
        Validated UUID

    Raises:
        HTTPException: If UUID is invalid
    """
    try:
        return appliance_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid appliance ID format",
        )


# ==================== CATALOG ENDPOINTS ====================


@router.get(
    "/catalog",
    response_model=List[ApplianceCatalog],
    summary="Get appliance catalog",
    description="Retrieve list of available appliance types from the catalog",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "category_id": "refrigerator_standard",
                            "label": "Refrigerator (Standard)",
                            "icon_emoji": "🧊",
                            "typical_wattage": 150,
                        }
                    ]
                }
            },
        }
    },
)
@track_request_duration("get_appliance_catalog")
async def get_appliance_catalog(
    search: Optional[str] = Query(
        None,
        min_length=1,
        max_length=100,
        description="Search term for filtering catalog items",
    ),
    service: ApplianceService = Depends(get_appliance_service),
    _: User = Depends(get_current_user),
) -> List[ApplianceCatalog]:
    """
    Get available appliance types from the catalog.

    This endpoint returns a list of predefined appliance types that users
    can select when creating their appliances. Each item includes typical
    wattage values for energy estimation.
    """
    try:
        increment_counter("appliance_catalog_requests")
        catalog_items = await service.get_catalog(search=search)
        logger.info(f"Retrieved {len(catalog_items)} catalog items")
        return catalog_items
    except Exception as e:
        logger.error(f"Error retrieving catalog: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appliance catalog",
        )


# ==================== CREATE ENDPOINTS ====================


@router.post(
    "/",
    response_model=UserApplianceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new appliance",
    description="Add a new appliance to user's inventory",
    responses={
        201: {"description": "Appliance created successfully"},
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict - Duplicate or limit exceeded"},
    },
)
@track_request_duration("create_appliance")
@rate_limiter.limit("10/minute")
async def create_appliance(
    appliance_data: UserApplianceCreate = Body(
        ...,
        example={
            "appliance_catalog_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "custom_name": "Kitchen Refrigerator",
            "custom_wattage": 150,
            "hours_per_day": 24,
            "days_per_week": 7,
            "brand": "Samsung",
            "model": "RF28R7351SR",
            "star_rating": 4,
            "purchase_year": 2022,
            "notes": "Energy Star certified model",
        },
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> UserApplianceResponse:
    """
    Create a new appliance in the user's inventory.

    The user must either:
    - Select an appliance type from the catalog (appliance_catalog_id)
    - OR provide custom wattage for custom appliances

    Returns the created appliance with generated ID and timestamps.
    """
    try:
        increment_counter("appliances_created")

        # Create appliance through service
        appliance = await service.create_appliance(
            user=current_user, appliance_data=appliance_data
        )

        # Schedule background task for analytics
        background_tasks.add_task(
            log_appliance_creation, user_id=current_user.id, appliance_id=appliance.id
        )

        logger.info(f"User {current_user.id} created appliance {appliance.id}")
        return appliance

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating appliance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create appliance",
        )


@router.post(
    "/bulk",
    response_model=List[UserApplianceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple appliances",
    description="Add multiple appliances to user's inventory in a single request",
)
@track_request_duration("create_appliances_bulk")
@rate_limiter.limit("5/minute")
async def create_appliances_bulk(
    appliances_data: List[UserApplianceCreate] = Body(
        ...,
        min_items=1,
        max_items=20,
        description="List of appliances to create (max 20)",
    ),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> List[UserApplianceResponse]:
    """
    Create multiple appliances in a single request.

    Useful for initial setup or importing appliances.
    Maximum 20 appliances per request to prevent abuse.
    """
    try:
        appliances = await service.create_multiple_appliances(
            user=current_user, appliances_data=appliances_data
        )

        increment_counter("appliances_bulk_created", len(appliances))
        logger.info(
            f"User {current_user.id} created {len(appliances)} appliances in bulk"
        )
        return appliances

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error in bulk creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create appliances",
        )


# ==================== READ ENDPOINTS ====================


@router.get(
    "/my",
    response_model=List[UserApplianceResponse],
    summary="Get my appliances",
    description="Retrieve all appliances for the current user",
)
@track_request_duration("get_my_appliances")
async def get_my_appliances(
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> List[UserApplianceResponse]:
    """
    Get all appliances owned by the current user.

    Returns a list of all appliances with their details.
    Results are sorted by creation date (newest first).
    """
    try:
        appliances = await service.get_user_appliances(user=current_user)
        return appliances
    except Exception as e:
        logger.error(f"Error retrieving user appliances: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appliances",
        )


@router.get(
    "/list",
    response_model=UserApplianceListResponse,
    summary="List appliances with pagination",
    description="Get paginated list of appliances with optional filtering",
)
@track_request_duration("list_appliances")
async def list_appliances(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(
        None, min_length=1, max_length=100, description="Search term"
    ),
    appliance_catalog_id: Optional[uuid.UUID] = Query(
        None, description="Filter by catalog ID"
    ),
    created_after: Optional[date] = Query(
        None, description="Filter by creation date (after)"
    ),
    created_before: Optional[date] = Query(
        None, description="Filter by creation date (before)"
    ),
    sort_by: str = Query(
        "created_at", regex="^(custom_name|brand|created_at|updated_at)$"
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> UserApplianceListResponse:
    """
    Get paginated list of appliances with advanced filtering options.

    Features:
    - Pagination with configurable page size
    - Text search in name, brand, and model
    - Filter by appliance type
    - Filter by date range
    - Sorting by multiple fields
    """
    try:
        # Build search parameters
        search_params = None
        if any([search, appliance_catalog_id, created_after, created_before]):
            search_params = UserApplianceSearchParams(
                search=search,
                appliance_catalog_id=appliance_catalog_id,
                created_after=created_after,
                created_before=created_before,
            )

        result = await service.list_appliances(
            user=current_user,
            page=page,
            page_size=page_size,
            search_params=search_params,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return result

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error listing appliances: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list appliances",
        )


@router.get(
    "/statistics",
    response_model=Dict[str, Any],
    summary="Get appliance statistics",
    description="Get aggregated statistics for user's appliances",
)
@track_request_duration("get_appliance_statistics")
async def get_appliance_statistics(
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get comprehensive statistics about user's appliances.

    Includes:
    - Total counts and energy consumption
    - Cost estimates
    - Brand distribution
    - Energy-saving recommendations
    """
    try:
        stats = await service.get_appliance_statistics(user=current_user)
        return stats
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate statistics",
        )


@router.get(
    "/{appliance_id}",
    response_model=UserApplianceDetailedResponse,
    summary="Get appliance details",
    description="Retrieve detailed information for a specific appliance",
)
@track_request_duration("get_appliance")
async def get_appliance(
    appliance_id: uuid.UUID = Depends(validate_appliance_id),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> UserApplianceDetailedResponse:
    """
    Get detailed information for a specific appliance.

    Includes all appliance data plus calculated fields like
    energy consumption estimates and costs.
    """
    try:
        appliance = await service.get_appliance(
            user=current_user, appliance_id=appliance_id
        )
        return appliance

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving appliance {appliance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appliance",
        )


# ==================== UPDATE ENDPOINTS ====================


@router.put(
    "/{appliance_id}",
    response_model=UserApplianceResponse,
    summary="Update appliance",
    description="Update an existing appliance's information",
)
@track_request_duration("update_appliance")
@rate_limiter.limit("30/minute")
async def update_appliance(
    appliance_id: uuid.UUID = Depends(validate_appliance_id),
    update_data: UserApplianceUpdate = Body(
        ...,
        example={
            "custom_name": "Updated Refrigerator Name",
            "hours_per_day": 20,
            "notes": "Moved to garage",
        },
    ),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> UserApplianceResponse:
    """
    Update an existing appliance.

    All fields are optional - only provided fields will be updated.
    User can only update their own appliances unless they are an admin.
    """
    try:
        updated_appliance = await service.update_appliance(
            user=current_user, appliance_id=appliance_id, update_data=update_data
        )

        increment_counter("appliances_updated")
        logger.info(f"User {current_user.id} updated appliance {appliance_id}")
        return updated_appliance

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating appliance {appliance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update appliance",
        )


@router.patch(
    "/bulk/update",
    response_model=Dict[str, Any],
    summary="Bulk update appliances",
    description="Update multiple appliances with the same changes",
)
@track_request_duration("bulk_update_appliances")
@rate_limiter.limit("10/minute")
async def bulk_update_appliances(
    appliance_ids: List[uuid.UUID] = Body(
        ..., min_items=1, max_items=50, description="List of appliance IDs to update"
    ),
    update_data: UserApplianceUpdate = Body(..., description="Updates to apply"),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Update multiple appliances with the same changes.

    Useful for bulk operations like changing usage patterns
    for multiple appliances at once.
    """
    try:
        result = await service.bulk_update_appliances(
            user=current_user, appliance_ids=appliance_ids, update_data=update_data
        )

        increment_counter("appliances_bulk_updated", result["updated_count"])
        return result

    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update appliances",
        )


# ==================== DELETE ENDPOINTS ====================


@router.delete(
    "/{appliance_id}",
    response_model=Dict[str, Any],
    summary="Delete appliance",
    description="Remove an appliance from inventory",
)
@track_request_duration("delete_appliance")
@rate_limiter.limit("20/minute")
async def delete_appliance(
    appliance_id: uuid.UUID = Depends(validate_appliance_id),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Delete an appliance from the user's inventory.

    This action is permanent and cannot be undone.
    All associated data will be removed.
    """
    try:
        result = await service.delete_appliance(
            user=current_user, appliance_id=appliance_id
        )

        increment_counter("appliances_deleted")
        logger.info(f"User {current_user.id} deleted appliance {appliance_id}")
        return result

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting appliance {appliance_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete appliance",
        )


@router.delete(
    "/bulk/delete",
    response_model=Dict[str, Any],
    summary="Bulk delete appliances",
    description="Delete multiple appliances at once",
)
@track_request_duration("bulk_delete_appliances")
@rate_limiter.limit("10/minute")
async def bulk_delete_appliances(
    appliance_ids: List[uuid.UUID] = Body(
        ..., min_items=1, max_items=50, description="List of appliance IDs to delete"
    ),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Delete multiple appliances in a single request.

    Useful for cleaning up multiple appliances at once.
    This action is permanent for all selected appliances.
    """
    try:
        result = await service.bulk_delete_appliances(
            user=current_user, appliance_ids=appliance_ids
        )

        increment_counter("appliances_bulk_deleted", result["deleted_count"])
        return result

    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error in bulk delete: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete appliances",
        )


# ==================== ENERGY ESTIMATION ENDPOINTS ====================


@router.get(
    "/{appliance_id}/consumption",
    response_model=Dict[str, Any],
    summary="Estimate appliance consumption",
    description="Get energy consumption estimates for an appliance",
)
@track_request_duration("estimate_consumption")
async def estimate_appliance_consumption(
    appliance_id: uuid.UUID = Depends(validate_appliance_id),
    electricity_rate: Optional[float] = Query(
        None,
        gt=0,
        le=1.0,
        description="Electricity rate per kWh (default: system setting)",
    ),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Calculate energy consumption and cost estimates for an appliance.

    Returns daily, monthly, and annual consumption in kWh and
    estimated costs based on the electricity rate.
    """
    try:
        estimates = await service.estimate_appliance_consumption(
            user=current_user,
            appliance_id=appliance_id,
            electricity_rate=electricity_rate,
        )
        return estimates

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Error estimating consumption: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to estimate consumption",
        )


@router.post(
    "/estimate-bill",
    response_model=List[ApplianceEstimateResponse],
    summary="Estimate bill distribution",
    description="Estimate each appliance's contribution to electricity bill",
)
@track_request_duration("estimate_bill_impact")
async def estimate_bill_impact(
    bill_amount: float = Body(..., gt=0, description="Total bill amount"),
    billing_days: int = Body(
        30, ge=1, le=365, description="Number of days in billing period"
    ),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> List[ApplianceEstimateResponse]:
    """
    Estimate how much each appliance contributes to the electricity bill.

    This helps users understand which appliances are consuming
    the most energy and costing the most money.
    """
    try:
        estimates = await service.estimate_bill_impact(
            user=current_user, bill_amount=bill_amount, billing_days=billing_days
        )

        increment_counter("bill_estimates_calculated")
        return estimates

    except Exception as e:
        logger.error(f"Error estimating bill impact: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to estimate bill impact",
        )


# ==================== ADMIN ENDPOINTS ====================


@router.get(
    "/admin/all",
    response_model=UserApplianceListResponse,
    summary="[Admin] Get all appliances",
    description="Admin endpoint to retrieve all appliances across all users",
    dependencies=[Depends(require_admin)],
)
@track_request_duration("admin_get_all_appliances")
async def admin_get_all_appliances(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> UserApplianceListResponse:
    """
    Admin-only endpoint to view all appliances in the system.

    Useful for system monitoring and support.
    """
    try:
        result = await service.admin_get_all_appliances(
            user=current_user, page=page, page_size=page_size
        )
        return result

    except Exception as e:
        logger.error(f"Error in admin get all appliances: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appliances",
        )


@router.get(
    "/admin/statistics",
    response_model=Dict[str, Any],
    summary="[Admin] Get system statistics",
    description="Admin endpoint to get system-wide appliance statistics",
    dependencies=[Depends(require_admin)],
)
@track_request_duration("admin_get_statistics")
async def admin_get_system_statistics(
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Admin-only endpoint to view system-wide statistics.

    Includes aggregate data across all users for system monitoring.
    """
    try:
        stats = await service.admin_get_system_statistics(user=current_user)
        return stats

    except Exception as e:
        logger.error(f"Error generating admin statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate statistics",
        )


@router.get(
    "/admin/user/{user_id}/appliances",
    response_model=List[UserApplianceResponse],
    summary="[Admin] Get user's appliances",
    description="Admin endpoint to view a specific user's appliances",
    dependencies=[Depends(require_admin)],
)
@track_request_duration("admin_get_user_appliances")
async def admin_get_user_appliances(
    user_id: uuid.UUID = Path(..., description="Target user ID"),
    service: ApplianceService = Depends(get_appliance_service),
    current_user: User = Depends(get_current_user),
) -> List[UserApplianceResponse]:
    """
    Admin-only endpoint to view appliances for a specific user.

    Useful for support and troubleshooting.
    """
    try:
        appliances = await service.get_user_appliances(
            user=current_user, target_user_id=user_id
        )
        return appliances

    except Exception as e:
        logger.error(f"Error retrieving user {user_id} appliances: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user appliances",
        )


# ==================== HEALTH CHECK ====================


@router.get(
    "/health",
    response_model=Dict[str, str],
    summary="Health check",
    description="Check if the appliance service is operational",
    include_in_schema=False,
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "appliance-management",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ==================== BACKGROUND TASKS ====================


async def log_appliance_creation(user_id: uuid.UUID, appliance_id: uuid.UUID):
    """
    Background task to log appliance creation for analytics.

    Args:
        user_id: ID of the user who created the appliance
        appliance_id: ID of the created appliance
    """
    try:
        # Log to analytics service
        logger.info(f"Analytics: User {user_id} created appliance {appliance_id}")
        # Could send to external analytics service here
    except Exception as e:
        logger.error(f"Failed to log analytics: {str(e)}")


# ==================== ERROR HANDLERS ====================


@router.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    """Handle validation errors with proper response."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc), "type": "validation_error"},
    )


@router.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc: NotFoundError):
    """Handle not found errors."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "type": "not_found"},
    )


@router.exception_handler(ForbiddenError)
async def forbidden_error_handler(request, exc: ForbiddenError):
    """Handle forbidden access errors."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc), "type": "forbidden"},
    )


# ==================== ROUTER CONFIGURATION ====================


def configure_router():
    """
    Configure router with middleware and additional settings.
    Called during app initialization.
    """
    logger.info("Appliance router configured successfully")
    return router


# Export configured router
appliance_router = configure_router()
