# # app/tasks/insight_tasks.py

# import logging
# import uuid
# import asyncio
# from datetime import datetime

# from src.app.core.celery_app import celery_app
# from src.app.db.session import db
# from src.app.crud.bill_crud import bill_repository
# from src.app.crud.insight_crud import insight_repository
# from src.app.models.insight_model import Insight, InsightStatus
# from src.app.schemas.insight_schema import InsightRead, InsightKPIs, InsightApplianceBreakdown, InsightRecommendation

# logger = logging.getLogger(__name__)

# def _run_v1_rule_engine(context: dict) -> dict:
#     """
#     Our simple, V1 rule-based AI engine.
#     Takes the full context and generates the final InsightRead dictionary.
#     """
#     recommendations = []
#     # Rule 1: High consumption
#     if context["current_bill"].kwh_total > 400:
#         recommendations.append(InsightRecommendation(
#             priority=1, title="High Overall Consumption",
#             description="Your energy usage this month was high. Review your top appliances to find savings opportunities."
#         ))
        
#     # Rule 2: Trend analysis
#     kwh_change = None
#     cost_change = None
#     trend = "stable"
#     if context["previous_bill"]:
#         kwh_change = ((context["current_bill"].kwh_total - context["previous_bill"].kwh_total) / context["previous_bill"].kwh_total) * 100
#         cost_change = ((context["current_bill"].cost_total - context["previous_bill"].cost_total) / context["previous_bill"].cost_total) * 100
#         if kwh_change > 10:
#             trend = "increasing"
#             recommendations.append(InsightRecommendation(
#                 priority=2, title="Usage Increasing",
#                 description=f"Your consumption increased by {kwh_change:.0f}% compared to last month. Let's look at why."
#             ))
#         elif kwh_change < -10:
#             trend = "decreasing"

#     # Rule 3: Highest consumer
#     breakdown = []
#     highest_consumer = None
#     if context["estimates"]:
#         # ... logic to calculate breakdown percentages ...
#         # For simplicity, let's create a placeholder
#         highest_consumer_estimate = max(context["estimates"], key=lambda x: x.estimated_kwh)
#         appliance_name = highest_consumer_estimate.user_appliance.custom_name
        
#         if (highest_consumer_estimate.estimated_kwh / context["current_bill"].kwh_total) > 0.4:
#              recommendations.append(InsightRecommendation(
#                 priority=1, title=f"Check Your {appliance_name}",
#                 description=f"Your '{appliance_name}' is responsible for a large portion of your bill. Ensure it's running efficiently."
#             ))

#     # Assemble the final JSON report using our Pydantic schemas
#     report = InsightRead(
#         bill_id=context["current_bill"].id,
#         generated_at=datetime.utcnow(),
#         kpis=InsightKPIs(
#             kwh_total=context["current_bill"].kwh_total,
#             cost_total=context["current_bill"].cost_total,
#             kwh_change_percent=kwh_change,
#             cost_change_percent=cost_change,
#             trend=trend,
#         ),
#         consumption_breakdown=breakdown, # You would build the breakdown list here
#         recommendations=recommendations,
#     )
#     return report.model_dump(mode="json")


# @celery_app.task(name="tasks.generate_insights")
# def generate_insights_task(bill_id: str):
#     """Celery task to generate insights for a bill."""
#     logger.info(f"Worker received task: Generate insights for bill_id: {bill_id}")

#     async def main():
#         async with db.session_context() as session:
#             try:
#                 bill_uuid = uuid.UUID(bill_id)
#                 insight = await insight_repository.get_by_bill_id(db=session, bill_id=bill_uuid)
#                 if not insight or insight.status != InsightStatus.PENDING:
#                     logger.warning(f"Insight generation not in pending state for bill {bill_id}. Skipping.")
#                     return

#                 # 1. Assemble the "Monthly Insight Context"
#                 current_bill = await bill_repository.get(db=session, bill_id=bill_uuid)
#                 # In a real implementation, you'd also fetch previous bills
#                 context = {
#                     "current_bill": current_bill,
#                     "previous_bill": await bill_repository.get_latest_by_user(db=session, user_id=current_bill.user_id), # Simplified
#                     "estimates": current_bill.estimates,
#                 }

#                 # 2. Run the rule engine to get the final JSON report
#                 report_json = _run_v1_rule_engine(context)
                
#                 # 3. Update the insight record with the result
#                 insight.structured_data = report_json
#                 insight.status = InsightStatus.COMPLETED
#                 session.add(insight)
#                 await session.commit()
#                 logger.info(f"Successfully generated insights for bill {bill_id}")

#             except Exception as e:
#                 logger.error(f"Failed to generate insights for bill {bill_id}: {e}", exc_info=True)
#                 # ... (error handling to set status to FAILED) ...

#     asyncio.run(main())