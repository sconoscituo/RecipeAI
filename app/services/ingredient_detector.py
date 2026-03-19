import base64
import json
import re
from typing import Optional
import google.generativeai as genai
from app.config import config

genai.configure(api_key=config.GEMINI_API_KEY)


async def detect_ingredients(image_bytes: bytes, mime_type: str = "image/jpeg") -> list[str]:
    """이미지에서 식재료 감지"""
    if not config.GEMINI_API_KEY:
        # API 키 없을 때 더미 데이터 반환
        return ["당근", "양파", "감자", "계란", "마늘"]

    model = genai.GenerativeModel("gemini-1.5-flash")
    image_data = base64.b64encode(image_bytes).decode()
    response = model.generate_content([
        {"mime_type": mime_type, "data": image_data},
        "이 이미지에서 식재료를 모두 찾아서 한국어로 리스트로 답해주세요. "
        "JSON 형식으로만 답하세요: {\"ingredients\": [\"재료1\", \"재료2\"]}"
    ])

    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())["ingredients"]
        except (json.JSONDecodeError, KeyError):
            pass
    return []
