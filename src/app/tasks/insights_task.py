import logging
import uuid
import asyncio
from datetime import datetime

from src.app.core.celery_app import celery_app

from src.app.crud.insights_crud import insights_repository
from src.app.models.insights_model import InsightStatus
from src.app.schemas.bill_schema import BillDetailedResponse
from src.app.services.ai_service import ai_service
from src.app.services.bill_service import bill_service

from src.app.db.session import Database
from src.app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.generate_insights")
def generate_insights_task(bill_id: str, user_id: str):
    """Celery task to generate insights for a bill by calling the AI service."""
    logger.info(f"Worker received task: Generate insights for bill_id: {bill_id}")

    async def main():
        bill_uuid = uuid.UUID(bill_id)
        user_uuid = uuid.UUID(user_id)

        # --- THE FIX: Create a NEW, LOCAL Database instance for this task run ---
        local_db = Database(str(settings.DATABASE_URL))
        await local_db.connect()
        async with local_db.session_context() as session:
            try:
                # YOUR EXISTING LOGIC IS PRESERVED HERE
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

                # Find the current and previous bills
                current_bill = next((b for b in all_bills if b.id == bill_uuid), None)
                if not current_bill:
                    raise ValueError(
                        f"Current bill {bill_uuid} not found in user's bill list."
                    )

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

                # 3. Call the AI service
                validated_report = ai_service.generate_insights_from_context(context)

                # 4. Update the insight record
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
                # We can reuse the same session to update the status on failure
                insight_to_fail = await insights_repository.get(
                    db=session, bill_id=bill_uuid
                )
                if insight_to_fail:
                    insight_to_fail.status = InsightStatus.FAILED
                    session.add(insight_to_fail)
                    await session.commit()
            finally:
                # --- CRITICAL: Always disconnect from the database when done ---
                await local_db.disconnect()
                logger.info("Insight task finished, DB connection closed.")

    # Run the self-contained async main function, just like in estimation_tasks.py
    asyncio.run(main())
