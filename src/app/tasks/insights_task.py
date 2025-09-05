# app/tasks/insight_tasks.py

import logging
import uuid
import asyncio
from datetime import datetime

from src.app.core.celery_app import celery_app
from src.app.db.session import db
from src.app.crud.insights_crud import insights_repository
from src.app.models.insights_model import InsightStatus
from src.app.schemas.bill_schema import BillResponse, BillDetailedResponse
from src.app.services.ai_service import ai_service
from src.app.services.bill_service import bill_service

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.generate_insights")
def generate_insights_task(bill_id: str, user_id: str):
    """Celery task to generate insights for a bill by calling the AI service."""
    logger.info(f"Worker received task: Generate insights for bill_id: {bill_id}")

    async def main():
        bill_uuid = uuid.UUID(bill_id)
        user_uuid = uuid.UUID(user_id)

        async with db.session_context() as session:
            try:
                insight = await insights_repository.get(db=session, bill_id=bill_uuid)
                if not insight:
                    logger.error(
                        f"Insight record for bill {bill_id} not found. Aborting task."
                    )
                    return

                # 1. Fetch bills sorted by billing period
                bill_list_response = await bill_service.get_my_bills(
                    db=session,
                    user_id=user_uuid,
                    limit=12,
                    skip=0,
                    order_by="billing_period_start",
                    order_desc=True,
                    filters=None,
                )

                all_bills = bill_list_response.items

                if not all_bills:
                    raise ValueError("No bills found for user to generate insights.")

                # Find the current bill
                current_bill = next((b for b in all_bills if b.id == bill_uuid), None)
                if not current_bill:
                    raise ValueError(
                        f"Current bill {bill_uuid} not found in user's bill list."
                    )

                # Find the previous bill (one before current, by billing_period_start order)
                prev_bill = None
                for idx, bill in enumerate(all_bills):
                    if bill.id == bill_uuid and idx + 1 < len(all_bills):
                        prev_bill = all_bills[idx + 1]
                        break

                # 2. Assemble context
                context = {
                    "current_bill": BillDetailedResponse.model_validate(
                        current_bill
                    ).model_dump(mode="json"),
                    "previous_bill": (
                        BillDetailedResponse.model_validate(prev_bill).model_dump(
                            mode="json"
                        )
                        if prev_bill
                        else None
                    ),
                }

                # 3. Call the AI service to get the final, validated Pydantic object
                validated_report = ai_service.generate_insights_from_context(context)

                # 4. Update the insight record with the result
                insight.structured_data = validated_report.model_dump(mode="json")
                insight.status = InsightStatus.COMPLETED
                insight.generated_at = datetime.utcnow()
                session.add(insight)
                await session.commit()
                logger.info(
                    f"Successfully generated and saved insights for bill {bill_id}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to generate insights for bill {bill_id}: {e}",
                    exc_info=True,
                )
                async with db.session_context() as error_session:
                    insight = await insights_repository.get(
                        db=error_session, bill_id=uuid.UUID(bill_id)
                    )
                    if insight:
                        insight.status = InsightStatus.FAILED
                        error_session.add(insight)
                        await error_session.commit()

    asyncio.run(main())
