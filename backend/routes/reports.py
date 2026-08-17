"""
FraudShield AI — Fraud Reports Router
========================================
Handles community fraud report submission, paginated listing, detail view,
and upvoting.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.database.mongo import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.models.report import ReportCreate, ReportResponse, ReportSubmitResponse
from backend.services.report_service import get_reports, submit_report

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/submit",
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new fraud report",
)
async def submit_new_report(
    payload: ReportCreate,
    current_user: dict = Depends(get_current_user),
):
    """Submit a community fraud report about a UPI ID, phone, URL, or message.

    Awards 10 guardian points and checks for milestone badges.
    """
    try:
        result = await submit_report(
            uid=current_user["uid"],
            entity_type=payload.entity_type,
            entity_value=payload.entity_value,
            scam_category=payload.scam_category,
            description=payload.description,
        )

        response_data = ReportSubmitResponse(**result)

        return {
            "success": True,
            "data": response_data.model_dump(),
            "message": "Fraud report submitted successfully.",
        }
    except Exception as e:
        logger.exception("Failed to submit report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": f"Failed to submit report: {str(e)}",
                "code": "REPORT_SUBMISSION_FAILED",
            },
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get paginated fraud reports",
)
async def list_reports(
    entity_type: Optional[str] = Query(None),
    scam_category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    """Retrieve all submitted fraud reports with optional filtering."""
    reports = await get_reports(
        page=page,
        limit=limit,
        entity_type=entity_type,
        scam_category=scam_category,
    )

    return {
        "success": True,
        "data": reports,
        "message": "Fraud reports list retrieved successfully.",
    }


@router.get(
    "/{report_id}",
    status_code=status.HTTP_200_OK,
    summary="Get fraud report by ID",
)
async def get_report_detail(report_id: str):
    """Retrieve full details of a specific community fraud report."""
    db = get_db()

    report_doc = await db.fraud_reports.find_one({"report_id": report_id})
    if not report_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Fraud report not found.",
                "code": "REPORT_NOT_FOUND",
            },
        )

    report_doc["_id"] = str(report_doc["_id"])
    if "created_at" in report_doc and not isinstance(
        report_doc["created_at"], str
    ):
        report_doc["created_at"] = report_doc["created_at"].isoformat()

    response_data = ReportResponse(**report_doc)

    return {
        "success": True,
        "data": response_data.model_dump(),
        "message": "Report details retrieved successfully.",
    }


@router.post(
    "/{report_id}/upvote",
    status_code=status.HTTP_200_OK,
    summary="Upvote a fraud report",
)
async def upvote_report(
    report_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Increment the upvote count for a community report."""
    db = get_db()

    report_doc = await db.fraud_reports.find_one({"report_id": report_id})
    if not report_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Fraud report not found.",
                "code": "REPORT_NOT_FOUND",
            },
        )

    result = await db.fraud_reports.find_one_and_update(
        {"report_id": report_id},
        {"$inc": {"upvotes": 1}},
        projection={"upvotes": 1, "_id": 0},
        return_document=True,
    )

    return {
        "success": True,
        "data": {"upvotes": result.get("upvotes", 0)},
        "message": "Report upvoted successfully.",
    }
