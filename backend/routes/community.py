"""
FraudShield AI — Community Router
====================================
Handles the community leaderboard, user badges/ranking, referral codes,
platform-wide fraud statistics, and community alert CRUD with voting.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.database.mongo import get_db
from backend.middleware.auth_middleware import get_current_user
from backend.models.community_report import (
    CommunityAlertCreate,
    VotePayload,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class ReferralApply(BaseModel):
    """Schema for applying a referral code."""

    referral_code: str = Field(
        ..., min_length=8, max_length=8, description="8-character referral code"
    )


# ---------------------------------------------------------------------------
# Leaderboard & Stats
# ---------------------------------------------------------------------------
@router.get(
    "/leaderboard",
    status_code=status.HTTP_200_OK,
    summary="Get top users leaderboard",
)
async def get_leaderboard():
    """Retrieve the top 50 users sorted by guardian points."""
    db = get_db()

    cursor = (
        db.users.find(
            {},
            {"name": 1, "guardian_points": 1, "badges": 1, "_id": 0},
        )
        .sort("guardian_points", -1)
        .limit(50)
    )

    leaderboard = []
    async for doc in cursor:
        leaderboard.append(doc)

    return {
        "success": True,
        "data": leaderboard,
        "message": "Leaderboard retrieved successfully.",
    }


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get platform fraud statistics",
)
async def get_stats():
    """Get system-wide metrics: total analyses, reports, scams prevented,
    and top scam categories."""
    db = get_db()

    total_analyses = await db.analyses.count_documents({})
    total_reports = await db.fraud_reports.count_documents({})
    scams_prevented = await db.analyses.count_documents(
        {"is_dangerous": True}
    )

    pipeline = [
        {"$group": {"_id": "$scam_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5},
    ]
    cursor = db.analyses.aggregate(pipeline)

    top_scam_types = []
    async for doc in cursor:
        scam_name = doc.get("_id")
        if scam_name:
            top_scam_types.append(
                {"scam_type": scam_name, "count": doc.get("count", 0)}
            )

    return {
        "success": True,
        "data": {
            "total_analyses": total_analyses,
            "total_reports": total_reports,
            "scams_prevented": scams_prevented,
            "top_scam_types": top_scam_types,
        },
        "message": "Platform stats retrieved successfully.",
    }


# ---------------------------------------------------------------------------
# Badges & Rank
# ---------------------------------------------------------------------------
@router.get(
    "/badges",
    status_code=status.HTTP_200_OK,
    summary="Retrieve user badges and leaderboard rank",
)
async def get_user_badges(current_user: dict = Depends(get_current_user)):
    """Retrieve the current user's badges, points, and global ranking."""
    db = get_db()

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

    points = user.get("guardian_points", 0)
    higher_users = await db.users.count_documents(
        {"guardian_points": {"$gt": points}}
    )
    rank = higher_users + 1

    return {
        "success": True,
        "data": {
            "badges": user.get("badges", []),
            "guardian_points": points,
            "rank": rank,
        },
        "message": "User badges and rank retrieved successfully.",
    }


# ---------------------------------------------------------------------------
# Referrals
# ---------------------------------------------------------------------------
@router.post(
    "/referral",
    status_code=status.HTTP_200_OK,
    summary="Claim a referral code",
)
async def claim_referral(
    payload: ReferralApply,
    current_user: dict = Depends(get_current_user),
):
    """Claim a referral code.  Awards 50 points to both parties."""
    db = get_db()
    code = payload.referral_code.upper()
    now = datetime.now(timezone.utc)

    referrer = await db.users.find_one({"referral_code": code})
    if not referrer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Referral code not found.",
                "code": "INVALID_REFERRAL_CODE",
            },
        )

    if referrer["uid"] == current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "You cannot apply your own referral code.",
                "code": "SELF_REFERRAL",
            },
        )

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

    if user.get("referred_by") is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "You have already applied a referral code.",
                "code": "REFERRAL_ALREADY_SET",
            },
        )

    # Award points to both
    await db.users.update_one(
        {"uid": current_user["uid"]},
        {
            "$set": {"referred_by": referrer["uid"], "updated_at": now},
            "$inc": {"guardian_points": 50},
        },
    )
    await db.users.update_one(
        {"uid": referrer["uid"]},
        {
            "$inc": {"guardian_points": 50},
            "$set": {"updated_at": now},
        },
    )

    logger.info(
        "Referral applied: %s referred by %s",
        current_user["uid"],
        referrer["uid"],
    )

    return {
        "success": True,
        "data": {"points_awarded": 50},
        "message": f"Referral code applied successfully. 50 points awarded to both you and {referrer['name']}.",
    }


# ---------------------------------------------------------------------------
# Community Alerts (matching frontend communityService.ts)
# ---------------------------------------------------------------------------
@router.get(
    "/alerts",
    status_code=status.HTTP_200_OK,
    summary="Get community fraud alerts",
)
async def get_community_alerts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Retrieve paginated community fraud alerts sorted by creation time."""
    db = get_db()
    skip = (page - 1) * limit

    cursor = (
        db.community_alerts.find({})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    alerts = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["timestamp"] = _humanize_timestamp(doc["created_at"])
            doc["created_at"] = doc["created_at"].isoformat()
        alerts.append(doc)

    return {
        "success": True,
        "data": alerts,
        "message": "Community alerts retrieved successfully.",
    }


@router.post(
    "/alerts",
    status_code=status.HTTP_201_CREATED,
    summary="Create a community fraud alert",
)
async def create_community_alert(
    payload: CommunityAlertCreate,
    current_user: dict = Depends(get_current_user),
):
    """Submit a new community fraud alert."""
    db = get_db()
    alert_id = f"cm_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)

    alert_doc = {
        "id": alert_id,
        "author": payload.author,
        "authorAvatar": payload.author_avatar,
        "title": payload.title,
        "category": payload.category,
        "description": payload.description,
        "riskLevel": payload.risk_level,
        "location": payload.location,
        "votes": 1,
        "verified": False,
        "timestamp": "Just now",
        "tags": payload.tags,
        "created_at": now,
        "submitted_by": current_user["uid"],
    }

    await db.community_alerts.insert_one(alert_doc)
    logger.info("Community alert %s created by %s", alert_id, current_user["uid"])

    alert_doc.pop("_id", None)

    return {
        "success": True,
        "data": alert_doc,
        "message": "Community alert created successfully.",
    }


@router.post(
    "/alerts/{alert_id}/vote",
    status_code=status.HTTP_200_OK,
    summary="Vote on a community alert",
)
async def vote_community_alert(
    alert_id: str,
    payload: VotePayload,
    current_user: dict = Depends(get_current_user),
):
    """Upvote or downvote a community fraud alert."""
    db = get_db()

    result = await db.community_alerts.find_one_and_update(
        {"id": alert_id},
        {"$inc": {"votes": payload.delta}},
        projection={"votes": 1, "_id": 0},
        return_document=True,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Community alert not found.",
                "code": "ALERT_NOT_FOUND",
            },
        )

    return {
        "success": True,
        "data": {"votes": result.get("votes", 0)},
        "message": "Vote recorded successfully.",
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _humanize_timestamp(dt: datetime) -> str:
    """Convert a datetime to a human-readable relative time string."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} min{'s' if minutes > 1 else ''} ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    days = seconds // 86400
    return f"{days} day{'s' if days > 1 else ''} ago"
