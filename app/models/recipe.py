from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, func
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    ingredients = Column(JSON, nullable=False)  # list of strings
    steps = Column(JSON, nullable=False)        # list of strings
    calories = Column(Float, nullable=True)
    time_minutes = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)
    detected_ingredients = Column(JSON, nullable=True)  # raw detected from image
    nutrition = Column(JSON, nullable=True)  # {"protein": x, "fat": x, "carbs": x}
    created_at = Column(DateTime, server_default=func.now())
