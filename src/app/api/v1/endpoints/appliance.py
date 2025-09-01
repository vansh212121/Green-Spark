import logging
import uuid
from typing import Dict, List
from fastapi import APIRouter, Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.db.session import get_session
from src.app.models.user_model import User
from src.app.services.appliance_service import appliance_service
from src.app.schemas.appliance_schema import (
    UserApplianceCreate,
    UserApplianceDetailedResponse,
    ApplianceEstimateResponse,
    UserApplianceListResponse,
    UserApplianceUpdate,
    ApplianceCatalogResponse,
    UserApplianceResponse,
)
from src.app.utils.deps import (
    get_current_verified_user,
    get_pagination_params,
    PaginationParams,
    require_user,
    require_admin,
    rate_limit_api,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Appliance"],
    prefix="/appliances",
)


@router.get(
    "/catalog",
    status_code=status.HTTP_200_OK,
    response_model=List[ApplianceCatalogResponse],
    summary="get all catalogs",
    description="get all catalogs",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def get_all_catalogs(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """get a list of all  catalogs"""

    return await appliance_service.get_appliance_catalog(
        db=db,
    )


@router.get(
    "/{appliance_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserApplianceDetailedResponse,
    summary="Get appliance by id",
    description="Get all information for the appliance by id",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def get_appliance_by_id(
    *,
    appliance_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """Get appliance by it's ID"""

    return await appliance_service.get_appliance_by_id(
        db=db, appliance_id=appliance_id, current_user=current_user
    )


@router.get(
    "/{bill_id}/appliances",
    response_model=UserApplianceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all appliances",
    description="Get a paginated and filterable list of all appliances by a bill_id.",
    dependencies=[
        Depends(require_user),
        Depends(rate_limit_api),
    ],
)
async def get_all_appliances(
    *,
    bill_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_session),
    pagination: PaginationParams = Depends(get_pagination_params),
    order_by: str = Query("created_at", description="Field to order by"),
    order_desc: bool = Query(True, description="Order descending"),
):
    """Get all Appliances with pagination and filtering support"""
    return await appliance_service.get_bill_appliances(
        bill_id=bill_id,
        user_id=current_user.id,
        db=db,
        order_by=order_by,
        order_desc=order_desc,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/{bill_id}/create",
    status_code=status.HTTP_201_CREATED,
    response_model=UserApplianceResponse,
    summary="create appliance",
    description="create an applaince",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def create_appliance(
    *,
    bill_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    appliance_data: UserApplianceCreate,
    current_user: User = Depends(get_current_verified_user),
):
    """create an application"""

    return await appliance_service.create_appliance(
        db=db, bill_id=bill_id, appliance_in=appliance_data, current_user=current_user
    )


@router.patch(
    "/{bill_id}/{appliance_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserApplianceResponse,
    summary="update appliance",
    description="update an applaince by it's bill_id",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def update_appliance(
    *,
    bill_id: uuid.UUID,
    appliance_id: str,
    db: AsyncSession = Depends(get_session),
    appliance_data: UserApplianceUpdate,
    current_user: User = Depends(get_current_verified_user),
):
    """update an appliance by it's ID"""

    return await appliance_service.update_appliance(
        db=db,
        appliance_id=appliance_id,
        appliance_data=appliance_data,
        current_user=current_user,
        bill_id=bill_id,
    )


@router.delete(
    "/{bill_id}/{appliance_id}",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str],
    summary="delete appliance",
    description="delete an applaince by it's bill_id",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def delete_appliance(
    *,
    bill_id: uuid.UUID,
    appliance_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """Delete an appliance by it's ID"""

    await appliance_service.delete_appliance(
        db=db, bill_id=bill_id, appliance_id=appliance_id, current_user=current_user
    )

    return {"message": "Appliance deleted successfully"}


@router.get(
    "/estimates/{bill_id}",
    response_model=List[ApplianceEstimateResponse],
    status_code=status.HTTP_200_OK,
    summary="get all estimates",
    description="get all applaince_estimates by it's bill_id",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def get_estimates(
    *,
    bill_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """get all appliance estimates"""

    return await appliance_service.get_all_estimates(
        db=db, current_user=current_user, bill_id=bill_id
    )
