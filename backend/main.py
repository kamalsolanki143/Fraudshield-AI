"""
FraudShield AI — FastAPI Application Entry Point
===================================================
Production-ready application server with:

  • CORS middleware for cross-origin frontend communication
  • MongoDB connection lifecycle management (startup / shutdown)
  • Cloudinary SDK initialisation
  • All API routers mounted under ``/api`` prefix
  • Health check endpoint
  • Global exception handling
  • Professional logging configuration
  • OpenAPI metadata

Run with::

    cd backend
    uvicorn main:app --reload --port 5000
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — ensure 'backend' is importable as a package.
# The Gemini service uses absolute imports like
# ``from backend.prompts.fraud_prompt import ...`` which require the
# project root (parent of backend/) to be on sys.path.
# ---------------------------------------------------------------------------
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import cloudinary
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database.mongo import close_db, connect_db
from backend.database.redis import close_redis, connect_redis
from backend.routes import auth, fraud, history, reports, payments, alerts, community

load_dotenv()

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("fraudshield")


# ---------------------------------------------------------------------------
# Application lifespan (startup + shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown lifecycle events."""
    # ---- Startup ----
    logger.info("🚀 Starting FraudShield AI Backend...")

    await connect_db()
    await connect_redis()

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )
    logger.info("☁️  Cloudinary configured")

    logger.info("✅ FraudShield AI Backend ready")

    yield

    # ---- Shutdown ----
    logger.info("🛑 Shutting down FraudShield AI Backend...")
    await close_db()
    await close_redis()
    logger.info("👋 Shutdown complete")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="FraudShield AI API",
    description=(
        "AI-powered fraud detection platform for Indian digital payments. "
        "Uses Gemini 1.5 Flash Vision to analyse screenshots and detect scams."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Format HTTPExceptions to the standard JSON error envelope."""
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers=exc.headers,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": str(exc.detail),
            "code": "HTTP_ERROR",
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal server error occurred.",
            "code": "INTERNAL_ERROR",
        },
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    """Retrieve service health status."""
    return {"status": "ok", "service": "FraudShield AI Backend", "version": "1.0.0"}


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint redirect to docs."""
    return {
        "service": "FraudShield AI Backend",
        "docs": "/docs",
        "health": "/health",
    }


# ---------------------------------------------------------------------------
# Mount routers — all under /api prefix to match frontend expectations
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(fraud.router, prefix="/api/fraud", tags=["Fraud Detection"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(community.router, prefix="/api/community", tags=["Community"])
