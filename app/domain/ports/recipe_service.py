"""
헥사고날 아키텍처 - RecipeAI Service Port
레시피 생성 도메인 서비스 추상 인터페이스
"""
from abc import abstractmethod
from typing import Any, Dict, List

from .base_service import AbstractService


class AbstractRecipeService(AbstractService):
    """레시피 AI 서비스 포트 - 구현체는 이 인터페이스를 따라야 함"""

    @abstractmethod
    async def generate_recipe(
        self,
        ingredients: List[str],
        preferences: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        재료 목록으로 AI 레시피 생성
        :param ingredients: 사용 가능한 재료 목록
        :param preferences: 식이 제한, 선호 요리 스타일 등
        :return: 생성된 레시피 (재료, 조리법, 시간 등)
        """
        ...

    @abstractmethod
    async def analyze_ingredients(
        self,
        image_url: str,
    ) -> List[str]:
        """
        음식/재료 이미지에서 재료 목록 추출
        :param image_url: 분석할 이미지 URL 또는 base64
        :return: 감지된 재료 이름 목록
        """
        ...

    @abstractmethod
    async def get_nutrition_info(
        self,
        recipe: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        레시피의 영양 정보 계산
        :param recipe: 레시피 데이터 (재료, 분량 포함)
        :return: 칼로리, 탄수화물, 단백질, 지방 등 영양 정보
        """
        ...
