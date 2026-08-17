"""
FraudShield AI — Fraud Reports Management Service
====================================================
Handles user-submitted fraud reports, automatic promotion of repeatedly
reported entities to the global fraud lookup database, and community
gamification (guardian points and milestone badges).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from backend.database.mongo import get_db

logger = logging.getLogger(__name__)


async def submit_report(
    uid: str,
    entity_type: str,
    entity_value: str,
    scam_category: str,
    description: str,
) -> dict:
    """Submit a new fraud report from a user.

    Saves the report, updates or promotes the entity to the global fraud
    database when the report threshold is reached, awards 10 guardian
    points, and checks for milestone badges.

    Args:
        uid:           The UID of the reporting user.
        entity_type:   Type of entity (``upi_id``, ``phone_number``, ``website``, ``message``).
        entity_value:  The unique value representing the entity.
        scam_category: Category label for the scam.
        description:   User's detailed description of the scam.

    Returns:
        A dict with ``report_id``, ``points_awarded``, and ``badges_earned``.
    """
    db = get_db()
    report_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    # Create the report document
    report_doc = {
        "report_id": report_id,
        "reporter_uid": uid,
        "entity_type": entity_type,
        "entity_value": entity_value,
        "scam_category": scam_category,
        "description": description,
        "verified": False,
        "upvotes": 0,
        "created_at": now,
    }

    await db.fraud_reports.insert_one(report_doc)
    logger.info("Report %s submitted by user %s", report_id, uid)

    # Check and update/promote to fraud_database
    existing_fraud = await db.fraud_database.find_one(
        {"entity_value": entity_value}
    )
    if existing_fraud:
        await db.fraud_database.update_one(
            {"entity_value": entity_value},
            {
                "$inc": {"reports_count": 1},
                "$set": {"last_reported": now},
            },
        )
    else:
        total_entity_reports = await db.fraud_reports.count_documents(
            {"entity_value": entity_value}
        )
        if total_entity_reports >= 3:
            await db.fraud_database.update_one(
                {"entity_value": entity_value},
                {
                    "$setOnInsert": {
                        "entity_type": entity_type,
                        "entity_value": entity_value,
                        "scam_category": scam_category,
                        "confidence": 60,
                        "reports_count": total_entity_reports,
                        "last_reported": now,
                        "source": "community",
                    }
                },
                upsert=True,
            )

    # Award 10 guardian points
    await db.users.update_one(
        {"uid": uid},
        {"$inc": {"guardian_points": 10}, "$set": {"updated_at": now}},
    )

    # Check for milestone badges
    user_reports_count = await db.fraud_reports.count_documents(
        {"reporter_uid": uid}
    )
    new_badges: List[str] = []
    if user_reports_count == 1:
        new_badges.append("Fraud Reporter")
    elif user_reports_count == 10:
        new_badges.append("Community Guardian")
    elif user_reports_count == 50:
        new_badges.append("Fraud Slayer")

    if new_badges:
        await db.users.update_one(
            {"uid": uid},
            {
                "$addToSet": {"badges": {"$each": new_badges}},
                "$set": {"updated_at": now},
            },
        )
        logger.info("User %s earned badges: %s", uid, new_badges)

    return {
        "report_id": report_id,
        "points_awarded": 10,
        "badges_earned": new_badges,
    }


async def get_reports(
    page: int,
    limit: int,
    entity_type: Optional[str] = None,
    scam_category: Optional[str] = None,
) -> List[dict]:
    """Retrieve a paginated list of community fraud reports.

    Sorted in descending order of creation time.

    Args:
        page:          Page number (1-indexed).
        limit:         Number of reports per page.
        entity_type:   Optional filter by entity type.
        scam_category: Optional filter by scam category.

    Returns:
        A list of report dictionaries with serialisable fields.
    """
    db = get_db()
    query: dict = {}

    if entity_type:
        query["entity_type"] = entity_type
    if scam_category:
        query["scam_category"] = scam_category

    skip = (page - 1) * limit
    cursor = (
        db.fraud_reports.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    reports: List[dict] = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        reports.append(doc)

    return reports
