from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.models.recipe import Recipe
from app.models.favorite import Favorite
from app.utils.auth import get_current_user
from app.services.ingredient_detector import detect_ingredients
from app.services.recipe_generator import generate_recipes, calculate_nutrition
from app.config import config

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


class RecipeOut(BaseModel):
    id: int
    title: str
    ingredients: list
    steps: list
    calories: Optional[float]
    time_minutes: Optional[int]
    image_url: Optional[str]
    detected_ingredients: Optional[list]
    nutrition: Optional[dict]

    class Config:
        from_attributes = True


def check_daily_limit(user: User):
    today = str(date.today())
    if user.last_usage_date != today:
        user.daily_usage = 0
        user.last_usage_date = today
    if not user.is_premium and user.daily_usage >= config.FREE_DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"무료 플랜은 하루 {config.FREE_DAILY_LIMIT}회까지 가능합니다. 프리미엄으로 업그레이드하세요.",
        )


@router.post("/analyze", response_model=list[RecipeOut], status_code=status.HTTP_201_CREATED)
async def analyze_and_generate(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_daily_limit(current_user)

    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"

    ingredients = await detect_ingredients(image_bytes, mime_type)
    if not ingredients:
        raise HTTPException(status_code=422, detail="이미지에서 식재료를 인식할 수 없습니다.")

    recipes_data = await generate_recipes(ingredients)
    saved_recipes = []

    for r in recipes_data:
        nutrition = await calculate_nutrition(r.get("ingredients", []), r.get("calories", 0))
        recipe = Recipe(
            user_id=current_user.id,
            title=r["title"],
            ingredients=r.get("ingredients", []),
            steps=r.get("steps", []),
            calories=r.get("calories"),
            time_minutes=r.get("time_minutes"),
            detected_ingredients=ingredients,
            nutrition=nutrition,
        )
        db.add(recipe)
        saved_recipes.append(recipe)

    current_user.daily_usage += 1
    await db.commit()
    for r in saved_recipes:
        await db.refresh(r)

    return saved_recipes


@router.get("/", response_model=list[RecipeOut])
async def list_recipes(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe).where(Recipe.user_id == current_user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.user_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.user_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
    await db.delete(recipe)
    await db.commit()


@router.post("/{recipe_id}/favorite", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fav = Favorite(user_id=current_user.id, recipe_id=recipe_id)
    db.add(fav)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="이미 즐겨찾기에 추가되어 있습니다.")
    return {"message": "즐겨찾기에 추가되었습니다."}


@router.delete("/{recipe_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        delete(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.recipe_id == recipe_id,
        )
    )
    await db.commit()


@router.get("/favorites/list", response_model=list[RecipeOut])
async def list_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe)
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .where(Favorite.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{recipe_id}/shopping-list")
async def get_shopping_list(
    recipe_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.user_id == current_user.id)
    )
    recipe = result.scalar_one_or_none()
    if not recipe:
        raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
    return {
        "recipe_title": recipe.title,
        "shopping_list": recipe.ingredients,
    }
