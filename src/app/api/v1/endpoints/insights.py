# GET /insights/status/{bill_id}
# GET /insights/report/{bill_id}
import logging
import uuid

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.db.session import get_session
from src.app.models.user_model import User
from src.app.services.insights_service import insight_service
from src.app.schemas.insights_schema import InsightResponse, InsightStatusResponse
from src.app.utils.deps import (
    get_current_verified_user,
    require_user,
    rate_limit_refresh,
    rate_limit_api,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Insights"],
    prefix="/insights",
)


@router.get(
    "/status/{bill_id}",
    response_model=InsightStatusResponse,
    summary="Get or Confirm insights Status",
    description="Confirm insights Status",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def get_insight_generation_status(
    *,
    bill_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """
    Check the status of an insight generation task for a specific bill.

    If no insight generation has been started, this will trigger it for the first time.
    The frontend can poll this endpoint until the status is 'completed'.
    """
    return await insight_service.get_or_trigger_insight_generation(
        db=db, bill_id=bill_id, current_user=current_user
    )


@router.get(
    "/report/{bill_id}",
    response_model=InsightResponse,
    summary="Get insights",
    description="Get final insights generated through ai",
    dependencies=[Depends(rate_limit_api), Depends(require_user)],
)
async def get_insight_report(
    *,
    bill_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """
    Retrieve the final, completed insight report for a specific bill.

    This endpoint should be called after the status check returns 'completed'.
    It will raise an error if the report is not yet ready.
    """
    return await insight_service.get_insight_report(
        db=db, bill_id=bill_id, current_user=current_user
    )


@router.post(
    "/report/{bill_id}/refresh",
    response_model=InsightStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regenerate insights",
    description="Regenerate new insights through ai",
    dependencies=[Depends(require_user)],
    # dependencies=[Depends(rate_limit_refresh)] # Add a strict rate limit
)
async def refresh_insight_report(
    *,
    bill_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_verified_user),
):
    """
    Manually trigger a regeneration of the insight report for a specific bill.
    This is a rate-limited endpoint to prevent abuse.
    """
    return await insight_service.trigger_insight_regeneration(
        db=db, bill_id=bill_id, user=current_user
    )
