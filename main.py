"""Main FastAPI application entry point.

Configures database connection lifespan, CORS middleware, Cloudinary SDK
initialization, and core API routing.
"""

import os
from contextlib import asynccontextmanager
import cloudinary
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb import close_db, connect_db

from routes import auth, fraud, history, reports, payments, alerts, community

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycles."""
    # Connect to MongoDB
    await connect_db()

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )

    yield

    # Clean up DB connection
    await close_db()


app = FastAPI(
    title="FraudShield AI API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Format HTTPExceptions to return the standard JSON error structure."""
    if isinstance(exc.detail, dict) and "success" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers=exc.headers
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": str(exc.detail),
            "code": "HTTP_ERROR"
        },
        headers=exc.headers
    )


@app.get("/health")
async def health_check():
    """Retrieve service health status.

    Returns:
        dict: A dictionary indicating status is ok and identifying the service.
    """
    return {"status": "ok", "service": "FraudShield AI Backend"}


# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(fraud.router, prefix="/fraud", tags=["Fraud Detection"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(community.router, prefix="/community", tags=["Community"])

