"""
FastAPI router for fraud report submission from web dashboard.
Prefix: /reports
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from database.mongo import MongoClient
from database.redis import RedisClient
from services.report_service import ReportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])

firestore = MongoClient()
redis = RedisClient()
report_service = ReportService()


class SubmitReportBody(BaseModel):
    upi_id: Optional[str] = None
    phone: Optional[str] = None
    scam_type: str
    description: Optional[str] = None


async def verify_token(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        from routes.auth import verify_token as auth_verify

        user_id = await auth_verify(token)
        return user_id
    except ImportError:
        logger.warning("auth.verify_token not available — using mock auth")
        return token
    except Exception:
        logger.exception("Token verification failed")
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/submit")
async def submit_report(
    body: SubmitReportBody,
    user_id: str = Depends(verify_token),
):
    identifier = body.upi_id or body.phone
    if not identifier:
        raise HTTPException(status_code=400, detail="Provide upi_id or phone")

    result = await report_service.submit_report(
        user_id=user_id,
        upi_or_phone=identifier,
        scam_type=body.scam_type,
        description=body.description,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/lookup/{identifier}")
async def lookup_identifier(identifier: str):
    try:
        is_upi = "@" in identifier
        cache_key = f"upi:{identifier}" if is_upi else f"phone:{identifier}"

        cached = await redis.get(cache_key)
        if cached:
            import json

            return json.loads(cached)

        if is_upi:
            doc = await firestore.get_fraud_upi(identifier)
        else:
            doc = await firestore.get_fraud_phone(identifier)

        if not doc:
            return {
                "found": False,
                "risk_level": None,
                "report_count": 0,
                "scam_type": None,
                "risk_score": None,
                "verified": False,
                "first_seen": None,
            }

        risk_score = doc.get("risk_score", 0)
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 35:
            risk_level = "MEDIUM"
        else:
            risk_level = "SAFE"

        result = {
            "found": True,
            "risk_level": risk_level,
            "report_count": doc.get("report_count", 0),
            "scam_type": doc.get("scam_type"),
            "risk_score": risk_score,
            "verified": doc.get("verified", False),
            "first_seen": doc.get("first_seen").isoformat()
            if doc.get("first_seen")
            else None,
        }

        await redis.set(cache_key, result, 3600)
        return result
    except Exception:
        logger.exception("Lookup failed for %s", identifier)
        raise HTTPException(status_code=500, detail="Lookup failed")


@router.get("/my-reports")
async def get_my_reports(user_id: str = Depends(verify_token)):
    try:
        cursor = firestore.community_reports.find(
            {"reported_by": user_id}
        ).sort("submitted_at", -1)
        docs = await cursor.to_list(length=None)
        result = []
        for d in docs:
            if d is None:
                continue
            d["_id"] = str(d["_id"])
            d.pop("reported_by", None)
            if d.get("submitted_at"):
                d["submitted_at"] = d["submitted_at"].isoformat()
            result.append(d)
        return {"reports": result}
    except Exception:
        logger.exception("Failed to fetch my reports")
        raise HTTPException(status_code=500, detail="Failed to fetch reports")
