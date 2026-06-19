"""Community leaderboard, referrals, and gamified statistics API router.

Handles fetching user ranking positions, awarding points for referrals,
listing leaderboards, and querying overall fraud statistics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from database.mongodb import get_db
from middleware.auth_middleware import get_current_user

router = APIRouter()


class ReferralApply(BaseModel):
    """Local schema for applying a referral code."""

    referral_code: str = Field(..., min_length=8, max_length=8, description="8-character referral code")


@router.get(
    "/leaderboard",
    status_code=status.HTTP_200_OK,
    summary="Get top users leaderboard",
)
async def get_leaderboard():
    """Retrieve the top 50 users sorted by their guardian points.

    Exposes name, points, and badges only.
    """
    db = get_db()

    cursor = db.users.find(
        {},
        {
            "name": 1,
            "guardian_points": 1,
            "badges": 1,
            "_id": 0,
        },
    ).sort("guardian_points", -1).limit(50)

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
    summary="Get platform metrics and fraud stats",
)
async def get_stats():
    """Get system-wide metrics.

    Includes total analyses run, total reports submitted, high-risk cases prevented,
    and a breakdown of the top 5 scam categories.
    """
    db = get_db()

    # Get counts
    total_analyses = await db.analyses.count_documents({})
    total_reports = await db.fraud_reports.count_documents({})
    scams_prevented = await db.analyses.count_documents({"verdict": "high_risk"})

    # Aggregate top scam types
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
            top_scam_types.append({"scam_type": scam_name, "count": doc.get("count", 0)})

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


@router.get(
    "/badges",
    status_code=status.HTTP_200_OK,
    summary="Retrieve user badges and leaderboard rank",
)
async def get_user_badges(current_user: dict = Depends(get_current_user)):
    """Retrieve the current user's unlocked badges, guardian points, and global ranking position."""
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

    # Calculate global leaderboard rank
    points = user.get("guardian_points", 0)
    higher_users = await db.users.count_documents({"guardian_points": {"$gt": points}})
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


@router.post(
    "/referral",
    status_code=status.HTTP_200_OK,
    summary="Claim a referral code",
)
async def claim_referral(
    payload: ReferralApply,
    current_user: dict = Depends(get_current_user),
):
    """Claim a referral code.

    Awards 50 points to both the referrer and the referred user.
    """
    db = get_db()
    code = payload.referral_code.upper()

    # Find referring user
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

    # Validate referral isn't self-referral
    if referrer["uid"] == current_user["uid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "You cannot apply your own referral code.",
                "code": "SELF_REFERRAL",
            },
        )

    # Fetch current user details
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

    # Validate that the user hasn't already been referred
    if user.get("referred_by") is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "You have already applied a referral code.",
                "code": "REFERRAL_ALREADY_SET",
            },
        )

    # Apply referral in a transaction/multi-update:
    # 1. Update referred user (current user)
    await db.users.update_one(
        {"uid": current_user["uid"]},
        {
            "$set": {
                "referred_by": referrer["uid"],
                "updated_at": datetime.utcnow(),
            },
            "$inc": {"guardian_points": 50},
        },
    )

    # 2. Update referrer
    await db.users.update_one(
        {"uid": referrer["uid"]},
        {
            "$inc": {"guardian_points": 50},
            "$set": {"updated_at": datetime.utcnow()},
        },
    )

    return {
        "success": True,
        "data": {"points_awarded": 50},
        "message": f"Referral code applied successfully. 50 points awarded to both you and {referrer['name']}.",
    }
