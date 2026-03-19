"""
주간 식단 계획 라우터
"""
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.utils.auth import get_current_user
from app.models.user import User
from app.config import config

router = APIRouter(prefix="/meal-plan", tags=["식단 계획"])


class MealPlanRequest(BaseModel):
    dietary_restrictions: Optional[List[str]] = []  # 채식, 글루텐프리, 저탄고지 등
    health_goals: Optional[str] = None  # 다이어트, 근육 증가, 유지
    servings: int = 2
    days: int = 7


class DayMeal(BaseModel):
    day: str
    breakfast: str
    lunch: str
    dinner: str
    snack: Optional[str] = None
    calories_estimate: int


class MealPlanResponse(BaseModel):
    plan: List[DayMeal]
    shopping_list: List[str]
    tips: List[str]


@router.post("/generate", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: MealPlanRequest,
    current_user: User = Depends(get_current_user),
):
    """AI 주간 식단 계획 생성"""
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    restrictions_text = ", ".join(request.dietary_restrictions) if request.dietary_restrictions else "없음"

    prompt = f"""한국 가정식 위주로 {request.days}일 식단 계획을 세워줘.

조건:
- 식이 제한: {restrictions_text}
- 건강 목표: {request.health_goals or "균형 잡힌 식사"}
- 인원: {request.servings}명

JSON 형식으로 반환 (마크다운 없이 순수 JSON):
{{
  "plan": [
    {{
      "day": "월요일",
      "breakfast": "메뉴명",
      "lunch": "메뉴명",
      "dinner": "메뉴명",
      "snack": "간식",
      "calories_estimate": 2000
    }}
  ],
  "shopping_list": ["재료1", "재료2"],
  "tips": ["팁1", "팁2"]
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            start = text.find("{")
            end = text.rfind("}") + 1
            text = text[start:end]
        data = json.loads(text)
        return MealPlanResponse(**data)
    except Exception:
        raise HTTPException(500, "식단 계획 생성 중 오류가 발생했습니다")
