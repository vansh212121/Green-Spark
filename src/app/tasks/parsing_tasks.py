# app/tasks/parsing_tasks.py
# import logging
# import google.generativeai as genai
# import base64
# import json
# import hashlib
# import uuid  # Import uuid
# import asyncio
# from src.app.core.celery_app import celery_app
# from src.app.db.session import db
# from src.app.crud.bill_crud import bill_repository
# from src.app.schemas.bill_schema import (
#     NormalizedBillSchema,
#     BillResponse,
# )
# from src.app.models.bill_model import BillStatus
# from src.app.core.config import settings

# # This needs the full BillService to use the update_bill_after_parsing method
# from src.app.services.cache_service import cache_service
# from src.app.services.s3_service import s3_service

# logger = logging.getLogger(__name__)

# genai.configure(api_key=settings.API_KEY)

# model = genai.GenerativeModel("gemini-1.5-flash")


# # Mock parser is fine, no changes needed
# def _mock_pdf_parser(file_uri: str) -> dict:
#     """
#     A mock function that simulates parsing a PDF.
#     In a real application, this would contain complex logic using a library like PyMuPDF.
#     """
#     logger.info(f"MOCK PARSER: Pretending to parse file at {file_uri}...")
#     time.sleep(5)  # Simulate a slow parsing process

#     # Return a dictionary of data that conforms to our NormalizedBillSchema
#     return {
#         "discom": "Mock Power Ltd.",
#         "account": {"consumer_id": "MOCK-12345", "name": "Test User"},
#         "period": {"start": "2025-07-01", "end": "2025-07-31"},
#         "consumption": {
#             "readings": {"previous": 1000.0, "current": 1350.5},
#             "total_kwh": 350.5,
#         },
#         "charges_breakdown": [
#             {"name": "Energy Charge", "amount": 1800.0},
#             {"name": "Fixed Charge", "amount": 150.0},
#             {"name": "Tax", "amount": 250.0},
#         ],
#         "billing_summary": {"net_current_demand": 2200.0, "total_payable": 2200.0},
#         "totals": {"cost": 2200.0, "currency": "INR"},
#     }


# @celery_app.task(name="tasks.parse_digital_pdf")
# def parse_digital_pdf_task(bill_id: str):
#     """Celery task to parse a PDF bill, update the database, and trigger next steps."""
#     logger.info(f"Worker received task: Parse PDF for bill_id: {bill_id}")

#     # We define an async function inside the sync task
#     async def main():
#         async with db.session_context() as session:
#             try:
#                 bill_uuid = uuid.UUID(bill_id)
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
#                     "parser_version": normalized_data.version,
#                     "checksum": f"sha256:{random.getrandbits(256):064x}",
#                 }
#                 await bill_repository.update(
#                     db=session, bill=bill, fields_to_update=update_data
#                 )
#                 logger.info(f"Successfully parsed and updated bill: {bill_id}")

#                 await cache_service.invalidate(BillResponse, bill_uuid)
#                 # estimate_appliances_task.delay(bill_id)

#             except Exception as e:
#                 logger.error(f"Failed to parse bill {bill_id}: {e}", exc_info=True)
#                 # Ensure we use a new session for the failure update
#                 async with db.session_context() as error_session:
#                     bill = await bill_repository.get(
#                         db=error_session, bill_id=uuid.UUID(bill_id)
#                     )
#                     if bill:
#                         await bill_repository.update(
#                             db=error_session,
#                             bill=bill,
#                             fields_to_update={"parse_status": BillStatus.FAILED},
#                         )
#                         await cache_service.invalidate(BillResponse, uuid.UUID(bill_id))

#     # We run our async main function using asyncio.run()
#     asyncio.run(main())

# ========NEW SETUP==========
# def gemini_pdf_parser(file_path: str) -> dict:
#     with open(file_path, "rb") as f:
#         file_bytes = f.read()

#     encoded_file = base64.b64encode(file_bytes).decode("utf-8")

#     prompt = """You are an expert document analysis AI. Your task is to analyze the provided image or PDF of an Indian electricity bill and extract the key information into a structured JSON format.

#         The required JSON output schema is:
#         {
#           "version": "gemini-1.5",
#           "discom": "Name of the electricity provider",
#           "account": {
#             "consumer_id": "The Consumer or Account ID",
#             "meter_id": "The Meter Number (if available)",
#             "name": "The name on the bill",
#             "address": "The service address on the bill"
#           },
#           "period": {
#             "start": "YYYY-MM-DD format",
#             "end": "YYYY-MM-DD format",
#             "bill_date": "YYYY-MM-DD format",
#             "due_date": "YYYY-MM-DD format"
#           },
#           "consumption": {
#             "readings": {"previous": 1234.0, "current": 1345.0},
#             "total_kwh": 111.0
#           },
#           "charges_breakdown": [
#             {"name": "Fixed Charge", "amount": 150.0},
#             {"name": "Energy Charge", "amount": 800.50}
#             // Add ALL other charges as items in this list
#           ],
#           "billing_summary": {
#             "net_current_demand": 1200.0,
#             "subsidy": 0.0,
#             "arrears": 0.0,
#             "adjustments": 0.0,
#             "total_payable": 1200.0
#           },
#           "totals": {"cost": 1200.0, "currency": "INR"},
#           "tariff": {
#             "plan_code": "The tariff plan code/name",
#             "slabs": [
#               {"description": "0-100 kWh", "rate": 3.50},
#               {"description": "101-200 kWh", "rate": 5.50}
#             ]
#           }
#         }

#         Analyze the document and provide ONLY the JSON object. Do not include any explanatory text or markdown formatting.
#         """

#     response = model.generate_content(
#         [
#             {
#                 "role": "user",
#                 "parts": [
#                     {"text": prompt},
#                     {
#                         "inline_data": {
#                             "mime_type": "application/pdf",
#                             "data": encoded_file,
#                         }
#                     },
#                 ],
#             }
#         ]
#     )

#     try:
#         gemini_output = response.candidates[0].content.parts[0].text
#         return json.loads(gemini_output)
#     except Exception as e:
#         raise ValueError(f"Gemini returned invalid JSON: {response}") from e


# @celery_app.task(name="tasks.parse_digital_pdf")
# def parse_digital_pdf_task(bill_id: str):
#     logger.info(f"Worker received task: Parse PDF for bill_id: {bill_id}")

#     async def main():
#         async with db.session_context() as session:
#             try:
#                 bill_uuid = uuid.UUID(bill_id)
#                 bill = await bill_repository.get(db=session, bill_id=bill_uuid)
#                 if not bill:
#                     logger.error(f"Bill {bill_id} not found")
#                     return

#                 # Download from S3 → temp file
#                 local_file_path = s3_service.download_file(bill.file_uri)

#                 raw_parsed_data = gemini_pdf_parser(local_file_path)
#                 normalized_data = NormalizedBillSchema.model_validate(raw_parsed_data)

#                 # Compute checksum
#                 with open(local_file_path, "rb") as f:
#                     checksum = "sha256:" + hashlib.sha256(f.read()).hexdigest()

#                 update_data = {
#                     "parse_status": BillStatus.SUCCESS,
#                     "provider": normalized_data.discom,
#                     "billing_period_start": normalized_data.period.start,
#                     "billing_period_end": normalized_data.period.end,
#                     "kwh_total": normalized_data.consumption.total_kwh,
#                     "cost_total": normalized_data.totals.cost,
#                     "normalized_json": normalized_data.model_dump(mode="json"),
#                     "parser_version": normalized_data.version,
#                     "checksum": checksum,
#                 }

#                 await bill_repository.update(
#                     db=session, bill=bill, fields_to_update=update_data
#                 )
#                 logger.info(f"Successfully parsed and updated bill: {bill_id}")

#                 await cache_service.invalidate(BillResponse, bill_uuid)

#             except Exception as e:
#                 logger.error(f"Failed to parse bill {bill_id}: {e}", exc_info=True)
#                 async with db.session_context() as error_session:
#                     bill = await bill_repository.get(
#                         error_session, bill_id=uuid.UUID(bill_id)
#                     )
#                     if bill:
#                         await bill_repository.update(
#                             db=error_session,
#                             bill=bill,
#                             fields_to_update={"parse_status": BillStatus.FAILED},
#                         )
#                         await cache_service.invalidate(BillResponse, uuid.UUID(bill_id))

#     asyncio.run(main())

# app/tasks/parsing_tasks.py
import logging
import uuid
import asyncio
import os
import hashlib

from src.app.core.celery_app import celery_app
from src.app.db.session import db
from src.app.crud.bill_crud import bill_repository
from src.app.schemas.bill_schema import NormalizedBillSchema, BillResponse
from src.app.models.bill_model import BillStatus
from src.app.services.cache_service import cache_service
from src.app.services.s3_service import s3_service
from src.app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.parse_digital_pdf")
def parse_digital_pdf_task(bill_id: str, mime_type: str = "application/pdf"):
    """Celery task to parse a PDF/image bill using Gemini, update the database, and trigger next steps."""
    logger.info(f"Worker received task: Parse document for bill_id: {bill_id}")
    local_file_path = None

    async def main():
        nonlocal local_file_path
        async with db.session_context() as session:
            try:
                bill_uuid = uuid.UUID(bill_id)
                bill = await bill_repository.get(db=session, bill_id=bill_uuid)
                if not bill:
                    logger.error(f"Bill {bill_id} not found")
                    return

                # 1. Download file from S3 to a temporary local path
                local_file_path = s3_service.download_file(bill.file_uri)

                # 2. Call our AI service to parse the file
                raw_parsed_data = ai_service.parse_bill_with_gemini(
                    local_file_path, mime_type
                )

                # 3. Validate the AI's output against our strict schema
                normalized_data = NormalizedBillSchema.model_validate(raw_parsed_data)

                # 4. Compute checksum of the local file
                with open(local_file_path, "rb") as f:
                    checksum = "sha256:" + hashlib.sha256(f.read()).hexdigest()

                # 5. Prepare the data for database update
                update_data = {
                    "parse_status": BillStatus.SUCCESS,
                    "provider": normalized_data.discom,
                    "billing_period_start": normalized_data.period.start,
                    "billing_period_end": normalized_data.period.end,
                    "kwh_total": normalized_data.consumption.total_kwh,
                    "cost_total": normalized_data.totals.get(
                        "cost"
                    ),  # Corrected access
                    "normalized_json": normalized_data.model_dump(mode="json"),
                    "parser_version": normalized_data.version,
                    "checksum": checksum,
                }

                await bill_repository.update(
                    db=session, bill=bill, fields_to_update=update_data
                )
                logger.info(f"Successfully parsed and updated bill: {bill_id}")

                await cache_service.invalidate(BillResponse, bill_uuid)
                # estimate_appliances_for_bill_task.delay(bill_id)

            except Exception as e:
                logger.error(f"Failed to parse bill {bill_id}: {e}", exc_info=True)
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
            finally:
                # 6. CRITICAL: Clean up the temporary file
                if local_file_path and os.path.exists(local_file_path):
                    os.remove(local_file_path)

    asyncio.run(main())
