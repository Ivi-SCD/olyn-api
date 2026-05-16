import json
import logging
import re

from groq import AsyncGroq

from app.core.config import settings
from app.core.exceptions import AIGenerationError

logger = logging.getLogger(__name__)


class GroqService:
    def __init__(self) -> None:
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def generate_itinerary(self, prompt: str) -> dict:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert local tourism specialist for Olinda, Pernambuco, Brazil. "
                            "You have deep knowledge of the city's history, culture, gastronomy, art, and attractions. "
                            "You MUST respond with valid JSON only — no markdown, no commentary."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            logger.error("Groq API call failed: %s", e)
            raise AIGenerationError(detail=str(e))

        raw = response.choices[0].message.content or ""
        return self._parse_json(raw)

    def _parse_json(self, raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            raise AIGenerationError(detail="LLM returned invalid JSON")
