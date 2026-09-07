"""
FastAPI application entry point for AdaptiveLearn.

Run with:  uvicorn backend.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import create_tables
from .routes import all_routers
from .seed_data import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed demo data on startup."""
    create_tables()
    seed_demo_data()
    yield


app = FastAPI(
    title="AdaptiveLearn API",
    description="AI-Based Personalized Learning System with Q-Learning",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — the Vite dev server proxies /api to this backend, so same-origin
# requests need no CORS at all. These origins are for direct calls.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://([a-z0-9-]+\.)*e2b\.app(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)


@app.get("/")
def root():
    return {
        "app": "AdaptiveLearn API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}
