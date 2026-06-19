"""Fraud analysis and entity search API router.

Handles screenshot uploads, Cloudinary saving, stub AI processing, and queries
for reported UPI IDs, phone numbers, and website links.
"""

from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from database.mongodb import get_db
from middleware.auth_middleware import get_current_user
from models.fraud_case import (
    AnalysisResponse,
    LookupPhone,
    LookupResponse,
    LookupUPI,
    LookupURL,
)
from services import gemini_service, risk_engine
from services.cloudinary_service import upload_image

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

    Validates format/size, verifies user analysis limits, uploads to Cloudinary,
    runs stubs for AI classification, and records the case in history.
    """
    db = get_db()

    # Validate image mime type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Invalid file format. Only JPEG, PNG, and WebP are allowed.",
                "code": "INVALID_FILE_TYPE",
            },
        )

    # Read bytes and validate size
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

    # Fetch user to verify analysis usage/limits
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

    # Upload to Cloudinary
    try:
        cloudinary_res = await upload_image(content, file.filename)
    except Exception as e:
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

    # Process via stubs
    gemini_out = await gemini_service.analyze_image(image_url, user.get("fraud_iq_level", "novice"))
    risk_out = await risk_engine.calculate_risk(gemini_out)

    # Save to analyses collection
    analysis_id = str(uuid.uuid4())
    now = datetime.utcnow()

    analysis_doc = {
        "analysis_id": analysis_id,
        "user_uid": current_user["uid"],
        "image_url": image_url,
        "public_id": public_id,
        "verdict": risk_out.get("verdict", "unknown"),
        "confidence_score": risk_out.get("confidence_score", 0),
        "scam_type": risk_out.get("scam_type", "Unknown Scam"),
        "explanation_en": risk_out.get("explanation_en", ""),
        "explanation_hi": risk_out.get("explanation_hi", ""),
        "recommended_action": risk_out.get("recommended_action", ""),
        "created_at": now,
    }

    await db.analyses.insert_one(analysis_doc)

    # Increment analyses_used for user
    await db.users.update_one(
        {"uid": current_user["uid"]},
        {"$inc": {"analyses_used": 1}, "$set": {"updated_at": now}},
    )

    response_data = AnalysisResponse(**analysis_doc)

    return {
        "success": True,
        "data": response_data.model_dump(),
        "message": "Image analyzed successfully.",
    }


@router.post(
    "/lookup/upi",
    status_code=status.HTTP_200_OK,
    summary="Look up reported UPI ID",
)
async def lookup_upi(payload: LookupUPI, current_user: dict = Depends(get_current_user)):
    """Search for a UPI ID in the fraud database."""
    db = get_db()

    doc = await db.fraud_database.find_one({"entity_type": "upi_id", "entity_value": payload.upi_id})
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

    # Calculate risk level based on report counts or confidence
    reports_count = doc.get("reports_count", 0)
    risk_level = "high_risk" if reports_count >= 3 else "medium_risk"

    response_data = LookupResponse(
        is_reported=True,
        report_count=reports_count,
        scam_categories=[doc.get("scam_category", "general")],
        risk_level=risk_level,
    )

    return {
        "success": True,
        "data": response_data.model_dump(),
        "message": "Suspicious UPI ID detected.",
    }


@router.post(
    "/lookup/phone",
    status_code=status.HTTP_200_OK,
    summary="Look up reported phone number",
)
async def lookup_phone(payload: LookupPhone, current_user: dict = Depends(get_current_user)):
    """Search for a phone number in the fraud database."""
    db = get_db()

    doc = await db.fraud_database.find_one({"entity_type": "phone_number", "entity_value": payload.phone_number})
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

    response_data = LookupResponse(
        is_reported=True,
        report_count=reports_count,
        scam_categories=[doc.get("scam_category", "general")],
        risk_level=risk_level,
    )

    return {
        "success": True,
        "data": response_data.model_dump(),
        "message": "Suspicious phone number detected.",
    }


@router.post(
    "/lookup/url",
    status_code=status.HTTP_200_OK,
    summary="Look up reported website URL",
)
async def lookup_url(payload: LookupURL, current_user: dict = Depends(get_current_user)):
    """Search for a URL in the fraud database."""
    db = get_db()

    doc = await db.fraud_database.find_one({"entity_type": "website", "entity_value": payload.url})
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

    response_data = LookupResponse(
        is_reported=True,
        report_count=reports_count,
        scam_categories=[doc.get("scam_category", "phishing")],
        risk_level=risk_level,
        reason=reason,
    )

    return {
        "success": True,
        "data": response_data.model_dump(),
        "message": "Suspicious website URL detected.",
    }
