"""
Report service for FraudShield.
Handles community fraud reporting, Guardian Points, and badge logic.
"""

from __future__ import annotations

import logging
import re

from database.mongo import MongoClient
from database.redis import RedisClient

logger = logging.getLogger(__name__)

POINTS_MAP = {
    "report_submitted": 10,
    "report_verified": 25,
    "critical_report": 50,
    "referral_signup": 30,
    "quiz_completion": 15,
    "daily_check": 2,
}

BADGE_THRESHOLDS = [
    (5, "Fraud Reporter"),
    (25, "Community Guardian"),
    (100, "Fraud Slayer"),
    (250, "Elite Defender"),
]

BADGE_MESSAGES = {
    "Fraud Reporter": (
        "🎖️ Badge Unlocked: Fraud Reporter\n"
        "Aapne 5 reports submit kiye! Community ne pehchana aapko. 🫡"
    ),
    "Community Guardian": (
        "🛡️ Badge Unlocked: Community Guardian\n"
        "25 reports! Aap hamari community ke asli rakshak hain. 💪"
    ),
    "Fraud Slayer": (
        "⚔️ Badge Unlocked: Fraud Slayer\n"
        "100 reports! Scammers aapse darte honge. 🔥"
    ),
    "Elite Defender": (
        "👑 Badge Unlocked: Elite Defender\n"
        "250 reports! Aap FraudShield ke legend hain. 🙌"
    ),
}


class ReportService:
    def __init__(self) -> None:
        self.firestore = MongoClient()
        self.redis = RedisClient()

    async def submit_report(
        self,
        user_id: str,
        upi_or_phone: str,
        scam_type: str,
        description: str | None,
    ) -> dict:
        try:
            input_type, sanitised = self.validate_input(upi_or_phone)
            if input_type == "invalid":
                return {
                    "success": False,
                    "points_awarded": 0,
                    "new_total": 0,
                    "badge_earned": None,
                    "message": "Galat format. UPI ID (example@paytm) ya 10-digit phone number daalein.",
                }

            dup_check = await self.firestore.community_reports.find_one(
                {"reported_by": user_id, "status": {"$ne": "rejected"}}
            )
            if dup_check:
                return {
                    "success": False,
                    "points_awarded": 0,
                    "new_total": 0,
                    "badge_earned": None,
                    "message": "Aap already ek report submit kar chuke hain. Har user ek hi report send kar sakta hai.",
                }

            data = {
                "reported_by": user_id,
                "scam_type": scam_type,
                "description": description,
                "status": "pending",
            }

            if input_type == "upi":
                data["upi_id"] = sanitised
                doc_id = await self.firestore.save_community_report(data)
                if doc_id:
                    await self.firestore.increment_fraud_upi_report(
                        upi_id=sanitised,
                        reported_by=user_id,
                        city="Unknown",
                        scam_type=scam_type,
                    )
                    await self.redis.invalidate_upi(sanitised)
            else:
                data["phone"] = sanitised
                doc_id = await self.firestore.save_community_report(data)
                if doc_id:
                    await self.firestore.increment_fraud_phone_report(
                        phone=sanitised,
                        scam_type=scam_type,
                    )

            new_total = await self.award_points(user_id, "report_submitted")
            badge = await self.check_badge_eligibility(user_id)

            return {
                "success": True,
                "points_awarded": POINTS_MAP["report_submitted"],
                "new_total": new_total,
                "badge_earned": badge,
                "message": (
                    "✅ Report submit ho gayi!\n\n"
                    f"+{POINTS_MAP['report_submitted']} Guardian Points credited 🌟\n"
                    f"Total Points: {new_total}\n\n"
                    "Shukriya community ko safe rakhne ke liye! 🛡️"
                ),
            }
        except Exception:
            logger.exception("submit_report failed for user %s", user_id)
            return {
                "success": False,
                "points_awarded": 0,
                "new_total": 0,
                "badge_earned": None,
                "message": "Report submit nahi ho payi. Please try again. 🔄",
            }

    async def get_recent_reports(self, limit: int = 20) -> list:
        try:
            docs = await self.firestore.get_community_reports(limit)
            result = []
            for d in docs:
                if d is None:
                    continue
                result.append(
                    {
                        "city": d.get("city", "Unknown"),
                        "scam_type": d.get("scam_type"),
                        "status": d.get("status"),
                        "time": d.get("submitted_at").isoformat()
                        if d.get("submitted_at")
                        else None,
                    }
                )
            return result
        except Exception:
            logger.exception("get_recent_reports failed")
            return []

    async def get_leaderboard(self, limit: int = 10) -> list:
        try:
            return await self.firestore.get_top_reporters(limit)
        except Exception:
            logger.exception("get_leaderboard failed")
            return []

    async def award_points(self, user_id: str, reason: str) -> int:
        points = POINTS_MAP.get(reason, 0)
        if points == 0:
            logger.warning("Unknown award reason: %s", reason)
            return 0
        new_total = await self.firestore.award_points(user_id, points)
        await self.redis.invalidate_user(user_id)
        return new_total

    async def check_badge_eligibility(self, user_id: str) -> str | None:
        try:
            user = await self.firestore.get_user(user_id)
            if not user:
                return None

            total_reports = await self.firestore.community_reports.count_documents(
                {"reported_by": user_id}
            )
            existing_badges = user.get("badges", [])

            for threshold, badge_name in reversed(BADGE_THRESHOLDS):
                if total_reports >= threshold and badge_name not in existing_badges:
                    await self.firestore.add_badge(user_id, badge_name)
                    await self.redis.invalidate_user(user_id)
                    return badge_name
            return None
        except Exception:
            logger.exception("check_badge_eligibility failed for %s", user_id)
            return None

    @staticmethod
    def get_badge_unlock_message(badge: str) -> str:
        return BADGE_MESSAGES.get(
            badge,
            f"🏅 Badge Unlocked: {badge}",
        )

    @staticmethod
    def validate_input(value: str) -> tuple[str, str]:
        value = value.strip()
        if "@" in value and re.match(r"^[\w.@_\-]+$", value):
            return ("upi", value)
        if re.match(r"^\d{10}$", value):
            return ("phone", value)
        return ("invalid", value)
