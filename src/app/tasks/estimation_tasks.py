# app/tasks/estimation_tasks.py

import logging
import uuid
import asyncio

from src.app.core.celery_app import celery_app
from src.app.crud.appliance_crud import appliance_repository
from src.app.crud.bill_crud import bill_repository
from src.app.models.bill_model import Bill
from src.app.models.appliance_model import ApplianceEstimate
from src.app.core.config import settings
from src.app.db.session import Database
from src.app.tasks.insights_task import generate_insights_task

logger = logging.getLogger(__name__)

async def _perform_estimation_for_bill(session, bill: Bill):
    """
    The core estimation logic. Takes a Bill object and calculates the
    appliance estimates for it based on the inventory ATTACHED to that specific bill.
    """
    actual_total_kwh = bill.kwh_total

    appliances_for_this_bill, _ = await appliance_repository.get_by_bills(
        db=session,
        bill_id=bill.id,
        skip=0,
        limit=100,
        order_by="created_at",
        order_desc=True,
    )

    if not appliances_for_this_bill:
        logger.info(
            f"Bill {bill.id} has no appliances in its inventory. Skipping estimation."
        )
        return

    # 2. Calculate total theoretical kWh from this bill's inventory
    theoretical_consumptions = []
    total_theoretical_kwh = 0.0
    billing_days = (bill.billing_period_end - bill.billing_period_start).days or 30

    for appliance in appliances_for_this_bill:
        # For a bill-specific appliance, the wattage is required.
        wattage = appliance.custom_wattage
        if not wattage:
            continue

        theoretical_kwh = (
            wattage
            * appliance.hours_per_day
            * appliance.days_per_week
            / 7
            * billing_days
        ) / 1000.0
        theoretical_consumptions.append(
            {"appliance": appliance, "kwh": theoretical_kwh}
        )
        total_theoretical_kwh += theoretical_kwh

    if total_theoretical_kwh == 0:
        logger.warning(
            f"Total theoretical consumption is 0 for bill {bill.id}. Cannot scale estimates."
        )
        # We should still clear old estimates in this case.
        delete_statement = ApplianceEstimate.__table__.delete().where(
            ApplianceEstimate.bill_id == bill.id
        )
        await session.execute(delete_statement)
        await session.commit()
        return

    # 3. Calculate the proportional scaling factor
    scaling_factor = actual_total_kwh / total_theoretical_kwh

    # 4. Delete any old estimates for this bill to ensure a clean slate
    delete_statement = ApplianceEstimate.__table__.delete().where(
        ApplianceEstimate.bill_id == bill.id
    )
    await session.execute(delete_statement)

    # 5. Create and save new ApplianceEstimate objects
    new_estimates = []
    avg_cost_per_kwh = bill.cost_total / bill.kwh_total if bill.kwh_total > 0 else 0

    for item in theoretical_consumptions:
        appliance = item["appliance"]
        scaled_kwh = item["kwh"] * scaling_factor
        estimated_cost = scaled_kwh * avg_cost_per_kwh

        new_estimates.append(
            ApplianceEstimate(
                bill_id=bill.id,
                user_appliance_id=appliance.id,
                estimated_kwh=scaled_kwh,
                estimated_cost=estimated_cost,
            )
        )

    session.add_all(new_estimates)
    await session.commit()
    logger.info(
        f"Successfully calculated and saved {len(new_estimates)} appliance estimates for bill {bill.id}"
    )

    # 6. Trigger the next step in the pipeline (when we build it)
    generate_insights_task.delay(str(bill.id), str(bill.user_id))


@celery_app.task(name="tasks.estimate_appliances_for_bill")
def estimate_appliances_for_bill_task(bill_id: str):
    """
    Celery task to run estimation for a single bill.
    This task is self-contained: it creates its own DB connection and async loop.
    """
    logger.info(f"Worker received task: Estimate appliances for bill_id: {bill_id}")

    # This is our self-contained async entry point
    async def main():
        # 1. Create a NEW, LOCAL Database instance for this task run.
        local_db = Database(str(settings.DATABASE_URL))

        # 2. Connect and get a session from this new local instance.
        await local_db.connect()
        async with local_db.session_context() as session:
            try:
                bill = await bill_repository.get(db=session, bill_id=uuid.UUID(bill_id))
                if bill:
                    # 3. Pass the session to our core logic function.
                    await _perform_estimation_for_bill(session, bill)
            finally:
                # 4. CRITICAL: Always disconnect from the database when done.
                await local_db.disconnect()

    # 5. Run the self-contained async main function.
    asyncio.run(main())
