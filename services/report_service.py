"""Fraud reports management service.

Handles user fraud report submissions, automatic promotion of reported entities
to the global fraud lookup database, and community points/milestone badges.
"""

from datetime import datetime
import uuid
from typing import List, Optional
from database.mongodb import get_db


async def submit_report(
    uid: str,
    entity_type: str,
    entity_value: str,
    scam_category: str,
    description: str,
) -> dict:
    """Submit a new fraud report from a user.

    Saves the report to the fraud_reports collection, updates or promotes the
    entity to the global fraud_database, increments user guardian points by 10,
    and awards milestone badges.

    Args:
        uid: The UID of the reporter (user).
        entity_type: The type of entity reported ('upi_id', 'phone_number', 'website', 'message').
        entity_value: The unique value representing the entity.
        scam_category: The category of scam.
        description: User's details of the scam event.

    Returns:
        dict: A dictionary containing report_id, points_awarded (10), and badges_earned.
    """
    db = get_db()
    report_id = str(uuid.uuid4())
    now = datetime.utcnow()

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

    # Insert report
    await db.fraud_reports.insert_one(report_doc)

    # Check and update/promote to fraud_database
    existing_fraud = await db.fraud_database.find_one({"entity_value": entity_value})
    if existing_fraud:
        await db.fraud_database.update_one(
            {"entity_value": entity_value},
            {
                "$inc": {"reports_count": 1},
                "$set": {"last_reported": now},
            },
        )
    else:
        total_entity_reports = await db.fraud_reports.count_documents({"entity_value": entity_value})
        if total_entity_reports >= 3:
            await db.fraud_database.update_one(
                {"entity_value": entity_value},
                {
                    "$setOnInsert": {
                        "entity_type": entity_type,
                        "entity_value": entity_value,
                        "scam_category": scam_category,
                        "confidence": 60,  # Default starting confidence for community-reported entities
                        "reports_count": total_entity_reports,
                        "last_reported": now,
                        "source": "community",
                    }
                },
                upsert=True,
            )

    # Award 10 guardian points to user
    await db.users.update_one(
        {"uid": uid},
        {"$inc": {"guardian_points": 10}, "$set": {"updated_at": now}},
    )

    # Check user report count for badges
    user_reports_count = await db.fraud_reports.count_documents({"reporter_uid": uid})
    new_badges = []
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
    """Retrieve a paginated list of community reports.

    Sorted in descending order of creation.

    Args:
        page: The page number (1-indexed).
        limit: The number of reports per page.
        entity_type: Optional filter for reported entity type.
        scam_category: Optional filter for scam category.

    Returns:
        List[dict]: A list of report dictionaries with serializable string _ids.
    """
    db = get_db()
    query = {}

    if entity_type:
        query["entity_type"] = entity_type
    if scam_category:
        query["scam_category"] = scam_category

    skip = (page - 1) * limit
    cursor = db.fraud_reports.find(query).sort("created_at", -1).skip(skip).limit(limit)

    reports = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # Ensure created_at is serialized cleanly
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        reports.append(doc)

    return reports
