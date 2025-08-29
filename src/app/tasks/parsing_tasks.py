# app/tasks/parsing_tasks.py
import logging
from datetime import date
import time
import random
import uuid  # Import uuid
import asyncio
from src.app.core.celery_app import celery_app
from src.app.db.session import db
from src.app.crud.bill_crud import bill_repository
from src.app.schemas.bill_schema import (
    NormalizedBillSchema,
    BillResponse,
)
from src.app.models.bill_model import BillStatus

# This needs the full BillService to use the update_bill_after_parsing method
from src.app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


# Mock parser is fine, no changes needed
def _mock_pdf_parser(file_uri: str) -> dict:
    """
    A mock function that simulates parsing a PDF.
    In a real application, this would contain complex logic using a library like PyMuPDF.
    """
    logger.info(f"MOCK PARSER: Pretending to parse file at {file_uri}...")
    time.sleep(5)  # Simulate a slow parsing process

    # Return a dictionary of data that conforms to our NormalizedBillSchema
    return {
        "discom": "Mock Power Ltd.",
        "account": {"consumer_id": "MOCK-12345", "name": "Test User"},
        "period": {"start": "2025-07-01", "end": "2025-07-31"},
        "consumption": {
            "readings": {"previous": 1000.0, "current": 1350.5},
            "total_kwh": 350.5,
        },
        "charges_breakdown": [
            {"name": "Energy Charge", "amount": 1800.0},
            {"name": "Fixed Charge", "amount": 150.0},
            {"name": "Tax", "amount": 250.0},
        ],
        "billing_summary": {"net_current_demand": 2200.0, "total_payable": 2200.0},
        "totals": {"cost": 2200.0, "currency": "INR"},
    }


# @celery_app.task(name="tasks.parse_digital_pdf")
# def parse_digital_pdf_task(bill_id: str):  # Celery tasks should be synchronous
#     """Celery task to parse a PDF bill, update the database, and trigger next steps."""
#     logger.info(f"Worker received task: Parse PDF for bill_id: {bill_id}")

#     # Use a real async event loop runner for the async code
#     import asyncio

#     async def main():
#         async with db.session_context() as session:
#             try:
#                 # Use the service layer's update method instead of raw repository
#                 # This keeps logic centralized. We just need to create it.
#                 # Let's simplify and call the repository directly for now.

#                 bill_uuid = uuid.UUID(bill_id)  # Convert str back to UUID
#                 bill = await bill_repository.get(db=session, bill_id=bill_uuid)
#                 if not bill:
#                     logger.error(f"Bill with ID {bill_id} not found in database.")
#                     return

#                 raw_parsed_data = _mock_pdf_parser(bill.file_uri)
#                 normalized_data = NormalizedBillSchema.model_validate(raw_parsed_data)

#                 update_data = {
#                     "parse_status": BillStatus.SUCCESS,
#                     "provider": normalized_data.discom,
#                     "billing_period_start": normalized_data.period.start,
#                     "billing_period_end": normalized_data.period.end,
#                     "kwh_total": normalized_data.consumption.total_kwh,
#                     "cost_total": normalized_data.totals.get("cost"),
#                     "normalized_json": normalized_data.model_dump(mode="json"),
#                     "parser_version": "mock-v1.0",
#                     "checksum": f"sha256:{random.getrandbits(256):064x}",
#                 }
#                 await bill_repository.update(
#                     db=session, bill=bill, fields_to_update=update_data
#                 )
#                 logger.info(f"Successfully parsed and updated bill: {bill_id}")

#                 await cache_service.invalidate(BillResponse, bill_uuid)

#             except Exception as e:
#                 logger.error(f"Failed to parse bill {bill_id}: {e}", exc_info=True)
#                 bill = await bill_repository.get(db=session, bill_id=uuid.UUID(bill_id))
#                 if bill:
#                     await bill_repository.update(
#                         db=session,
#                         bill=bill,
#                         fields_to_update={"parse_status": BillStatus.FAILED},
#                     )
#                     await cache_service.invalidate(BillResponse, uuid.UUID(bill_id))


#     asyncio.run(main())
@celery_app.task(name="tasks.parse_digital_pdf")
def parse_digital_pdf_task(bill_id: str):
    """Celery task to parse a PDF bill, update the database, and trigger next steps."""
    logger.info(f"Worker received task: Parse PDF for bill_id: {bill_id}")

    # We define an async function inside the sync task
    async def main():
        async with db.session_context() as session:
            try:
                bill_uuid = uuid.UUID(bill_id)
                bill = await bill_repository.get(db=session, bill_id=bill_uuid)
                if not bill:
                    logger.error(f"Bill with ID {bill_id} not found in database.")
                    return

                raw_parsed_data = _mock_pdf_parser(bill.file_uri)
                normalized_data = NormalizedBillSchema.model_validate(raw_parsed_data)

                update_data = {
                    "parse_status": BillStatus.SUCCESS,
                    "provider": normalized_data.discom,
                    "billing_period_start": normalized_data.period.start,
                    "billing_period_end": normalized_data.period.end,
                    "kwh_total": normalized_data.consumption.total_kwh,
                    "cost_total": normalized_data.totals.get("cost"),
                    "normalized_json": normalized_data.model_dump(mode="json"),
                    "parser_version": normalized_data.version,
                    "checksum": f"sha256:{random.getrandbits(256):064x}",
                }
                await bill_repository.update(
                    db=session, bill=bill, fields_to_update=update_data
                )
                logger.info(f"Successfully parsed and updated bill: {bill_id}")

                await cache_service.invalidate(BillResponse, bill_uuid)
                # estimate_appliances_task.delay(bill_id)

            except Exception as e:
                logger.error(f"Failed to parse bill {bill_id}: {e}", exc_info=True)
                # Ensure we use a new session for the failure update
                async with db.session_context() as error_session:
                    bill = await bill_repository.get(
                        db=error_session, bill_id=uuid.UUID(bill_id)
                    )
                    if bill:
                        await bill_repository.update(
                            db=error_session,
                            bill=bill,
                            fields_to_update={"parse_status": BillStatus.FAILED},
                        )
                        await cache_service.invalidate(BillResponse, uuid.UUID(bill_id))

    # We run our async main function using asyncio.run()
    asyncio.run(main())
