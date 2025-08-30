# app/tasks/estimation_tasks.py

import logging
import uuid
import asyncio
from typing import List

from src.app.core.celery_app import celery_app
from src.app.db.session import db
from src.app.crud.appliance_crud import appliance_repository
from src.app.crud.bill_crud import bill_repository
from src.app.models.bill_model import Bill
from src.app.models.appliance_model import (
    UserAppliance,
    ApplianceEstimate,
    ApplianceCatalog,
)

# We might need the generate_insights_task to trigger it next
# from src.app.tasks.insight_tasks import generate_insights_task

logger = logging.getLogger(__name__)


async def _perform_estimation_for_bill(session, bill: Bill):
    """
    The core estimation logic. Takes a Bill object and calculates the
    appliance estimates for it.
    """
    user_id = bill.user_id
    actual_total_kwh = bill.kwh_total

    # 1. Get user's full appliance inventory
    appliances, _ = await appliance_repository.get_by_user(
        db=session,
        user_id=user_id,
        limit=500,
        skip=0,
        order_by="created_at",
        order_desc=True,
    )

    if not appliances:
        logger.info(
            f"User {user_id} has no appliances. Skipping estimation for bill {bill.id}."
        )
        return

    # 2. Calculate total theoretical kWh
    theoretical_consumptions = []
    total_theoretical_kwh = 0

    for appliance in appliances:
        # Prioritize custom wattage, but fall back to catalog's typical wattage
        wattage = appliance.custom_wattage
        if not wattage and appliance.appliance_catalog_id:
            catalog_item = await session.get(
                ApplianceCatalog, appliance.appliance_catalog_id
            )
            if catalog_item:
                wattage = catalog_item.typical_wattage

        if not wattage:
            continue

        # Simple estimation formula
        billing_days = (bill.billing_period_end - bill.billing_period_start).days
        theoretical_kwh = (
            wattage
            * appliance.hours_per_day
            * appliance.days_per_week
            / 7
            * billing_days
        ) / 1000
        theoretical_consumptions.append(
            {"appliance": appliance, "kwh": theoretical_kwh}
        )
        total_theoretical_kwh += theoretical_kwh

    if total_theoretical_kwh == 0:
        logger.warning(
            f"Total theoretical consumption is 0 for user {user_id}. Cannot scale estimates for bill {bill.id}."
        )
        return

    # 3. Calculate scaling factor
    scaling_factor = actual_total_kwh / total_theoretical_kwh

    # 4. Delete old estimates for this bill to ensure a clean slate
    #    In a production system, you might use a more advanced update/insert (upsert)
    for old_estimate in bill.estimates:
        await session.delete(old_estimate)
    await session.commit()

    # 5. Create and save new ApplianceEstimate objects
    for item in theoretical_consumptions:
        appliance = item["appliance"]
        scaled_kwh = item["kwh"] * scaling_factor

        # A simple cost estimate can be derived from the bill's average cost per kWh
        avg_cost_per_kwh = bill.cost_total / bill.kwh_total if bill.kwh_total > 0 else 0
        estimated_cost = scaled_kwh * avg_cost_per_kwh

        estimate_obj = ApplianceEstimate(
            bill_id=bill.id,
            user_appliance_id=appliance.id,
            estimated_kwh=scaled_kwh,
            estimated_cost=estimated_cost,
        )
        session.add(estimate_obj)

    await session.commit()
    logger.info(
        f"Successfully calculated and saved {len(theoretical_consumptions)} appliance estimates for bill {bill.id}"
    )

    # 6. Trigger the next step in the pipeline
    # generate_insights_task.delay(str(bill.id))


@celery_app.task(name="tasks.estimate_appliances")
def estimate_appliances_for_single_bill_task(bill_id: str):
    """Celery task to run estimation for one newly parsed bill."""
    logger.info(f"Worker received task: Estimate appliances for bill_id: {bill_id}")

    async def main():
        async with db.session_context() as session:
            bill = await bill_repository.get(db=session, bill_id=uuid.UUID(bill_id))
            if bill:
                await _perform_estimation_for_bill(session, bill)

    asyncio.run(main())


@celery_app.task(name="tasks.re_estimate_for_user")
def re_estimate_all_bills_for_user_task(user_id: str):
    """Celery task to re-run estimation for ALL of a user's bills."""
    logger.info(f"Worker received task: Re-estimate all bills for user_id: {user_id}")

    async def main():
        async with db.session_context() as session:
            # We don't need pagination here, we want all bills for the user
            bills, _ = await bill_repository.get_by_user(
                db=session, user_id=uuid.UUID(user_id), limit=1000
            )
            for bill in bills:
                await _perform_estimation_for_bill(session, bill)

    asyncio.run(main())
