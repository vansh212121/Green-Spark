import logging
import json
import google.generativeai as genai
from src.app.core.config import settings
from src.app.schemas.insights_schema import InsightResponse

# InsightResponee
from src.app.schemas.bill_schema import NormalizedBillSchema

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        # Correctly use GEMINI_API_KEY from our settings
        genai.configure(api_key=settings.API_KEY)
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"},
        )
        # Initialize both prompts when the service is created
        self.parser_prompt = self._build_parser_prompt()
        self.insight_prompt = self._build_insight_prompt()

    def _build_parser_prompt(self) -> str:
        """This prompt instructs the AI to act as a document parser."""
        return """
        You are an expert document analysis AI. Your task is to analyze the provided image or PDF of an Indian electricity bill and extract the key information into a structured JSON format. 
        
        The required JSON output schema is:
        {
          "version": "gemini-1.5",
          "discom": "Name of the electricity provider",
          "account": {
            "consumer_id": "The Consumer or Account ID",
            "meter_id": "The Meter Number (if available)",
            "name": "The name on the bill",
            "address": "The service address on the bill"
          },
          "period": {
            "start": "YYYY-MM-DD format",
            "end": "YYYY-MM-DD format",
            "bill_date": "YYYY-MM-DD format",
            "due_date": "YYYY-MM-DD format"
          },
          "consumption": {
            "readings": {"previous": 1234.0, "current": 1345.0},
            "total_kwh": 111.0
          },
          "charges_breakdown": [
            {"name": "Fixed Charge", "amount": 150.0},
            {"name": "Energy Charge", "amount": 800.50}
            // Add ALL other charges as items in this list
          ],
          "billing_summary": {
            "net_current_demand": 1200.0,
            "subsidy": 0.0,
            "arrears": 0.0,
            "adjustments": 0.0,
            "total_payable": 1200.0
          },
          "totals": {"cost": 1200.0, "currency": "INR"},
          "tariff": {
            "plan_code": "The tariff plan code/name",
            "slabs": [
              {"description": "0-100 kWh", "rate": 3.50},
              {"description": "101-200 kWh", "rate": 5.50}
            ]
          }
        }

        Analyze the document and provide ONLY the JSON object. Do not include any explanatory text or markdown formatting.
        """

    def _build_insight_prompt(self) -> str:
        """This prompt instructs the AI to act as a data analyst."""
        return """
                
        You are "Sparky", an expert AI energy analyst for the GreenSpark application.

        Your task is to analyze a user's electricity consumption data for a specific month and provide clear, actionable insights.



        You will be given a JSON object containing the user's "Monthly Insight Context".

        This includes the current bill, the previous bill (if available) for comparison,

        and a detailed breakdown of appliance energy estimates.



        Based on the provided data context, your goal is to generate a JSON response

        that strictly adheres to the following Pydantic schema structure.

        Do not add any fields not present in the schema.



        SCHEMA:

        class InsightKPIs(BaseModel):

            kwh_total: float

            cost_total: float

            kwh_change_percent: Optional[float]

            cost_change_percent: Optional[float]

            trend: str # must be one of ["increasing", "decreasing", "stable"]



        class InsightApplianceBreakdown(BaseModel):

            appliance_name: str

            estimated_kwh: float

            percentage_of_total: float



        class InsightRecommendation(BaseModel):

            priority: int # 1 for high, 2 for medium, 3 for low

            title: str

            description: str
            savings: str  # e.g., "Save ₹250/month" or "Costing ~₹220 more"
            effort: str   # one of ["Easy", "Moderate", "High investment", "One-time investment", "Awareness", "Varies"]
            impact: str   # one of ["High", "Medium", "Low", "Long-term", "Varies"]


        class InsightResponse(BaseModel):

            bill_id: str # The UUID of the current bill

            generated_at: str # Current UTC datetime in ISO 8601 format
            kpis: InsightKPIs

            consumption_breakdown: List[InsightApplianceBreakdown]

            recommendations: List[InsightRecommendation]



        INSTRUCTIONS:

        1. If the previous bill is not provided, set `kwh_change_percent` and

            `cost_change_percent` to null, and `trend` to "stable".

        2. If the previous bill is provided, calculate percentage changes between

            current and previous. `trend` is "increasing" if kWh change > 5%,

            "decreasing" if < -5%, else "stable".
        - Also compare appliance-level estimates where possible:
            * For each appliance that exists in both months, calculate its change in kWh.
            * Highlight the top 1-2 appliances with the biggest increase in usage.

        3. Always calculate percentages and totals directly from the provided data.

            Round percentages to two decimal places.

        4. Build `consumption_breakdown` from appliance data, sorted by

            `estimated_kwh` in descending order.

        5. Generate 6-7 practical, personalized recommendations in `recommendations`.
        -   - Each recommendation must strictly include:
        -        * priority (1 = high, 2 = medium, 3 = low)
        -        * title (short, actionable, e.g., "Optimize AC Temperature")
        -        * description (why this matters, tied to data)
        -        * savings (quantified monthly INR savings, like "Save ₹250/month")
        -        * effort (one of: "Easy", "Moderate", "High investment", "One-time investment")
        -        * impact (one of: "High", "Medium", "Long-term")
        +   - Each recommendation must strictly include:
        +        * priority (1 = high, 2 = medium, 3 = low)
        +        * title (short, actionable, e.g., "Optimize AC Temperature")
        +        * description (why this matters, tied to data)
        +        * savings (quantified monthly INR savings, e.g. "Save ₹250/month" or for comparison insights, "Costing ~₹220 more")
        +        * effort (one of: "Easy", "Moderate", "High investment", "One-time investment", "Awareness")
        +        * impact (one of: "High", "Medium", "Low", "Long-term")


        6. In addition to actionable recommendations, always include at least 3 
        -   "comparison insight" that highlights how the current bill differs from 
        -   the previous month (e.g., "Your usage increased by 13% (40.5 kWh), costing ~₹220 more"). 
        -   This comparison insight should follow the same JSON structure as other recommendations.
        +   "comparison insights" that highlight how the current bill differs from 
        +   the previous month (e.g., "Your usage increased by 13% (40.5 kWh), costing ~₹220 more"). 
        +   These must follow the same JSON structure as recommendations, with proper `priority`, `savings`, `effort`, and `impact` values (no placeholders or "Varies").


        7. Return ONLY the final JSON object that validates against the `InsightResponse` schema.

        Do not include explanatory text, markdown formatting, or conversational notes.
        """

    def parse_bill_with_gemini(
        self, file_path: str, mime_type: str
    ) -> NormalizedBillSchema:
        """Takes a local file path to an image/pdf, sends it to Gemini, and returns a validated Pydantic schema object."""
        logger.info(f"Sending file to Gemini for parsing: {file_path}")
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        file_part = {"mime_type": mime_type, "data": file_bytes}

        try:
            # Use the specific prompt for parsing
            response = self.model.generate_content([self.parser_prompt, file_part])
            response_json = json.loads(response.text)

            # Validate the AI's output against our strict schema before returning
            return NormalizedBillSchema.model_validate(response_json)
        except Exception as e:
            logger.error(
                f"Gemini parsing or validation failed. Response text: {getattr(response, 'text', 'No response text available')}",
                exc_info=True,
            )
            raise ValueError("Failed to parse bill from AI response.") from e

    def generate_insights_from_context(self, context: dict) -> InsightResponse:
        """Takes the rich 'Monthly Insight Context' and sends it to Gemini to generate actionable insights."""
        logger.info("Sending monthly context to Gemini for insight generation...")

        # Use the specific prompt for insights
        full_prompt = [self.insight_prompt, json.dumps(context, default=str)]

        try:
            response = self.model.generate_content(full_prompt)
            response_json = json.loads(response.text)

            # Validate the AI's output against our strict schema before returning
            return InsightResponse.model_validate(response_json)
        except Exception as e:
            logger.error(
                f"Gemini insight generation or validation failed. Response text: {getattr(response, 'text', 'No response text available')}",
                exc_info=True,
            )
            raise ValueError(
                "Failed to generate valid insights from AI response."
            ) from e


# Singleton instance
ai_service = AIService()
