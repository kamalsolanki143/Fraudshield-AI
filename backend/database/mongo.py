"""
MongoDB async client singleton for FraudShield.
Uses motor (async MongoDB driver) with pymongo.
All database operations wrapped in try/except with logging.
"""

from __future__ import annotations

import logging
import os
import random
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

logger = logging.getLogger(__name__)


class MongoClient:
    _instance: "MongoClient | None" = None

    def __new__(cls) -> "MongoClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.client: AsyncIOMotorClient | None = None
        self.db = None
        self.users = None
        self.fraud_upi_ids = None
        self.fraud_phone_numbers = None
        self.scam_patterns = None
        self.advisories = None
        self.community_reports = None
        self.critical_reports = None
        self.analysis_history = None

    async def initialize(self) -> None:
        uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGODB_DB_NAME", "fraudshield")
        if not uri:
            raise ValueError("MONGODB_URI environment variable not set")
        try:
            self.client = AsyncIOMotorClient(uri)
            self.db = self.client[db_name]
            self.users = self.db["users"]
            self.fraud_upi_ids = self.db["fraud_upi_ids"]
            self.fraud_phone_numbers = self.db["fraud_phone_numbers"]
            self.scam_patterns = self.db["scam_patterns"]
            self.advisories = self.db["advisories"]
            self.community_reports = self.db["community_reports"]
            self.critical_reports = self.db["critical_reports"]
            self.analysis_history = self.db["analysis_history"]

            await self.users.create_index("telegram_id", unique=True)
            await self.fraud_upi_ids.create_index("upi_id", unique=True)
            await self.fraud_phone_numbers.create_index("phone", unique=True)
            await self.scam_patterns.create_index("active")
            await self.advisories.create_index("pushed_to_users")
            await self.community_reports.create_index([("reported_by", ASCENDING), ("status", ASCENDING)])
            await self.critical_reports.create_index("case_id", unique=True)
            await self.analysis_history.create_index("user_id")

            logger.info("MongoDB initialized successfully | db=%s", db_name)
        except Exception:
            logger.exception("Failed to initialize MongoDB")
            raise

    async def close(self) -> None:
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    @staticmethod
    def _clean(doc: dict | None) -> dict | None:
        if doc is None:
            return None
        doc["_id"] = str(doc["_id"])
        return doc

    # ── USERS ──────────────────────────────────────────────

    async def get_user(self, telegram_id: str) -> dict | None:
        try:
            doc = await self.users.find_one({"telegram_id": telegram_id})
            return self._clean(doc)
        except Exception:
            logger.exception("get_user failed for %s", telegram_id)
            return None

    async def save_user(self, telegram_id: str, data: dict) -> bool:
        try:
            data["telegram_id"] = telegram_id
            data["joined"] = datetime.now(timezone.utc)
            data["last_active"] = datetime.now(timezone.utc)
            await self.users.insert_one(data)
            return True
        except Exception:
            logger.exception("save_user failed for %s", telegram_id)
            return False

    async def update_user(self, telegram_id: str, fields: dict) -> bool:
        try:
            fields["last_active"] = datetime.now(timezone.utc)
            await self.users.update_one({"telegram_id": telegram_id}, {"$set": fields})
            return True
        except Exception:
            logger.exception("update_user failed for %s", telegram_id)
            return False

    # ── FRAUD UPI IDS ──────────────────────────────────────

    async def get_fraud_upi(self, upi_id: str) -> dict | None:
        try:
            doc = await self.fraud_upi_ids.find_one({"upi_id": upi_id})
            return self._clean(doc)
        except Exception:
            logger.exception("get_fraud_upi failed for %s", upi_id)
            return None

    async def save_fraud_upi(self, upi_id: str, data: dict) -> bool:
        try:
            data["upi_id"] = upi_id
            data["first_seen"] = datetime.now(timezone.utc)
            data["last_reported"] = datetime.now(timezone.utc)
            await self.fraud_upi_ids.insert_one(data)
            return True
        except Exception:
            logger.exception("save_fraud_upi failed for %s", upi_id)
            return False

    async def update_fraud_upi(self, upi_id: str, fields: dict) -> bool:
        try:
            await self.fraud_upi_ids.update_one({"upi_id": upi_id}, {"$set": fields})
            return True
        except Exception:
            logger.exception("update_fraud_upi failed for %s", upi_id)
            return False

    async def increment_fraud_upi_report(
        self,
        upi_id: str,
        reported_by: str,
        city: str,
        scam_type: str,
    ) -> dict | None:
        try:
            now = datetime.now(timezone.utc)
            existing = await self.fraud_upi_ids.find_one({"upi_id": upi_id})
            if existing:
                await self.fraud_upi_ids.update_one(
                    {"upi_id": upi_id},
                    {
                        "$inc": {"report_count": 1},
                        "$set": {"last_reported": now, "scam_type": scam_type},
                        "$addToSet": {
                            "reported_cities": city,
                            "reported_by_users": reported_by,
                        },
                    },
                )
            else:
                await self.fraud_upi_ids.insert_one(
                    {
                        "upi_id": upi_id,
                        "report_count": 1,
                        "first_seen": now,
                        "last_reported": now,
                        "scam_type": scam_type,
                        "risk_score": 0,
                        "verified": False,
                        "reported_cities": [city],
                        "reported_by_users": [reported_by],
                    }
                )

            updated = await self.fraud_upi_ids.find_one({"upi_id": upi_id})
            if updated is None:
                return None

            count = updated["report_count"]
            verified = updated.get("verified", False)

            if count >= 10 and verified:
                risk_score = 95
            elif count >= 3 and verified:
                risk_score = 90
            elif count in (1, 2) and verified:
                risk_score = 75
            elif count >= 3 and not verified:
                risk_score = 70
            elif count == 2 and not verified:
                risk_score = 55
            else:
                risk_score = 35

            if count >= 3:
                verified = True

            await self.fraud_upi_ids.update_one(
                {"upi_id": upi_id},
                {"$set": {"risk_score": risk_score, "verified": verified}},
            )

            updated["risk_score"] = risk_score
            updated["verified"] = verified
            return self._clean(updated)
        except Exception:
            logger.exception("increment_fraud_upi_report failed for %s", upi_id)
            return None

    # ── FRAUD PHONE NUMBERS ────────────────────────────────

    async def get_fraud_phone(self, phone: str) -> dict | None:
        try:
            doc = await self.fraud_phone_numbers.find_one({"phone": phone})
            return self._clean(doc)
        except Exception:
            logger.exception("get_fraud_phone failed for %s", phone)
            return None

    async def increment_fraud_phone_report(self, phone: str, scam_type: str) -> dict | None:
        try:
            now = datetime.now(timezone.utc)
            existing = await self.fraud_phone_numbers.find_one({"phone": phone})
            if existing:
                await self.fraud_phone_numbers.update_one(
                    {"phone": phone},
                    {
                        "$inc": {"report_count": 1},
                        "$set": {"last_reported": now},
                        "$addToSet": {"scam_types": scam_type},
                    },
                )
            else:
                await self.fraud_phone_numbers.insert_one(
                    {
                        "phone": phone,
                        "report_count": 1,
                        "scam_types": [scam_type],
                        "first_seen": now,
                        "last_reported": now,
                        "risk_score": 0,
                        "verified": False,
                    }
                )

            updated = await self.fraud_phone_numbers.find_one({"phone": phone})
            if updated is None:
                return None

            count = updated["report_count"]
            verified = updated.get("verified", False)

            if count >= 10 and verified:
                risk_score = 95
            elif count >= 3 and verified:
                risk_score = 90
            elif count in (1, 2) and verified:
                risk_score = 75
            elif count >= 3 and not verified:
                risk_score = 70
            elif count == 2 and not verified:
                risk_score = 55
            else:
                risk_score = 35

            if count >= 3:
                verified = True

            await self.fraud_phone_numbers.update_one(
                {"phone": phone},
                {"$set": {"risk_score": risk_score, "verified": verified}},
            )

            updated["risk_score"] = risk_score
            updated["verified"] = verified
            return self._clean(updated)
        except Exception:
            logger.exception("increment_fraud_phone_report failed for %s", phone)
            return None

    # ── COMMUNITY REPORTS ──────────────────────────────────

    async def save_community_report(self, data: dict) -> str | None:
        try:
            data["submitted_at"] = datetime.now(timezone.utc)
            result = await self.community_reports.insert_one(data)
            return str(result.inserted_id)
        except Exception:
            logger.exception("save_community_report failed")
            return None

    async def get_community_reports(self, limit: int = 20) -> list:
        try:
            cursor = self.community_reports.find().sort("submitted_at", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [self._clean(d) for d in docs if d is not None]
        except Exception:
            logger.exception("get_community_reports failed")
            return []

    async def update_community_report_status(self, doc_id: str, status: str) -> bool:
        try:
            from bson.objectid import ObjectId

            update: dict[str, Any] = {"status": status}
            if status == "verified":
                update["verified_at"] = datetime.now(timezone.utc)
            await self.community_reports.update_one(
                {"_id": ObjectId(doc_id)}, {"$set": update}
            )
            return True
        except Exception:
            logger.exception("update_community_report_status failed for %s", doc_id)
            return False

    # ── ADVISORIES ─────────────────────────────────────────

    async def save_advisory(self, data: dict) -> str | None:
        try:
            data["ingested_at"] = datetime.now(timezone.utc)
            data["pushed_to_users"] = False
            result = await self.advisories.insert_one(data)
            return str(result.inserted_id)
        except Exception:
            logger.exception("save_advisory failed")
            return None

    async def get_unpushed_advisories(self) -> list:
        try:
            cursor = (
                self.advisories.find({"pushed_to_users": False})
                .sort("ingested_at", -1)
            )
            docs = await cursor.to_list(length=None)
            return [self._clean(d) for d in docs if d is not None]
        except Exception:
            logger.exception("get_unpushed_advisories failed")
            return []

    async def mark_advisory_pushed(self, doc_id: str) -> bool:
        try:
            from bson.objectid import ObjectId

            await self.advisories.update_one(
                {"_id": ObjectId(doc_id)}, {"$set": {"pushed_to_users": True}}
            )
            return True
        except Exception:
            logger.exception("mark_advisory_pushed failed for %s", doc_id)
            return False

    async def get_recent_advisories(self, limit: int = 3) -> list:
        try:
            cursor = self.advisories.find().sort("ingested_at", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [self._clean(d) for d in docs if d is not None]
        except Exception:
            logger.exception("get_recent_advisories failed")
            return []

    # ── CRITICAL REPORTS ───────────────────────────────────

    async def save_critical_report(self, data: dict) -> str | None:
        try:
            today = datetime.now(timezone.utc).strftime("%Y%m%d")
            rand = f"{random.randint(0, 9999):04d}"
            case_id = f"FS-{today}-{rand}"
            data["case_id"] = case_id
            data["reported_at"] = datetime.now(timezone.utc)
            await self.critical_reports.insert_one(data)
            return case_id
        except Exception:
            logger.exception("save_critical_report failed")
            return None

    # ── ANALYSIS HISTORY ───────────────────────────────────

    async def save_analysis_history(self, user_id: str, result: dict) -> bool:
        try:
            doc = dict(result)
            doc["user_id"] = user_id
            doc["analysed_at"] = datetime.now(timezone.utc)
            doc["deleted"] = False
            await self.analysis_history.insert_one(doc)
            return True
        except Exception:
            logger.exception("save_analysis_history failed for user %s", user_id)
            return False

    async def get_user_history(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list, int]:
        try:
            query = {"user_id": user_id, "deleted": False}
            total = await self.analysis_history.count_documents(query)
            cursor = (
                self.analysis_history.find(query)
                .sort("analysed_at", -1)
                .skip(offset)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            return [self._clean(d) for d in docs if d is not None], total
        except Exception:
            logger.exception("get_user_history failed for %s", user_id)
            return [], 0

    async def get_history_item(self, doc_id: str, user_id: str) -> dict | None:
        try:
            from bson.objectid import ObjectId

            doc = await self.analysis_history.find_one(
                {"_id": ObjectId(doc_id), "user_id": user_id}
            )
            return self._clean(doc)
        except Exception:
            logger.exception("get_history_item failed for %s", doc_id)
            return None

    async def soft_delete_history(self, doc_id: str, user_id: str) -> bool:
        try:
            from bson.objectid import ObjectId

            result = await self.analysis_history.update_one(
                {"_id": ObjectId(doc_id), "user_id": user_id},
                {"$set": {"deleted": True}},
            )
            return result.modified_count > 0
        except Exception:
            logger.exception("soft_delete_history failed for %s", doc_id)
            return False

    async def get_user_history_stats(self, user_id: str) -> dict:
        try:
            pipeline = [
                {"$match": {"user_id": user_id, "deleted": False}},
                {
                    "$group": {
                        "_id": None,
                        "total_checks": {"$sum": 1},
                        "high_risk_caught": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "HIGH"]}, 1, 0]}
                        },
                        "medium_risk_caught": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "MEDIUM"]}, 1, 0]}
                        },
                        "safe_checks": {
                            "$sum": {"$cond": [{"$eq": ["$risk_level", "SAFE"]}, 1, 0]}
                        },
                        "critical_cases": {
                            "$sum": {"$cond": [{"$eq": ["$is_critical", True]}, 1, 0]}
                        },
                    },
                },
            ]
            cursor = self.analysis_history.aggregate(pipeline)
            results = await cursor.to_list(length=1)
            if not results:
                return {
                    "total_checks": 0,
                    "high_risk_caught": 0,
                    "medium_risk_caught": 0,
                    "safe_checks": 0,
                    "critical_cases": 0,
                    "scams_prevented_estimate": 0,
                }
            r = results[0]
            high = r.get("high_risk_caught", 0)
            critical = r.get("critical_cases", 0)
            return {
                "total_checks": r.get("total_checks", 0),
                "high_risk_caught": high,
                "medium_risk_caught": r.get("medium_risk_caught", 0),
                "safe_checks": r.get("safe_checks", 0),
                "critical_cases": critical,
                "scams_prevented_estimate": high + critical,
            }
        except Exception:
            logger.exception("get_user_history_stats failed for %s", user_id)
            return {
                "total_checks": 0,
                "high_risk_caught": 0,
                "medium_risk_caught": 0,
                "safe_checks": 0,
                "critical_cases": 0,
                "scams_prevented_estimate": 0,
            }

    # ── USERS QUERY HELPERS ────────────────────────────────

    async def get_users_by_city(self, city: str) -> list:
        try:
            cursor = self.users.find(
                {"city": city, "proactive_enabled": True}
            )
            docs = await cursor.to_list(length=None)
            return [self._clean(d) for d in docs if d is not None]
        except Exception:
            logger.exception("get_users_by_city failed for %s", city)
            return []

    async def get_users_by_alert_frequency(self, frequency: str) -> list:
        try:
            cursor = self.users.find({"alert_frequency": frequency})
            docs = await cursor.to_list(length=None)
            return [self._clean(d) for d in docs if d is not None]
        except Exception:
            logger.exception("get_users_by_alert_frequency failed for %s", frequency)
            return []

    async def get_top_reporters(self, limit: int = 10) -> list:
        try:
            cursor = (
                self.users.find()
                .sort("guardian_points", -1)
                .limit(limit)
            )
            docs = await cursor.to_list(length=limit)
            result = []
            for d in docs:
                if d is None:
                    continue
                cleaned = self._clean(d)
                if cleaned:
                    result.append(
                        {
                            "telegram_id": cleaned.get("telegram_id"),
                            "name": cleaned.get("name"),
                            "city": cleaned.get("city"),
                            "guardian_points": cleaned.get("guardian_points", 0),
                            "badges": cleaned.get("badges", []),
                        }
                    )
            return result
        except Exception:
            logger.exception("get_top_reporters failed")
            return []

    # ── POINTS AND BADGES ──────────────────────────────────

    async def award_points(self, telegram_id: str, points: int) -> int:
        try:
            result = await self.users.find_one_and_update(
                {"telegram_id": telegram_id},
                {"$inc": {"guardian_points": points}},
                projection={"guardian_points": True},
                return_document=True,
            )
            if result:
                return result.get("guardian_points", 0)
            return 0
        except Exception:
            logger.exception("award_points failed for %s", telegram_id)
            return 0

    async def add_badge(self, telegram_id: str, badge: str) -> bool:
        try:
            await self.users.update_one(
                {"telegram_id": telegram_id},
                {"$addToSet": {"badges": badge}},
            )
            return True
        except Exception:
            logger.exception("add_badge failed for %s", telegram_id)
            return False

    async def get_community_stats(self) -> dict:
        try:
            total_upi_ids = await self.fraud_upi_ids.count_documents({})
            total_phones = await self.fraud_phone_numbers.count_documents({})
            total_reports = await self.community_reports.count_documents({})
            verified_reports = await self.community_reports.count_documents(
                {"status": "verified"}
            )

            top_scam_type = "Unknown"
            top_city = "Unknown"

            scam_pipeline = [
                {"$group": {"_id": "$scam_type", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 1},
            ]
            scam_cursor = self.community_reports.aggregate(scam_pipeline)
            scam_results = await scam_cursor.to_list(length=1)
            if scam_results:
                top_scam_type = scam_results[0]["_id"] or "Unknown"

            city_pipeline = [
                {"$unwind": "$reported_cities"},
                {"$group": {"_id": "$reported_cities", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 1},
            ]
            city_cursor = self.fraud_upi_ids.aggregate(city_pipeline)
            city_results = await city_cursor.to_list(length=1)
            if city_results:
                top_city = city_results[0]["_id"] or "Unknown"

            return {
                "total_upi_ids_reported": total_upi_ids,
                "total_phone_numbers_reported": total_phones,
                "total_community_reports": total_reports,
                "verified_reports": verified_reports,
                "top_scam_type": top_scam_type,
                "top_city": top_city,
            }
        except Exception:
            logger.exception("get_community_stats failed")
            return {
                "total_upi_ids_reported": 0,
                "total_phone_numbers_reported": 0,
                "total_community_reports": 0,
                "verified_reports": 0,
                "top_scam_type": "Unknown",
                "top_city": "Unknown",
            }
