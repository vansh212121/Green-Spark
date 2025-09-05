# app/crud/insight_crud.py

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, TypeVar, Generic, Any, Dict

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.exception_utils import handle_exceptions
from src.app.core.exceptions import InternalServerError
from abc import ABC, abstractmethod
from src.app.models.insights_model import Insight

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


class InsightsRepository(BaseRepository[Insight]):
    """Repository for all database operations related to the User model."""

    def __init__(self):
        super().__init__(Insight)
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get(self, db: AsyncSession, *, bill_id: uuid.UUID) -> Optional[Insight]:
        """Get insights by it's bill_id"""
        statement = select(self.model).where(self.model.bill_id == bill_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def create(self, db: AsyncSession, *, obj_in: Insight) -> Insight:
        """create an insight"""

        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        return obj_in

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def update(
        self, db: AsyncSession, *, insight: Insight, fields_to_update: Dict[str, Any]
    ) -> Insight:
        """Update insights by bill_id"""

        for field, value in fields_to_update.items():
            if field in {"generated_at"} and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    value = datetime.now(timezone.utc)

            setattr(insight, field, value)

        db.add(insight)
        await db.commit()
        await db.refresh(insight)

        self._logger.info(
            f"insight fields updated for {insight.id}: {list(fields_to_update.keys())}"
        )
        return insight

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def delete(self, db: AsyncSession, *, bill_id: uuid.UUID) -> None:
        statement = select(self.model).where(self.model.bill_id == bill_id)
        await db.execute(statement)
        await db.commit()
        self._logger.info(f"Insight hard deleted: {bill_id}")
        return


insights_repository = InsightsRepository()
