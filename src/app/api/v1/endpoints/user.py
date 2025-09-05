import logging

from typing import Dict
from fastapi import APIRouter, Depends, status, Query

from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.config import settings
from src.app.schemas.user_schema import UserResponse, UserUpdate
from src.app.schemas.auth_schema import UserPasswordChange
from src.app.models.user_model import User
from src.app.db.session import get_session
from src.app.schemas.bill_schema import BillUserListResponse, BillSearchParams
from src.app.utils.deps import (
    get_current_verified_user,
    rate_limit_api,
    require_user,
    PaginationParams,
    get_pagination_params,
    rate_limit_auth,
)
from src.app.services.user_service import user_service
from src.app.services.auth_service import auth_service
from src.app.services.bill_service import bill_service

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["User"],
    prefix=f"{settings.API_V1_STR}/users",
)


# ------ Current User Operations ------
@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get profile information for the authenticated user",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def get_my_profile(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    return current_user


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Update current user profile",
    description="Update profile information for the authenticated user",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def update_my_profile(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    user_data: UserUpdate,
):
    updated_user = await user_service.update_user(
        db=db,
        user_id_to_update=current_user.id,
        user_data=user_data,
        current_user=current_user,
    )

    return updated_user


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Deactivate current user profile",
    description="Deactivate profile for the authenticated user",
    dependencies=[Depends(rate_limit_auth), Depends(require_user)],
)
async def deactivate_my_account(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """
    Deactivate a user account.

    - Users can deactivate their own account
    - Admins can deactivate any user account
    - The last admin account cannot be deactivated
    """
    user_to_deactivate = await user_service.deactivate_user(
        db=db, user_id_to_deactivate=current_user.id, current_user=current_user
    )

    return user_to_deactivate


@router.post(
    "/change-password",
    response_model=Dict[str, str],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Change Current User's Password",
    description="Change Current User's Password",
    dependencies=[Depends(rate_limit_auth), Depends(require_user)],
)
async def change_my_password(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    password_data: UserPasswordChange,
):
    """Change a logged-in User Password"""
    await auth_service.change_password(
        db=db, password_data=password_data, user=current_user
    )

    return {"message": "Password updated successfully"}


@router.get(
    "/me/bills",
    response_model=BillUserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List my bills",
    description="Get a paginated and filterable list of my bills.",
    dependencies=[
        Depends(require_user),
        Depends(rate_limit_api),
    ],  # Simplified the auth check)
)
async def get_my_bills(
    *,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_session),
    pagination: PaginationParams = Depends(get_pagination_params),
    search_params: BillSearchParams = Depends(BillSearchParams),
    order_by: str = Query("created_at", description="Field to order by"),
    order_desc: bool = Query(True, description="Order descending"),
):
    """get paginated response of current_user bills"""

    return await bill_service.get_my_bills(
        db=db,
        user_id=current_user.id,
        skip=pagination.skip,
        limit=pagination.limit,
        order_by=order_by,
        order_desc=order_desc,
        filters=search_params.model_dump(exclude_none=True),
    )
