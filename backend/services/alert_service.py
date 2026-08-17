"""
FraudShield AI — Alert Management Service
============================================
Handles CRUD operations for safety alerts issued by regulatory bodies
(RBI, NPCI) or local scam-awareness campaigns.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.database.mongo import get_db

logger = logging.getLogger(__name__)


async def get_alerts(
    page: int,
    limit: int,
    category: Optional[str] = None,
    city: Optional[str] = None,
) -> List[dict]:
    """Retrieve a paginated list of fraud/safety alerts.

    Sorted in descending order of creation time.

    Args:
        page:     Page number (1-indexed).
        limit:    Number of alerts per page.
        category: Optional filter for alert category.
        city:     Optional filter for a specific city.

    Returns:
        A list of alert dictionaries with serialisable fields.
    """
    db = get_db()
    query: dict = {}

    if category:
        query["category"] = category
    if city:
        query["city"] = city

    skip = (page - 1) * limit
    cursor = (
        db.alerts.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    alerts: List[dict] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        alerts.append(doc)

    return alerts


async def create_alert(
    title: str,
    body: str,
    category: str,
    city: Optional[str] = None,
) -> str:
    """Create a new safety alert.

    Args:
        title:    The headline of the alert.
        body:     The detailed content body.
        category: Category label (e.g. ``rbi``, ``npci``, ``city``, ``scam_type``).
        city:     Optional city tag for localised alerts.

    Returns:
        The generated UUID4 ``alert_id``.
    """
    db = get_db()
    alert_id = str(uuid.uuid4())

    alert_doc: dict = {
        "alert_id": alert_id,
        "title": title,
        "body": body,
        "category": category,
        "created_at": datetime.now(timezone.utc),
    }

    if city:
        alert_doc["city"] = city

    await db.alerts.insert_one(alert_doc)
    logger.info("Created alert %s in category '%s'", alert_id, category)
    return alert_id
