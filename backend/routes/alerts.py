"""
FastAPI router for alert-related endpoints.
Prefix: /alerts
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.mongo import MongoClient
from services.alert_service import AlertService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AdvisoryCreate(BaseModel):
    source: str
    raw_title: str
    summary_en: list[str]
    summary_hi: list[str]
    severity: str


class TestCriticalRequest(BaseModel):
    user_id: str
    scam_type: str


firestore = MongoClient()
_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER"),
            smtp_pass=os.getenv("SMTP_PASS"),
        )
    return _alert_service


@router.get("/advisories")
async def get_advisories():
    try:
        docs = await firestore.get_recent_advisories(limit=10)
        return docs
    except Exception:
        logger.exception("Failed to fetch advisories")
        raise HTTPException(status_code=500, detail="Failed to fetch advisories")


@router.post("/advisory")
async def create_advisory(body: AdvisoryCreate):
    try:
        data = body.model_dump()
        adv_id = await firestore.save_advisory(data)
        if not adv_id:
            raise HTTPException(status_code=500, detail="Failed to save advisory")

        pushed_count = 0
        if body.severity == "HIGH":
            data["_id"] = adv_id
            pushed_count = await get_alert_service().push_advisory_alert(data)

        return {"advisory_id": adv_id, "pushed_count": pushed_count}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create advisory")
        raise HTTPException(status_code=500, detail="Failed to create advisory")


@router.get("/critical-reports")
async def get_critical_reports():
    try:
        cursor = firestore.critical_reports.find().sort("reported_at", -1).limit(20)
        docs = await cursor.to_list(length=20)
        result = []
        for d in docs:
            if d is None:
                continue
            d["_id"] = str(d["_id"])
            d.pop("user_id", None)
            result.append(d)
        return result
    except Exception:
        logger.exception("Failed to fetch critical reports")
        raise HTTPException(status_code=500, detail="Failed to fetch critical reports")


@router.post("/test-critical")
async def test_critical_alert(body: TestCriticalRequest):
    env = os.getenv("ENVIRONMENT", "development")
    if env != "development":
        raise HTTPException(status_code=403, detail="Only available in development mode")

    try:
        mock_result = {
            "risk_level": "HIGH",
            "confidence_score": 95,
            "scam_type": body.scam_type,
            "reasons_en": ["Suspicious UPI ID pattern detected"],
            "reasons_hi": ["संदिग्ध UPI ID पैटर्न पाया गया"],
            "verdict_en": "This is a confirmed scam attempt.",
            "verdict_hi": "यह एक पुष्ट scam प्रयास है।",
            "action_en": "Do not send any money. Report immediately.",
            "action_hi": "कोई पैसे न भेजें। तुरंत रिपोर्ट करें।",
            "upi_ids_found": ["scammer@paytm"],
            "phone_numbers_found": ["9876543210"],
            "is_critical": True,
            "critical_reason": "High confidence fraud with financial risk",
            "estimated_loss_inr": 15000,
        }

        case_id = await get_alert_service().handle_critical_case(
            body.user_id, mock_result
        )
        return {
            "case_id": case_id,
            "emails_sent": True,
            "message": "Test critical alert sent successfully",
        }
    except Exception:
        logger.exception("Test critical alert failed")
        raise HTTPException(status_code=500, detail="Test critical alert failed")
