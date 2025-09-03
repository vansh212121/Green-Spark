# # app/services/insight_service.py

# import logging
# import uuid
# from typing import Optional

# from sqlmodel.ext.asyncio.session import AsyncSession

# from src.app.core.exceptions import NotAuthorized, ResourceNotFound, AppError
# from src.app.crud.insight_crud import insight_repository, InsightRepository
# from src.app.crud.bill_crud import bill_repository, BillRepository
# from src.app.models.user_model import User, UserRole
# from src.app.models.insight_model import Insight, InsightStatus
# from src.app.schemas.insight_schema import InsightRead, InsightCreate, InsightStatusResponse
# # from src.app.tasks.insight_tasks import generate_insights_task # We'll import this when the task is built

# logger = logging.getLogger(__name__)

# class InsightService:
#     def __init__(self,
#                  insight_repo: InsightRepository = insight_repository,
#                  bill_repo: BillRepository = bill_repository):
#         self.insight_repository = insight_repo
#         self.bill_repository = bill_repo

#     async def get_or_trigger_insight_generation(
#         self, db: AsyncSession, *, bill_id: uuid.UUID, user: User
#     ) -> InsightStatusResponse:
#         """
#         Checks for an existing insight for a bill. If it exists, returns its status.
#         If not, it creates a 'pending' insight record and triggers the generation task.
#         """
#         # 1. Authorize: Ensure the user owns the bill they're requesting insights for.
#         bill = await self.bill_repository.get(db=db, bill_id=bill_id)
#         if not bill:
#             raise ResourceNotFound(resource_type="Bill", resource_id=str(bill_id))
#         if bill.user_id != user.id and not user.role >= UserRole.ADMIN:
#             raise NotAuthorized("You are not authorized to access insights for this bill.")

#         # 2. Check if an insight record already exists.
#         insight = await self.insight_repository.get_by_bill_id(db=db, bill_id=bill_id)

#         if insight:
#             return InsightStatusResponse(bill_id=bill_id, status=insight.status)

#         # 3. If no insight exists, create a new one and trigger the task.
#         insight_create_schema = InsightCreate(bill_id=bill_id, user_id=user.id)
#         await self.insight_repository.create(db=db, obj_in=insight_create_schema)

#         # Trigger the Celery task to run in the background
#         # generate_insights_task.delay(str(bill_id))

#         logger.info(f"Insight generation queued for bill {bill_id} by user {user.id}")
#         return InsightStatusResponse(bill_id=bill_id, status=InsightStatus.PENDING)

#     async def get_insight_report(
#         self, db: AsyncSession, *, bill_id: uuid.UUID, user: User
#     ) -> InsightRead:
#         """
#         Securely retrieves the completed insight report for a bill.
#         """
#         insight = await self.insight_repository.get_by_bill_id(db=db, bill_id=bill_id)

#         if not insight:
#             # We can use a custom exception here for the frontend to handle
#             raise ResourceNotFound(resource_type="Insight", resource_id=f"for bill {bill_id}")

#         # Authorization check (redundant if called after get_or_trigger, but good for safety)
#         if insight.user_id != user.id and not user.role >= UserRole.ADMIN:
#             raise NotAuthorized("You are not authorized to view this insight report.")

#         if insight.status != InsightStatus.COMPLETED:
#             raise AppError(
#                 status_code=202, # 202 Accepted
#                 message=f"Insight generation is still {insight.status.value}. Please check back later.",
#                 error_code="INSIGHT_NOT_READY"
#             )

#         # Validate the stored JSON against our Pydantic schema and return it
#         return InsightRead.model_validate(insight.structured_data)

# # Singleton instance
# insight_service = InsightService()


import uuid
import logging
from typing import Optional, Dict, Any
from datetime import date

from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.crud.insights_crud import insights_repository
from src.app.crud.bill_crud import bill_repository
from src.app.schemas.insights_schema import (
    InsightResponee,
    InsightRecommendation,
    InsightKPIs,
    InsightCreate,
    InsightTrend,
    InsightStatusResponse,
)
from src.app.models.insights_model import Insight, InsightStatus
from src.app.models.bill_model import Bill
from src.app.models.user_model import User, UserRole

from src.app.services.cache_service import cache_service
from src.app.core.exception_utils import raise_for_status
from src.app.core.exceptions import (
    ResourceNotFound,
    NotAuthorized,
    ServiceUnavailable,
    ValidationError,
)


logger = logging.getLogger(__name__)


class InsightService:
    """Handles all insights-related business logic."""

    def __init__(self):
        """
        Initializes the InsightsService.
        This version has no arguments, making it easy for FastAPI to use,
        while still allowing for dependency injection during tests.
        """
        self.insights_repository = insights_repository
        self.bill_repository = bill_repository
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _check_authorization(
        self, *, current_user: User, insight: Insight, action: str
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
        is_not_self = str(current_user.id) != str(insight.user_id)
        raise_for_status(
            condition=is_not_self,
            exception=NotAuthorized,
            detail=f"You are not authorized to {action} this insight.",
        )

    async def _load_insight_schema_from_db(
        self, *, db: AsyncSession, bill_id: uuid.UUID
    ) -> Optional[InsightResponee]:
        """Private helper to load a user from the DB and convert it to a Pydantic schema.
        This is our "loader" function for the cache."""

        insight_model = await self.insights_repository.get(db=db, bill_id=bill_id)
        raise_for_status(
            condition=insight_model is None,
            exception=ResourceNotFound,
            detail=f"insight with {bill_id} not Found.",
            resource_type="Insight",
        )
        return InsightResponee.model_validate(insight_model)

    async def get_by_bill_id(
        self, db: AsyncSession, *, bill_id: uuid.UUID, current_user: User
    ) -> Optional[Insight]:
        """get insights by bill_id"""

        bill = await self.bill_repository.get(db=db, bill_id=bill_id)
        raise_for_status(
            condition=(bill is None),
            exception=ResourceNotFound,
            detail=f"Bill with the id {bill_id} not Found.",
            resource_type="Bill",
        )

        if bill.user_id != current_user.id and not current_user.role >= UserRole.ADMIN:
            raise NotAuthorized(
                "You are not authorized to add an appliance to this bill."
            )

        insight = await cache_service.get_or_set(
            schema_type=Insight,
            obj_id=bill_id,
            loader=lambda: self._load_insight_schema_from_db(db=db, bill_id=bill_id),
            ttl=300,  # Cache for 5 minutes
        )

        self._logger.debug(
            f"Insights for {bill_id} retrieved by user {current_user.id}"
        )
        return insight

    async def get_or_trigger_insight_generation(
        self, db: AsyncSession, *, bill_id: uuid.UUID, current_user: User
    ) -> InsightStatusResponse:
        """
        Checks for an existing insight for a bill. If it exists, returns its status.
        If not, it creates a 'pending' insight record and triggers the generation task.
        """
        # 1. Authorize: Ensure the user owns the bill they're requesting insights for.
        bill = await self.bill_repository.get(db=db, bill_id=bill_id)
        raise_for_status(
            condition=(bill is None),
            exception=ResourceNotFound,
            detail=f"Bill with the id {bill_id} not Found.",
            resource_type="Bill",
        )

        if bill.user_id != current_user.id and not current_user.role >= UserRole.ADMIN:
            raise NotAuthorized(
                "You are not authorized to add an appliance to this bill."
            )

        # 2. Check if an insight record already exists.
        insight = await self.insights_repository.get(db=db, bill_id=bill_id)

        if insight:
            return InsightStatusResponse(bill_id=bill_id, status=insight.status)

        # 3. If no insight exists, create a new one and trigger the task.
        insight_create_schema = InsightCreate(bill_id=bill_id, user_id=current_user.id)
        await self.insights_repository.create(db=db, obj_in=insight_create_schema)

        # Trigger the Celery task to run in the background
        # generate_insights_task.delay(str(bill_id))

        logger.info(
            f"Insight generation queued for bill {bill_id} by user {current_user.id}"
        )
        return InsightStatusResponse(bill_id=bill_id, status=InsightStatus.PENDING)

    async def get_insight_report(
        self, db: AsyncSession, *, bill_id: uuid.UUID, current_user: User
    ) -> InsightResponee:
        """
        Securely retrieves the completed insight report for a bill.
        """
        insight = await self.insights_repository.get(db=db, bill_id=bill_id)
        raise_for_status(
            condition=insight is None,
            exception=ResourceNotFound,
            detail=f"insight with {bill_id} not Found.",
            resource_type="Insight",
        )

        # Authorization check (redundant if called after get_or_trigger, but good for safety)
        if (
            insight.user_id != current_user.id
            and not current_user.role >= UserRole.ADMIN
        ):
            raise NotAuthorized("You are not authorized to view this insight report.")

        if insight.status != InsightStatus.COMPLETED:
            raise ServiceUnavailable(
                detail=f"Insight generation is still {insight.status.value}. Please check back later.",
            )

        # Validate the stored JSON against our Pydantic schema and return it
        return InsightResponee.model_validate(insight.structured_data)


# Singleton instance
insight_service = InsightService()
