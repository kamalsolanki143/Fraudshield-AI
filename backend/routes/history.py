"""
FraudShield AI — Analysis History Router
==========================================
Handles retrieving, viewing, and deleting the user's past screenshot
analysis records.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.database.mongo import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.services.cloudinary_service import delete_image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get user analysis history",
)
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Retrieve a paginated list of screenshot analyses completed by the user.

    Sorted in descending order of creation.
    """
    db = get_db()
    skip = (page - 1) * limit

    cursor = (
        db.analyses.find(
            {"user_uid": current_user["uid"]},
            {
                "analysis_id": 1,
                "verdict": 1,
                "risk_score": 1,
                "confidence_score": 1,
                "scam_type": 1,
                "image_url": 1,
                "risk_level": 1,
                "is_dangerous": 1,
                "created_at": 1,
                "_id": 0,
            },
        )
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    history_list = []
    async for doc in cursor:
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        history_list.append(doc)

    return {
        "success": True,
        "data": history_list,
        "message": "Analysis history retrieved successfully.",
    }


@router.get(
    "/{analysis_id}",
    status_code=status.HTTP_200_OK,
    summary="Get detailed analysis by ID",
)
async def get_analysis_detail(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Retrieve the full details of a specific analysis case.

    Verifies case ownership before returning data.
    """
    db = get_db()

    analysis_doc = await db.analyses.find_one({"analysis_id": analysis_id})
    if not analysis_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Analysis record not found.",
                "code": "RECORD_NOT_FOUND",
            },
        )

    if analysis_doc.get("user_uid") != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": "You do not have permission to view this analysis record.",
                "code": "ACCESS_DENIED",
            },
        )

    analysis_doc["_id"] = str(analysis_doc["_id"])
    if "created_at" in analysis_doc and isinstance(
        analysis_doc["created_at"], datetime
    ):
        analysis_doc["created_at"] = analysis_doc["created_at"].isoformat()

    return {
        "success": True,
        "data": analysis_doc,
        "message": "Analysis details retrieved successfully.",
    }


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete analysis record",
)
async def delete_analysis_record(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete an analysis record from the database and Cloudinary.

    Verifies ownership and decrements the user's analysis counter.
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    analysis_doc = await db.analyses.find_one({"analysis_id": analysis_id})
    if not analysis_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Analysis record not found.",
                "code": "RECORD_NOT_FOUND",
            },
        )

    if analysis_doc.get("user_uid") != current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "error": "You do not have permission to delete this analysis record.",
                "code": "ACCESS_DENIED",
            },
        )

    # Delete from Cloudinary
    public_id = analysis_doc.get("public_id")
    if public_id:
        try:
            await delete_image(public_id)
        except Exception as e:
            logger.warning("Cloudinary deletion warning: %s", e)

    await db.analyses.delete_one({"analysis_id": analysis_id})

    # Decrement user analyses_used (floor at 0)
    await db.users.update_one(
        {"uid": current_user["uid"]},
        {
            "$inc": {"analyses_used": -1},
            "$set": {"updated_at": now},
        },
    )

    logger.info("Deleted analysis %s for user %s", analysis_id, current_user["uid"])

    return {
        "success": True,
        "data": None,
        "message": "Analysis record and associated image deleted successfully.",
    }
