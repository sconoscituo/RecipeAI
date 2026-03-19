from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import users, recipes, payments
from app.config import config
from app.middleware.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=config.APP_NAME,
    description="냉장고 재료 사진 → AI 레시피 추천 서비스",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(users.router)
app.include_router(recipes.router)
app.include_router(payments.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": config.APP_NAME}
