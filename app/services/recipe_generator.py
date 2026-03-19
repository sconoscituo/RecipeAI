import json
import re
import google.generativeai as genai
from app.config import config

genai.configure(api_key=config.GEMINI_API_KEY)


async def generate_recipes(ingredients: list[str]) -> list[dict]:
    """재료로 레시피 5개 생성"""
    if not config.GEMINI_API_KEY:
        return [
            {
                "title": "샘플 요리",
                "ingredients": [f"{ing} 적당량" for ing in ingredients[:3]],
                "steps": ["재료를 손질합니다.", "볶아서 완성합니다."],
                "calories": 350,
                "time_minutes": 20,
            }
        ]

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""재료: {', '.join(ingredients)}
이 재료들로 만들 수 있는 한국 요리 레시피 5개를 JSON으로 생성하세요.
반드시 JSON만 출력하세요:
{{
  "recipes": [
    {{
      "title": "요리명",
      "ingredients": ["재료1 양", "재료2 양"],
      "steps": ["단계1", "단계2", "단계3"],
      "calories": 300,
      "time_minutes": 20
    }}
  ]
}}"""

    response = model.generate_content(prompt)
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())["recipes"]
        except (json.JSONDecodeError, KeyError):
            pass
    return []


async def calculate_nutrition(ingredients: list[str], calories: float) -> dict:
    """영양소 자동 계산 (칼로리 기반 추정)"""
    return {
        "calories": calories,
        "protein_g": round(calories * 0.15 / 4, 1),
        "fat_g": round(calories * 0.30 / 9, 1),
        "carbs_g": round(calories * 0.55 / 4, 1),
    }
