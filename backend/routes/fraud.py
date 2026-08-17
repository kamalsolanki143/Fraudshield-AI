"""
FraudShield AI — Fraud Analysis Router
=========================================
Handles screenshot uploads for AI-powered fraud detection, and entity
lookups (UPI IDs, phone numbers, URLs) against the community fraud database.

Analysis flow::

    Upload → Validate → User limits check → Cloudinary upload →
    Fraud Service (Gemini AI + Risk Engine) → MongoDB save → Response
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from backend.database.mongo import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.models.fraud_case import (
    LookupPhone,
    LookupResponse,
    LookupUPI,
    LookupURL,
)
from backend.services.cloudinary_service import upload_image
from backend.services.fraud_service import analyze_fraud_screenshot

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_MIME_TYPES = ("image/jpeg", "image/png", "image/webp", "image/jpg")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/analyze",
    status_code=status.HTTP_201_CREATED,
    summary="Analyze payment screenshot or QR code",
)
async def analyze_fraud(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Analyze a screenshot image to detect potential scams.

    Validates format/size, verifies user analysis limits, uploads to
    Cloudinary, runs Gemini Vision AI analysis through the fraud service,
    and records the case in the user's history.
    """
    db = get_db()

    # ---- Validate MIME type ----
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Invalid file format. Only JPEG, PNG, and WebP are allowed.",
                "code": "INVALID_FILE_TYPE",
            },
        )

    # ---- Read and validate size ----
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "File size exceeds the 10MB limit.",
                "code": "FILE_TOO_LARGE",
            },
        )

    # ---- Check user analysis limits ----
    user = await db.users.find_one({"uid": current_user["uid"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "User profile not found.",
                "code": "USER_NOT_FOUND",
            },
        )

    if user.get("analyses_used", 0) >= user.get("analyses_limit", 5):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": "Analysis limit reached. Please upgrade your plan.",
                "code": "LIMIT_REACHED",
            },
        )

    # ---- Upload to Cloudinary ----
    try:
        cloudinary_res = await upload_image(content, file.filename or "screenshot.png")
    except Exception as e:
        logger.exception("Cloudinary upload failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": f"Failed to upload image: {str(e)}",
                "code": "UPLOAD_FAILED",
            },
        )

    image_url = cloudinary_res["url"]
    public_id = cloudinary_res["public_id"]

    # ---- Run AI analysis via fraud service ----
    try:
        analysis_result = await analyze_fraud_screenshot(
            file_bytes=content,
            original_filename=file.filename or "screenshot.png",
        )
    except Exception as e:
        logger.exception("Fraud analysis failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "code": "ANALYSIS_FAILED",
            },
        )

    # ---- Save to database ----
    analysis_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    analysis_doc = {
        "analysis_id": analysis_id,
        "user_uid": current_user["uid"],
        "image_url": image_url,
        "public_id": public_id,
        "verdict": analysis_result.get("verdict", "SUSPICIOUS"),
        "risk_score": analysis_result.get("risk_score", 50),
        "confidence_score": analysis_result.get("confidence_score", 0.8),
        "scam_type": analysis_result.get("scam_type", "None Detected"),
        "reasons": analysis_result.get("reasons", []),
        "action_step": analysis_result.get("action_step", ""),
        "risk_level": analysis_result.get("risk_level", "yellow"),
        "is_dangerous": analysis_result.get("is_dangerous", False),
        "explanation_en": analysis_result.get("explanation_en", ""),
        "explanation_hi": analysis_result.get("explanation_hi", ""),
        "analysed_at": analysis_result.get("analysed_at", now.isoformat()),
        "recommended_action": analysis_result.get("action_step", ""),
        "created_at": now,
    }

    await db.analyses.insert_one(analysis_doc)

    # Increment analyses_used
    await db.users.update_one(
        {"uid": current_user["uid"]},
        {"$inc": {"analyses_used": 1}, "$set": {"updated_at": now}},
    )

    logger.info(
        "Analysis %s completed: score=%s verdict=%s",
        analysis_id,
        analysis_doc["risk_score"],
        analysis_doc["verdict"],
    )

    # Remove MongoDB _id before response
    analysis_doc.pop("_id", None)

    return {
        "success": True,
        "data": analysis_doc,
        "message": "Image analyzed successfully.",
    }


# ---------------------------------------------------------------------------
# Entity lookup endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/lookup/upi",
    status_code=status.HTTP_200_OK,
    summary="Look up reported UPI ID",
)
async def lookup_upi(
    payload: LookupUPI,
    current_user: dict = Depends(get_current_user),
):
    """Search for a UPI ID in the fraud database."""
    db = get_db()

    doc = await db.fraud_database.find_one(
        {"entity_type": "upi_id", "entity_value": payload.upi_id}
    )
    if not doc:
        return {
            "success": True,
            "data": LookupResponse(
                is_reported=False,
                report_count=0,
                scam_categories=[],
                risk_level="safe",
            ).model_dump(),
            "message": "UPI ID is clean. No reports found.",
        }

    reports_count = doc.get("reports_count", 0)
    risk_level = "high_risk" if reports_count >= 3 else "medium_risk"

    return {
        "success": True,
        "data": LookupResponse(
            is_reported=True,
            report_count=reports_count,
            scam_categories=[doc.get("scam_category", "general")],
            risk_level=risk_level,
        ).model_dump(),
        "message": "Suspicious UPI ID detected.",
    }


@router.post(
    "/lookup/phone",
    status_code=status.HTTP_200_OK,
    summary="Look up reported phone number",
)
async def lookup_phone(
    payload: LookupPhone,
    current_user: dict = Depends(get_current_user),
):
    """Search for a phone number in the fraud database."""
    db = get_db()

    doc = await db.fraud_database.find_one(
        {"entity_type": "phone_number", "entity_value": payload.phone_number}
    )
    if not doc:
        return {
            "success": True,
            "data": LookupResponse(
                is_reported=False,
                report_count=0,
                scam_categories=[],
                risk_level="safe",
            ).model_dump(),
            "message": "Phone number is clean. No reports found.",
        }

    reports_count = doc.get("reports_count", 0)
    risk_level = "high_risk" if reports_count >= 3 else "medium_risk"

    return {
        "success": True,
        "data": LookupResponse(
            is_reported=True,
            report_count=reports_count,
            scam_categories=[doc.get("scam_category", "general")],
            risk_level=risk_level,
        ).model_dump(),
        "message": "Suspicious phone number detected.",
    }


@router.post(
    "/lookup/url",
    status_code=status.HTTP_200_OK,
    summary="Look up reported website URL",
)
async def lookup_url(
    payload: LookupURL,
    current_user: dict = Depends(get_current_user),
):
    """Search for a URL in the fraud database."""
    db = get_db()

    doc = await db.fraud_database.find_one(
        {"entity_type": "website", "entity_value": payload.url}
    )
    if not doc:
        return {
            "success": True,
            "data": LookupResponse(
                is_reported=False,
                report_count=0,
                scam_categories=[],
                risk_level="safe",
                reason="This URL is not reported as suspicious.",
            ).model_dump(),
            "message": "Website URL is clean. No reports found.",
        }

    reports_count = doc.get("reports_count", 0)
    risk_level = "high_risk" if reports_count >= 3 else "medium_risk"
    reason = f"This link has been reported in {reports_count} scam cases."

    return {
        "success": True,
        "data": LookupResponse(
            is_reported=True,
            report_count=reports_count,
            scam_categories=[doc.get("scam_category", "phishing")],
            risk_level=risk_level,
            reason=reason,
        ).model_dump(),
        "message": "Suspicious website URL detected.",
    }
