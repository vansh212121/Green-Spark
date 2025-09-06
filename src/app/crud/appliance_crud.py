import logging
import uuid
from typing import Optional, List, Dict, Any, TypeVar, Generic, Tuple
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_, delete

from src.app.core.exception_utils import handle_exceptions
from src.app.core.exceptions import InternalServerError

from src.app.models.appliance_model import (
    ApplianceCatalog,
    ApplianceEstimate,
    UserAppliance,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository providing consistent interface for database operations."""

    def __init__(self, model: type[T]):
        self.model = model

    @abstractmethod
    async def get(self, db: AsyncSession, *, obj_id: Any) -> Optional[T]:
        """Get entity by its primary key."""
        pass

    @abstractmethod
    async def create(self, db: AsyncSession, *, obj_in: Any) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, db: AsyncSession, *, db_obj: T, obj_in: Any) -> T:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, db: AsyncSession, *, obj_id: Any) -> None:
        """Delete an entity by its primary key."""
        pass


class UserApplianceRepository(BaseRepository[UserAppliance]):
    """Repository for all database operations related to the User model."""

    def __init__(self):
        super().__init__(UserAppliance)
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get(
        self, db: AsyncSession, *, obj_id: uuid.UUID
    ) -> Optional[UserAppliance]:
        """"""
        statement = (
            select(self.model)
            .where(self.model.id == obj_id)
            .options(selectinload(self.model.estimates))
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[UserAppliance], int]:
        """Get paginated list of user_appliancess by user_id"""
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(selectinload(self.model.estimates))
        )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Apply ordering
        query = self._apply_ordering(query, order_by, order_desc)

        # Apply pagination
        paginated_query = query.offset(skip).limit(limit)
        result = await db.execute(paginated_query)
        appliances = result.scalars().all()

        return appliances, total

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_by_bills(
        self,
        db: AsyncSession,
        *,
        bill_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[UserAppliance], int]:
        """Get paginated list of user_appliancess by user_id"""
        query = (
            select(self.model)
            .where(self.model.bill_id == bill_id)
            .options(selectinload(self.model.estimates))  # 👈 force load estimates
        )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Apply ordering
        query = self._apply_ordering(query, order_by, order_desc)

        # Apply pagination
        paginated_query = query.offset(skip).limit(limit)
        result = await db.execute(paginated_query)
        appliances = result.scalars().all()

        return appliances, total

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_all(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> Tuple[List[UserAppliance], int]:
        """Get multiple user_appliancess with filtering and pagination."""
        query = select(self.model)

        # Apply filters
        if filters:
            query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        # Apply ordering
        query = self._apply_ordering(query, order_by, order_desc)

        # Apply pagination
        paginated_query = query.offset(skip).limit(limit)
        result = await db.execute(paginated_query)
        appliances = result.scalars().all()

        return appliances, total

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def create(self, db: AsyncSession, *, obj_in: UserAppliance) -> UserAppliance:
        """Create a new user_appliance. Expects a pre-constructed UserAppliance model object."""
        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        self._logger.info(f"UserAppliance created: {obj_in.id}")
        return obj_in

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def update(
        self,
        db: AsyncSession,
        *,
        appliance: UserAppliance,
        fields_to_update: Dict[str, Any],
    ) -> UserAppliance:
        # Updates specific fields of a bill object.

        for field, value in fields_to_update.items():
            if field in {"created_at", "updated_at"} and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    value = datetime.now(timezone.utc)

            setattr(appliance, field, value)

        db.add(appliance)
        await db.commit()
        await db.refresh(appliance)

        self._logger.info(
            f"appliance fields updated for {appliance.id}: {list(fields_to_update.keys())}"
        )
        return appliance

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def delete(self, db: AsyncSession, *, obj_id: uuid.UUID) -> None:
        """Delete a user_appliance by it's ID"""
        statement = delete(self.model).where(self.model.id == obj_id)
        await db.execute(statement)
        await db.commit()
        self._logger.info(f"UserAppliance hard deleted: {obj_id}")
        return

    # ==================== Catalog METHODS ====================
    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def check_catalog_exists(
        self, db: AsyncSession, *, catalog_id: uuid.UUID
    ) -> bool:
        """
        Check if an appliance catalog entry exists.

        Args:
            catalog_id: UUID of the catalog entry

        Returns:
            True if exists, False otherwise
        """
        query = select(ApplianceCatalog).where(
            ApplianceCatalog.category_id == catalog_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_catalog_items(self, db: AsyncSession) -> List[ApplianceCatalog]:
        """Get all appliance catalog items."""
        statement = select(ApplianceCatalog).order_by(ApplianceCatalog.label)
        result = await db.execute(statement)
        return result.scalars().all()

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def create_catalog(
        self, db: AsyncSession, *, catalog_in: ApplianceCatalog
    ) -> ApplianceCatalog:
        """Create an catalog"""
        db.add(catalog_in)
        await db.commit()
        await db.refresh(catalog_in)
        self._logger.info(f"Catalog created: {catalog_in.category_id}")
        return catalog_in

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def delete_catalog(self, db: AsyncSession, *, obj_id: str) -> None:
        """Delete a catalog by it's ID"""
        statement = delete(ApplianceCatalog).where(
            ApplianceCatalog.category_id == obj_id
        )
        await db.execute(statement)
        await db.commit()
        self._logger.info(f"Appliance Catalog hard deleted: {obj_id}")
        return

    # ===========estimates============
    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_all_estimates(
        self, db: AsyncSession, *, bill_id: uuid.UUID
    ) -> List[ApplianceEstimate]:
        """Get all estimates for a bill"""
        statement = select(ApplianceEstimate).where(
            ApplianceEstimate.bill_id == bill_id
        )
        result = await db.execute(statement)
        return result.scalars().all()

    # ==================== HELPER METHODS ====================
    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_by_name_for_user(
        self, db: AsyncSession, *, name: str, user_id: uuid.UUID
    ) -> Optional[UserAppliance]:
        """Check if a user already has an appliance with the same custom name."""
        statement = select(self.model).where(
            and_(self.model.custom_name == name, self.model.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def exists(
        self, db: AsyncSession, *, label: str
    ) -> Optional[ApplianceCatalog]:
        """Check if an appliance already exists with the same label"""
        statement = select(ApplianceCatalog).where(ApplianceCatalog.label == label)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    def _apply_ordering(self, query, order_by: str, order_desc: bool):
        """Apply ordering to query."""
        order_column = getattr(self.model, order_by, self.model.created_at)
        if order_desc:
            return query.order_by(order_column.desc())
        else:
            return query.order_by(order_column.asc())


appliance_repository = UserApplianceRepository()
