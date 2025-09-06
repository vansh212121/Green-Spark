import logging
import uuid
from typing import Dict

from fastapi import APIRouter, Depends, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.config import settings
from src.app.db.session import get_session
from src.app.utils.deps import (
    get_current_verified_user,
    get_pagination_params,
    rate_limit_api,
    require_admin,
    PaginationParams,
)
from src.app.schemas.appliance_schema import (
    UserApplianceListResponse,
    ApplianceCatalogResponse,
    ApplianceCatalogCreate,
)
from src.app.services.appliance_service import appliance_service
from src.app.schemas.user_schema import (
    UserResponse,
    UserListResponse,
    UserSearchParams,
)
from src.app.models.user_model import User, UserRole
from src.app.services.user_service import user_service

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Admin"],
    prefix=f"{settings.API_V1_STR}/admin",
)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Get user by id",
    description="Get all information for the user by id (moderators and admin only)",
    dependencies=[Depends(rate_limit_api), Depends(require_admin)],
)
async def get_user_by_id(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
):
    """Get User's profile by it's ID (Admin only)"""

    return await user_service.get_user_by_id(
        db=db, user_id=user_id, current_user=current_user
    )


@router.post(
    "/{user_id}/change-role",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Change user role",
    description="Change a user's role (admin only)",
    dependencies=[Depends(require_admin), Depends(rate_limit_api)],
)
async def change_user_role(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    user_id: uuid.UUID,
    new_role: UserRole = Query(..., description="New role for the user"),
):
    """
    Change a user's role.

    **Admin access required.**

    Available roles:
    - USER: Standard user
    - ADMIN: System administrator
    """

    updated_user = await user_service.change_role(
        db=db, user_id_to_change=user_id, current_user=current_user, new_role=new_role
    )

    logger.info(
        f"User role changed",
        extra={
            "user_id": user_id,
            "new_role": new_role.value,
            "changed_by": current_user.id,
        },
    )

    return updated_user


@router.post(
    "/{user_id}/activate",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str],
    summary="Activate a users account",
    description="Activate a user's account using his id(Admins only).",
    dependencies=[Depends(require_admin), Depends(rate_limit_api)],
)
async def activate_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
):
    """
    Deactivate a user account.

    - Users can deactivate their own account
    - Admins can deactivate any user account
    - The last admin account cannot be deactivated
    """

    user_to_activate = await user_service.activate_user(
        db=db, user_id_to_activate=user_id, current_user=current_user
    )

    logger.info(
        f"User activated", extra={"user_id": user_id, "activated_by": current_user.id}
    )

    return {"message": f"{user_to_activate.first_name}'s Account has been Activated."}


@router.post(
    "/{user_id}/deactivate",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str],
    summary="Deactivate user by id",
    description="Deactivate user profile by id",
    dependencies=[Depends(rate_limit_api), Depends(require_admin)],
)
async def deactivate_user(
    db: AsyncSession = Depends(get_session),
    *,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
):
    """
    Deactivate a user account.

    - Users can deactivate their own account
    - Admins can deactivate any user account
    - The last admin account cannot be deactivated
    """
    user_to_deactivate = await user_service.deactivate_user(
        db=db, user_id_to_deactivate=user_id, current_user=current_user
    )

    return {
        "message": f"{user_to_deactivate.first_name}'s Account has been Deactivated."
    }


@router.delete(
    "/{user_id}/delete",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str],
    summary="Delete user by id",
    description="Delete user profile by id",
    dependencies=[Depends(rate_limit_api), Depends(require_admin)],
)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
):
    """
    Delete a user account.

    - Users can Delete their own account
    - Admins can Delete any user account
    - The last admin account cannot be Deleted
    """
    await user_service.delete_user(
        db=db, user_id_to_delete=user_id, current_user=current_user
    )

    return {"message": "User deleted succesfully."}


@router.get(
    "/users/all",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all users",
    description="Get a paginated and filterable list of all users (Admins only).",
    dependencies=[
        Depends(require_admin),
        Depends(rate_limit_api),
    ],  # Simplified the auth check
)
async def get_all_users(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    pagination: PaginationParams = Depends(get_pagination_params),
    search_params: UserSearchParams = Depends(UserSearchParams),
    order_by: str = Query("created_at", description="Field to order by"),
    order_desc: bool = Query(True, description="Order descending"),
):
    """Get all User's with pagination and filtering support"""

    return await user_service.get_users(
        db=db,
        current_user=current_user,
        skip=pagination.skip,
        limit=pagination.limit,
        filters=search_params.model_dump(exclude_none=True),
        order_by=order_by,
        order_desc=order_desc,
    )


# ============Appliances and Catalogs===========
@router.get(
    "/{user_id}/appliances",
    response_model=UserApplianceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all appliances",
    description="Get a paginated and filterable list of all appliances by a bill_id.(admin only)",
    dependencies=[
        Depends(require_admin),
        Depends(rate_limit_api),
    ],
)
async def get_all_appliances_by_user(
    *,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_session),
    pagination: PaginationParams = Depends(get_pagination_params),
    order_by: str = Query("created_at", description="Field to order by"),
    order_desc: bool = Query(True, description="Order descending"),
):
    """Get all Appliances with pagination and filtering support"""
    return await appliance_service.get_user_appliances(
        user_id=user_id,
        db=db,
        order_by=order_by,
        order_desc=order_desc,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/catalog",
    response_model=ApplianceCatalogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="create a catalog",
    description="Create a catalog (Admins only).",
    dependencies=[
        Depends(require_admin),
        Depends(rate_limit_api),
    ],
)
async def create_catalog(
    *,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
    catalog: ApplianceCatalogCreate,
):
    """create a catalog"""

    return await appliance_service.create_catalog(
        db=db, current_user=current_user, catalog_in=catalog
    )


@router.delete(
    "/{catalog_id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="delete a catalog",
    description="delete a catalog by it's ID(Admins only).",
    dependencies=[
        Depends(require_admin),
        Depends(rate_limit_api),
    ],
)
async def delete_catalog(
    *,
    catalog_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """Delete a catalog by it's ID"""

    await appliance_service.delete_catalog(
        db=db, current_user=current_user, catalog_id=catalog_id
    )

    return {"message": "Catalog deleted successfully"}
