"""Alert management service.

Handles queries for safety alerts issued by agencies (like RBI, NPCI) or
localized scams, and insertion of new alerts.
"""

from datetime import datetime
import uuid
from typing import List, Optional
from database.mongodb import get_db


async def get_alerts(
    page: int,
    limit: int,
    category: Optional[str] = None,
    city: Optional[str] = None,
) -> List[dict]:
    """Retrieve a paginated list of fraud/safety alerts.

    Sorted in descending order of creation.

    Args:
        page: The page number (1-indexed).
        limit: The number of alerts to retrieve per page.
        category: Optional filter for alert category (e.g. 'rbi', 'npci').
        city: Optional filter for a specific city.

    Returns:
        List[dict]: A list of alert dictionaries with serializable string _ids.
    """
    db = get_db()
    query = {}

    if category:
        query["category"] = category
    if city:
        query["city"] = city

    skip = (page - 1) * limit
    cursor = db.alerts.find(query).sort("created_at", -1).skip(skip).limit(limit)

    alerts = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        # Ensure created_at is serialized cleanly
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
        title: The headline of the alert.
        body: The detailed content body.
        category: The category of the alert (e.g. 'rbi', 'npci', 'city', 'scam_type').
        city: Optional city filter for localized alerts.

    Returns:
        str: The generated UUID4 alert_id.
    """
    db = get_db()
    alert_id = str(uuid.uuid4())

    alert_doc = {
        "alert_id": alert_id,
        "title": title,
        "body": body,
        "category": category,
        "created_at": datetime.utcnow(),
    }

    if city:
        alert_doc["city"] = city

    await db.alerts.insert_one(alert_doc)
    return alert_id
