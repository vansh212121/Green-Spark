# app/tasks/parsing_tasks.py
import logging
import uuid
import asyncio
import os
import hashlib

from src.app.core.celery_app import celery_app
from src.app.db.session import Database
from src.app.crud.bill_crud import bill_repository
from src.app.schemas.bill_schema import NormalizedBillSchema
from src.app.models.bill_model import BillStatus
from src.app.services.s3_service import s3_service
from src.app.services.ai_service import ai_service
from src.app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.parse_digital_pdf")
def parse_digital_pdf_task(bill_id: str, mime_type: str = "application/pdf"):
    """Celery task to parse a PDF/image bill using Gemini, update the database, and trigger next steps."""
    logger.info(f"Worker received task: Parse document for bill_id: {bill_id}")
    local_file_path = None

    async def main():
        nonlocal local_file_path

        # 1. Create a NEW, LOCAL Database instance for this task run.
        local_db = Database(str(settings.DATABASE_URL))

        # 2. Connect and get a session from this new local instance.
        await local_db.connect()
        async with local_db.session_context() as session:
            try:
                bill_uuid = uuid.UUID(bill_id)
                bill = await bill_repository.get(db=session, bill_id=bill_uuid)
                if not bill:
                    logger.error(f"Bill {bill_id} not found")
                    return

                # 3. Download file from S3 to a temporary local path
                local_file_path = s3_service.download_file(bill.file_uri)

                # 4. Call our AI service to parse the file
                raw_parsed_data = ai_service.parse_bill_with_gemini(
                    local_file_path, mime_type
                )

                # 5. Validate the AI's output against our strict schema
                normalized_data = NormalizedBillSchema.model_validate(raw_parsed_data)

                # 6. Compute checksum of the local file
                with open(local_file_path, "rb") as f:
                    checksum = "sha256:" + hashlib.sha256(f.read()).hexdigest()

                # 7. Prepare the data for database update
                update_data = {
                    "parse_status": BillStatus.SUCCESS,
                    "provider": normalized_data.discom,
                    "billing_period_start": normalized_data.period.start,
                    "billing_period_end": normalized_data.period.end,
                    "kwh_total": normalized_data.consumption.total_kwh,
                    "cost_total": normalized_data.totals.get("cost"),
                    "normalized_json": normalized_data.model_dump(mode="json"),
                    "parser_version": normalized_data.version,
                    "checksum": checksum,
                }

                await bill_repository.update(
                    db=session, bill=bill, fields_to_update=update_data
                )
                logger.info(f"Successfully parsed and updated bill: {bill_id}")

                # await cache_service.invalidate(BillResponse, bill_uuid)

            except Exception as e:
                logger.error(f"Failed to parse bill {bill_id}: {e}", exc_info=True)
                async with local_db.session_context() as error_session:
                    bill = await bill_repository.get(
                        db=error_session, bill_id=uuid.UUID(bill_id)
                    )
                    if bill:
                        await bill_repository.update(
                            db=error_session,
                            bill=bill,
                            fields_to_update={"parse_status": BillStatus.FAILED},
                        )
                        # await cache_service.invalidate(BillResponse, uuid.UUID(bill_id))
            finally:
                # 8. CRITICAL: Clean up the temporary file
                if local_file_path and os.path.exists(local_file_path):
                    os.remove(local_file_path)

                # 9. Always disconnect from DB
                await local_db.disconnect()

    asyncio.run(main())
