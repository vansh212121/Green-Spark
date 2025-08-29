import logging
import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_, or_, delete

from src.app.core.exception_utils import handle_exceptions
from src.app.core.exceptions import InternalServerError

from src.app.models.bill_model import Bill, BillStatus

logger = logging.getLogger(__name__)


class BillRepository:
    """Repository for all database operations related to the User model."""

    def __init__(self, model: type[Bill] = Bill):
        # Corrected __init__
        self.model = model
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get(self, db: AsyncSession, *, bill_id: uuid.UUID) -> Optional[Bill]:
        """Get a bill by it's ID"""
        statement = select(self.model).where(self.model.id == bill_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_by_checksum(
        self, db: AsyncSession, *, checksum: str, user_id: uuid.UUID
    ) -> Optional[Bill]:
        """Finds a bill by its checksum for a specific user to prevent duplicates."""
        statement = select(self.model).where(
            and_(self.model.checksum == checksum, self.model.user_id == user_id)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

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
    ) -> Tuple[List[Bill], int]:
        """Get multiple bills with filtering and pagination."""
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
        bills = result.scalars().all()

        return bills, total

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def get_latest_by_user(
        self, db: AsyncSession, *, user_id: uuid.UUID
    ) -> Optional[Bill]:
        """Gets the most recent bill for a user based on billing period end date."""
        statement = (
            select(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.parse_status == BillStatus.SUCCESS,
                )
            )
            .order_by(self.model.billing_period_end.desc())
            .limit(1)
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def create(self, db: AsyncSession, *, bill_data: Bill) -> Bill:
        """Create a bill"""

        db.add(bill_data)
        await db.commit()
        await db.refresh(bill_data)
        self._logger.info(f"Bill created: {bill_data}")
        return bill_data

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def update(
        self, db: AsyncSession, bill: Bill, fields_to_update: Dict[str, Any]
    ) -> Bill:
        # Updates specific fields of a bill object.

        for field, value in fields_to_update.items():
            if field in {"created_at"} and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    value = datetime.now(timezone.utc)

            setattr(bill, field, value)

        db.add(bill)
        await db.commit()
        await db.refresh(bill)

        self._logger.info(
            f"bill fields updated for {bill.id}: {list(fields_to_update.keys())}"
        )
        return bill

    @handle_exceptions(
        default_exception=InternalServerError,
        message="An unexpected database error occurred.",
    )
    async def delete(self, db: AsyncSession, *, bill_id: uuid.UUID) -> None:
        """Delete a bill by it's ID"""
        statement = delete(self.model).where(self.model.id == bill_id)
        await db.execute(statement)
        await db.commit()
        self._logger.info(f"Bill hard deleted: {bill_id}")
        return

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Apply filters to query."""
        conditions = []

        if "user_id" in filters and filters["user_id"] is not None:
            conditions.append(Bill.user_id == filters["user_id"])

        if "source_type" in filters and filters["source_type"] is not None:
            conditions.append(Bill.source_type == filters["source_type"])

        if "search" in filters and filters["search"]:
            search_term = f"%{filters['search']}%"
            conditions.append(
                or_(
                    Bill.provider.ilike(search_term),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        return query

    def _apply_ordering(self, query, order_by: str, order_desc: bool):
        """Apply ordering to query."""
        order_column = getattr(self.model, order_by, self.model.created_at)
        if order_desc:
            return query.order_by(order_column.desc())
        else:
            return query.order_by(order_column.asc())


bill_repository = BillRepository()
