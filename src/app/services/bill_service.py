# app/services/user_service.py
"""
Bill service module.

This module provides the business logic layer for user operations,
handling authorization, validation, and orchestrating repository calls.
"""
import uuid
import logging
from typing import Optional, Dict, Any
from datetime import date

from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.crud.user_crud import user_repository
from src.app.crud.bill_crud import bill_repository
from src.app.schemas.bill_schema import (
    BillUploadRequest,
    BillListResponse,
    BillResponse,
    BillUploadResponse,
    BillConfirmRequest,
    NormalizedBillSchema,
)
from src.app.models.bill_model import Bill, BillStatus, BillSource
from src.app.models.user_model import User, UserRole

from src.app.services.s3_service import s3_service

from src.app.services.cache_service import cache_service
from src.app.core.exception_utils import raise_for_status
from src.app.core.exceptions import (
    ResourceNotFound,
    NotAuthorized,
    InternalServerError,
    ValidationError,
)
from src.app.tasks.parsing_tasks import parse_digital_pdf_task

logger = logging.getLogger(__name__)


class BillService:
    """Handles all user-related business logic."""

    def __init__(self):
        """
        Initializes the UserService.
        This version has no arguments, making it easy for FastAPI to use,
        while still allowing for dependency injection during tests.
        """
        self.user_repository = user_repository
        self.bill_repository = bill_repository
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _check_authorization(
        self, *, current_user: User, bill: Bill, action: str
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
        is_not_self = str(current_user.id) != str(bill.user_id)
        raise_for_status(
            condition=is_not_self,
            exception=NotAuthorized,
            detail=f"You are not authorized to {action} this user.",
        )

    async def _load_bill_schema_from_db(
        self, *, db: AsyncSession, bill_id: uuid.UUID
    ) -> Optional[BillResponse]:
        """Private helper to load a user from the DB and convert it to a Pydantic schema.
        This is our "loader" function for the cache."""

        bill_model = await self.bill_repository.get(db=db, bill_id=bill_id)
        raise_for_status(
            condition=bill_model is None,
            exception=ResourceNotFound,
            detail=f"Bill with {bill_id} not Found.",
            resource_type="Bill",
        )
        return BillResponse.model_validate(bill_model)

    async def get_bill_by_id(
        self, db: AsyncSession, *, bill_id: uuid.UUID, current_user: User
    ) -> Optional[BillResponse]:
        """Retrieve bill by it's ID"""

        bill = await cache_service.get_or_set(
            schema_type=BillResponse,
            obj_id=bill_id,
            loader=lambda: self._load_bill_schema_from_db(db=db, bill_id=bill_id),
            ttl=300,  # Cache for 5 minutes
        )

        # Fine-grained authorization check
        if current_user.is_admin:
            return bill
        is_not_self = current_user.id != bill.user_id

        raise_for_status(
            condition=(is_not_self),
            exception=NotAuthorized,
            detail="You are not authorized to view this bill.",
        )

        self._logger.debug(f"Bill {bill_id} retrieved by user {current_user.id}")
        return bill

    async def get_user_bills(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> BillListResponse:
        """
        Lists bills with pagination and filtering.

        Args:
            db: Database session
            current_user: User making the request
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters to apply
            order_by: Field to order by
            order_desc: Whether to order in descending order

        Returns:
            UserListResponse: Paginated list of users

        Raises:
            NotAuthorized: If user lacks permission to list users
            ValidationError: If pagination parameters are invalid
        """
        # Authorization check: admins can list all users
        user = await self.user_repository.get(db=db, obj_id=user_id)

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
        bills, total = await self.bill_repository.get_all(
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
        response = BillListResponse(
            items=bills, total=total, page=page, pages=total_pages, size=limit
        )

        return response

    def create_upload_url(
        self, *, user: User, filename: str, content_type: str
    ) -> BillUploadResponse:
        """Generates a presigned URL for a direct-to-storage file upload."""
        object_key = f"{user.id}/{uuid.uuid4()}-{filename}"

        # Now we pass the content_type down to the s3_service
        upload_url = s3_service.generate_presigned_put_url(
            object_key=object_key, content_type=content_type
        )

        file_uri = f"s3://{s3_service.bucket_name}/{object_key}"
        return BillUploadResponse(upload_url=upload_url, file_uri=file_uri)

    async def confirm_upload_and_start_parsing(
        self, db: AsyncSession, *, user: User, confirm_data: BillConfirmRequest
    ) -> Bill:
        """Creates an initial bill record and triggers the async parsing task."""
        bill_obj = Bill(
            user_id=user.id,
            file_uri=confirm_data.file_uri,
            source_type=BillSource.PDF,
            parse_status=BillStatus.PROCESSING,
            billing_period_start=date(1970, 1, 1),  # Corrected: use date object
            billing_period_end=date(1970, 2, 2),  # Corrected: use date object
            kwh_total=10,
            cost_total=10,
            provider="Pending Parse",
        )

        new_bill = await self.bill_repository.create(db=db, bill_data=bill_obj)

        # Trigger the parsing task
        parse_digital_pdf_task.delay(bill_id=str(new_bill.id))

        logger.info(
            f"PDF bill processing queued for user {user.id}, bill_id: {new_bill.id}"
        )
        return new_bill

    async def update_bill_after_parsing(
        self, db: AsyncSession, *, bill_id: uuid.UUID, parsed_data: NormalizedBillSchema
    ) -> Bill:
        """
        Updates a bill record with data from the Celery parser.
        This is an internal method called by the system, not a user.
        """
        # 1. Fetch the existing placeholder bill object
        bill_to_update = await self.bill_repository.get(db=db, bill_id=bill_id)
        if not bill_to_update:
            # This should ideally not happen if the task was triggered correctly
            logger.error(f"Cannot update non-existent bill with ID: {bill_id}")
            raise ResourceNotFound(resource_type="Bill", resource_id=str(bill_id))

        # 2. Prepare the dictionary of fields to update on the main table
        update_data = {
            "parse_status": BillStatus.SUCCESS,
            "provider": parsed_data.discom,
            "billing_period_start": parsed_data.period.start,
            "billing_period_end": parsed_data.period.end,
            "kwh_total": parsed_data.consumption.total_kwh,
            "cost_total": parsed_data.totals.get("cost"),
            "normalized_json": parsed_data.model_dump(),
            "parser_version": parsed_data.version,
            # "checksum": ... # The worker would calculate and pass this in
        }

        # 3. Call the repository to save the changes
        updated_bill = await self.bill_repository.update(
            db=db, bill=bill_to_update, fields_to_update=update_data
        )

        # 4. CRITICAL: Invalidate the cache for this bill
        await cache_service.invalidate(BillResponse, updated_bill.id)

        self._logger.info(f"Successfully parsed and updated bill: {bill_id}")

        # 5. Trigger the next step in the pipeline
        # estimate_appliances_task.delay(updated_bill.id)

        return updated_bill

    async def delete_bill(
        self, db: AsyncSession, *, bill_id_to_delete: uuid.UUID, current_user: User
    ) -> None:
        """Deleted a bill by it's ID"""

        bill_to_delete = await self.bill_repository.get(db=db, bill_id=bill_id_to_delete)

        raise_for_status(
            condition=(bill_to_delete is None),
            exception=ResourceNotFound,
            detail=f"Bill with id {bill_id_to_delete} is not found.",
            resource_type="Bill",
        )
        self._check_authorization(
            current_user=current_user,
            bill=bill_to_delete,
            action="delete",
        )

        # 4. Perform the deletion
        await self.bill_repository.delete(db=db, bill_id=bill_to_delete)

        # 5. Clean up cache and tokens
        await cache_service.invalidate(User, bill_id_to_delete)

        self._logger.warning(
            f"Bill {bill_id_to_delete} permanently deleted by {current_user.id}",
            extra={
                "deleted_bill_id": bill_id_to_delete,
                "deleter_id": current_user.id,
            },
        )


bill_service = BillService()
