"""
FraudShield AI — Safety Alerts Router
========================================
Provides endpoints to list, view, and publish safety alerts from
regulatory agencies (RBI, NPCI) or localised scam campaigns.
Admin-only creation protected by ``X-Admin-Key`` header.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.database.mongo import get_db
from backend.services.alert_service import create_alert, get_alerts

logger = logging.getLogger(__name__)
router = APIRouter()


class AlertCreate(BaseModel):
    """Schema for creating a new safety alert."""

    title: str = Field(..., min_length=2, description="Heading of the alert")
    body: str = Field(..., min_length=5, description="Full details of the alert")
    category: str = Field(..., description="Category (rbi/npci/city/scam_type)")
    city: Optional[str] = Field(None, description="Optional city focus")


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get paginated safety alerts",
)
async def list_alerts(
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Retrieve a paginated list of safety alerts sorted by creation date."""
    alerts = await get_alerts(
        page=page,
        limit=limit,
        category=category,
        city=city,
    )

    return {
        "success": True,
        "data": alerts,
        "message": "Alerts list retrieved successfully.",
    }


@router.get(
    "/{alert_id}",
    status_code=status.HTTP_200_OK,
    summary="Get specific alert detail",
)
async def get_alert_detail(alert_id: str):
    """Fetch complete details of a specific safety alert."""
    db = get_db()

    alert_doc = await db.alerts.find_one({"alert_id": alert_id})
    if not alert_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Alert not found.",
                "code": "ALERT_NOT_FOUND",
            },
        )

    alert_doc["_id"] = str(alert_doc["_id"])
    if "created_at" in alert_doc and isinstance(
        alert_doc["created_at"], datetime
    ):
        alert_doc["created_at"] = alert_doc["created_at"].isoformat()

    return {
        "success": True,
        "data": alert_doc,
        "message": "Alert details retrieved successfully.",
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new alert (Admin only)",
)
async def publish_new_alert(
    payload: AlertCreate,
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
):
    """Publish a new safety alert.  Requires ``X-Admin-Key`` header."""
    admin_key_env = os.getenv(
        "ADMIN_KEY", "any-secret-string-for-admin-routes"
    )

    if not x_admin_key or x_admin_key != admin_key_env:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": "Invalid or missing X-Admin-Key header.",
                "code": "FORBIDDEN",
            },
        )

    alert_id = await create_alert(
        title=payload.title,
        body=payload.body,
        category=payload.category,
        city=payload.city,
    )

    logger.info("Admin published alert: %s", alert_id)

    return {
        "success": True,
        "data": {"alert_id": alert_id},
        "message": "Alert published successfully.",
    }
