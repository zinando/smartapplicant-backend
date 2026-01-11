from django.core.management.base import BaseCommand
from api.ai import get_structured_data_from_gemini, call_gemini_smart, get_available_models


class Command(BaseCommand):
    help = "Test AI response for given prompt"

    # def add_arguments(self, parser):
    #     parser.add_argument('prompt', type=str, help='The prompt to send to the AI')

    def handle(self, *args, **kwargs):
        user_message = "I ordered a face cream last week and my skin is now burning and red."
        prompt = """You are an API, not a chatbot.

Your task is to analyze the input and return ONLY a valid JSON object that follows the schema below.
Do NOT add explanations, comments, markdown, or natural language.
Do NOT wrap the JSON in code blocks.
Do NOT return anything except JSON.

SCHEMA:
{
  "query": string,
  "intent": {
    "primary": string,
    "secondary": [string]
  },
  "entities": [
    {
      "type": string,
      "value": string,
      "confidence": number
    }
  ],
  "sentiment": {
    "overall": "positive" | "neutral" | "negative",
    "score": number
  },
  "urgency": {
    "level": "low" | "medium" | "high",
    "reason": string
  },
  "customer_stage": "lead" | "buyer" | "support" | "churn_risk",
  "suggested_actions": [
    {
      "action": string,
      "priority": number,
      "description": string
    }
  ],
  "response_guidelines": {
    "tone": string,
    "must_include": [string],
    "must_avoid": [string]
  }
}

RULES:
- Every field must be present.
- Numbers must be between 0 and 1 where applicable.
- If something is unknown, infer the most likely value.
- Do not leave any field empty.

INPUT:
{{USER_MESSAGE}}
""".strip().replace("{{USER_MESSAGE}}", user_message)
        response = call_gemini_smart(prompt)
        self.stdout.write(f"AI Response:\n{response}")