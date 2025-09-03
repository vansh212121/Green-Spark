# app/services/ai_service.py
import logging
import json
import google.generativeai as genai
from src.app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        genai.configure(api_key=settings.API_KEY)
        self.model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )  # Use a fast, multi-modal model
        self.prompt = self._build_prompt()

    def _build_prompt(self) -> str:
        # This is our "Golden Prompt". It instructs the AI on exactly what to do.
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

    def parse_bill_with_gemini(self, file_path: str, mime_type: str) -> dict:
        """Takes a local file path to an image/pdf, sends it to Gemini, and returns the structured JSON data."""
        logger.info(f"Sending file to Gemini for parsing: {file_path}")
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        image_part = {"mime_type": mime_type, "data": file_bytes}

        prompt_part = self.prompt

        try:
            response = self.model.generate_content([prompt_part, image_part])
            # Clean up the response to get just the JSON
            gemini_output = (
                response.text.strip().replace("```json", "").replace("```", "").strip()
            )
            return json.loads(gemini_output)
        except Exception as e:
            logger.error(
                f"Gemini returned an invalid or unexpected response: {response.text}",
                exc_info=True,
            )
            raise ValueError(f"Gemini returned invalid data") from e


# Singleton instance
ai_service = AIService()
