# app/services/appliance_service.py
"""
Appliance service module.

This module provides the business logic layer for appliance operations,
handling authorization, validation, and orchestrating repository calls.
"""
import uuid
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.crud.appliance_crud import appliance_repository
from src.app.crud.user_crud import user_repository
from src.app.models.appliance_model import ApplianceCatalog, UserAppliance
from src.app.models.user_model import User, UserRole
from src.app.schemas.appliance_schema import (
    UserApplianceDetailedResponse,
    UserApplianceListResponse,
    UserApplianceCreate,
    UserApplianceUpdate,
)
from src.app.core.exception_utils import raise_for_status
from src.app.services.cache_service import cache_service
from src.app.core.exceptions import (
    ResourceNotFound,
    NotAuthorized,
    ResourceAlreadyExists,
    ValidationError,
)


logger = logging.getLogger(__name__)


class ApplianceService:
    """Handles all bill-related business logic."""

    def __init__(self):
        """
        Initializes the ApplianceService.
        This version has no arguments, making it easy for FastAPI to use,
        while still allowing for dependency injection during tests.
        """
        self.appliance_repository = appliance_repository
        self.user_repository = user_repository
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _check_authorization(
        self, *, current_user: User, appliance: UserAppliance, action: str
    ) -> None:
        """
        Central authorization check. An admin can do anything.
        A non-admin can only perform actions on their own account.

        Args:
            current_user: The user performing the action
            target_user: The user being acted upon
            action: Description of the action for error messages

        Raises:
            NotAuthorized: If user lacks permission for the action
        """

        # Admins have super powers
        if current_user.is_admin:
            return

        # Users can only modify their own account
        is_not_self = str(current_user.id) != str(appliance.user_id)
        raise_for_status(
            condition=is_not_self,
            exception=NotAuthorized,
            detail=f"You are not authorized to {action} this user.",
        )

    async def _load_bill_schema_from_db(
        self, *, db: AsyncSession, appliance_id: uuid.UUID
    ) -> Optional[UserApplianceDetailedResponse]:
        """Private helper to load a appliance from the DB and convert it to a Pydantic schema.
        This is our "loader" function for the cache."""

        appliance_model = await self.appliance_repository.get(
            db=db, obj_id=appliance_id
        )
        raise_for_status(
            condition=appliance_model is None,
            exception=ResourceNotFound,
            detail=f"Appliance with {appliance_id} not Found.",
            resource_type="Appliance",
        )
        return UserApplianceDetailedResponse.model_validate(appliance_model)

    async def get_appliance_by_id(
        self, db: AsyncSession, *, current_user: User, appliance_id: uuid.UUID
    ) -> Optional[UserAppliance]:
        """Retrieve appliance by it's ID"""

        appliance = await cache_service.get_or_set(
            schema_type=UserApplianceDetailedResponse,
            obj_id=appliance_id,
            loader=lambda: self._load_bill_schema_from_db(
                db=db, appliance_id=appliance_id
            ),
            ttl=300,  # Cache for 5 minutes
        )

        # Fine-grained authorization check
        if current_user.is_admin:
            return appliance_id
        is_not_self = current_user.id != appliance.user_id

        raise_for_status(
            condition=(is_not_self),
            exception=NotAuthorized,
            detail="You are not authorized to view this appliance.",
        )

        self._logger.debug(
            f"Appliance {appliance_id} retrieved by user {current_user.id}"
        )
        return appliance

    async def get_user_appliances(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> UserApplianceListResponse:
        """
        Lists appliances with pagination and filtering.

        Args:
            db: Database session
            current_user: User making the request
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            order_by: Field to order by
            order_desc: Whether to order in descending order

        Returns:
            UserApplianceListResponse: Paginated list of users

        Raises:
            NotAuthorized: If user lacks permission to list users
            ValidationError: If pagination parameters are invalid
        """
        # Authorization check: admins can list all users
        user = await self.appliance_repository.get(db=db, obj_id=user_id)

        raise_for_status(
            condition=(user.role < UserRole.ADMIN),
            exception=NotAuthorized,
            detail="Only administrators can list users.",
        )

        # Input validation
        if skip < 0:
            raise ValidationError("Skip parameter must be non-negative")
        if limit <= 0 or limit > 100:
            raise ValidationError("Limit must be between 1 and 100")

        # Delegate fetching to the repository
        appliances, total = await self.appliance_repository.get_all(
            db=db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc,
        )

        # Calculate pagination info
        page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit  # Ceiling division

        # Construct the response schema
        response = UserApplianceListResponse(
            items=appliances, total=total, page=page, pages=total_pages, size=limit
        )

        return response

    async def create_appliance(
        self, db: AsyncSession, *, current_user: User, appliance_in: UserApplianceCreate
    ) -> UserAppliance:
        """create a new appliance"""

        existing_by_name = await self.appliance_repository.get_by_name_for_user(
            db=db, name=appliance_in.custom_name, user_id=current_user.id
        )
        raise_for_status(
            condition=(existing_by_name is not None),
            exception=ResourceAlreadyExists,
            detail=f"Appliance with name {existing_by_name} already exists",
            resource_type="Appliance",
        )
        appliance_dict = appliance_in.model_dump()
        appliance_dict["created_at"] = datetime.now(timezone.utc)
        appliance_dict["updated_at"] = datetime.now(timezone.utc)

        appliance_to_create = UserAppliance(**appliance_dict)

        new_appliance = await self.appliance_repository.create(
            db=db, obj_in=appliance_to_create
        )
        await db.refresh(new_appliance)

        self._logger.info(f"New appliance created: {new_appliance.custom_name}")

        return new_appliance

    async def update_appliance(
        self,
        db: AsyncSession,
        *,
        current_user: User,
        appliance_id: uuid.UUID,
        appliance_data: UserApplianceUpdate,
    ) -> UserAppliance:
        """update an existing appliance"""

        appliance_to_update = await appliance_repository.get(db=db, obj_id=appliance_id)
        raise_for_status(
            condition=(appliance_to_update is None),
            exception=ResourceNotFound,
            detail=f"Appliance with id {appliance_id} not found.",
            resource_type="Appliance",
        )

        self._check_authorization(
            current_user=current_user, appliance=appliance_to_update, action="Update"
        )

        await self._validate_book_update(db, appliance_data, appliance_to_update)

        update_dict = appliance_data.model_dump(exclude_unset=True, exclude_none=True)

        # Remove timestamp fields that should not be manually updated
        for ts_field in {"created_at", "updated_at"}:
            update_dict.pop(ts_field, None)

        updated_book = await self.appliance_repository.update(
            db=db, appliance=appliance_to_update, fields_to_update=update_dict
        )

        await cache_service.invalidate(UserAppliance, appliance_id)

        self._logger.info(
            f"Appliance {appliance_id} updated by {current_user.id}",
            extra={
                "updated_appliance_id": appliance_id,
                "updater_id": current_user.id,
                "updated_fields": list(update_dict.keys()),
            },
        )
        return updated_book

    async def delete_appliance(
        self, db: AsyncSession, *, current_user: User, appliance_id: uuid.UUID
    ) -> None:
        """Delete an appliance by it's ID"""

        appliance_to_delete = await self.appliance_repository.get(
            db=db, obj_id=appliance_id
        )
        raise_for_status(
            condition=(appliance_to_delete is None),
            exception=ResourceNotFound,
            detail=f"Appliance with id {appliance_id} not found",
            resource_type="Appliance",
        )

        # 2. Perform authorization check
        self._check_authorization(
            current_user=current_user,
            appliance=appliance_to_delete,
            action="delete",
        )

        # 4. Perform the deletion
        await self.appliance_repository.delete(db=db, obj_id=appliance_id)

        # 5. Clean up cache and tokens
        await cache_service.invalidate(UserAppliance, appliance_id)

        self._logger.warning(
            f"Appliance {appliance_id} permanently deleted by {current_user.id}",
            extra={
                "deleted_appliance_id": appliance_id,
                "deleter_id": current_user.id,
                "deleted_appliance_name": appliance_id.custom_name,
            },
        )

    async def get_appliance_catalog(self, db: AsyncSession) -> List[ApplianceCatalog]:
        """Gets the list of common appliances from the catalog."""

        return await self.appliance_repository.get_catalog_items(db=db)

    async def _validate_user_update(
        self,
        db: AsyncSession,
        appliance_data: UserApplianceUpdate,
        current_user: User,
        existing_appliance: UserAppliance,
    ) -> None:
        """Validates appliance update data for potential conflicts."""

        if appliance_data.custom_name != existing_appliance.custom_name:
            if await self.appliance_repository.get_by_name_for_user(
                db=db, name=appliance_data.custom_name, user_id=current_user.id
            ):
                raise ResourceAlreadyExists("Name is already in use")


appliance_service = ApplianceService()
