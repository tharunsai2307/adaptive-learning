"""
FastAPI application entry point for AdaptiveLearn.

Run with:  uvicorn backend.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import create_tables
from .routes import all_routers
from .seed_data import seed_demo_data

app = FastAPI(
    title="AdaptiveLearn API",
    description="AI-Based Personalized Learning System with Q-Learning",
    version="1.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
for router in all_routers:
    app.include_router(router)


@app.on_event("startup")
def on_startup():
    """Create tables and seed demo data on first run."""
    create_tables()
    seed_demo_data()


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
