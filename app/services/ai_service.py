import json

import httpx

from app.config import get_settings
from app.core.logger import logger


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def analyze_comment(self, comment: str) -> dict:
        if not self.settings.openrouter_api_key:
            return self._fallback("AI API key is not configured")

        model = self.settings.openrouter_model or "openai/gpt-oss-20b:free"

        prompt = (
            "You are an assistant for a developer landing page backend API. "
            "Analyze the contact form comment. "
            "Return only valid JSON without markdown and without explanations. "
            "JSON fields: category, tone, priority, suggested_reply. "
            "category must be one of: job_offer, cooperation, question, complaint, other. "
            "tone must be one of: positive, neutral, negative. "
            "priority must be one of: low, medium, high. "
            f"Comment: {comment}"
        )

        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            content = data["choices"][0]["message"]["content"]
            parsed_result = self._parse_ai_response(content)

            return {
                "status": "success",
                "provider": "OpenRouter",
                "model": model,
                "result": parsed_result,
            }

        except Exception as error:
            logger.exception("AI service failed: %s", str(error))
            return self._fallback(str(error))

    def _parse_ai_response(self, content: str) -> dict:
        try:
            cleaned_content = content.strip()

            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content.replace("```json", "").replace("```", "").strip()
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content.replace("```", "").strip()

            return json.loads(cleaned_content)

        except Exception:
            logger.warning("AI response is not valid JSON: %s", content)

            return {
                "category": "other",
                "tone": "neutral",
                "priority": "medium",
                "suggested_reply": content,
            }

    def _fallback(self, reason: str) -> dict:
        return {
            "status": "fallback",
            "provider": "local",
            "reason": reason,
            "result": {
                "category": "other",
                "tone": "neutral",
                "priority": "medium",
                "suggested_reply": "Спасибо за обращение. Я свяжусь с вами после обработки заявки.",
            },
        }