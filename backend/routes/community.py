"""
FastAPI router for community features.
Prefix: /community
"""

import json
import logging

from fastapi import APIRouter, HTTPException, Query

from database.mongo import MongoClient
from database.redis import RedisClient
from services.report_service import ReportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/community", tags=["Community"])

firestore = MongoClient()
redis = RedisClient()
report_service = ReportService()

STATS_CACHE_KEY = "community:stats"
STATS_CACHE_TTL = 600


@router.get("/reports")
async def get_community_reports(limit: int = Query(default=20, le=50)):
    try:
        reports = await report_service.get_recent_reports(limit)
        total = len(reports)
        return {"reports": reports, "total": total}
    except Exception:
        logger.exception("Failed to fetch community reports")
        raise HTTPException(status_code=500, detail="Failed to fetch community reports")


@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(default=10)):
    try:
        leaderboard = await report_service.get_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception:
        logger.exception("Failed to fetch leaderboard")
        raise HTTPException(status_code=500, detail="Failed to fetch leaderboard")


@router.get("/stats")
async def get_community_stats():
    try:
        cached = await redis.get(STATS_CACHE_KEY)
        if cached:
            return json.loads(cached)

        stats = await firestore.get_community_stats()
        await redis.set(STATS_CACHE_KEY, json.dumps(stats), STATS_CACHE_TTL)
        return stats
    except Exception:
        logger.exception("Failed to fetch community stats")
        raise HTTPException(status_code=500, detail="Failed to fetch community stats")


@router.get("/patterns")
async def get_scam_patterns():
    try:
        cursor = firestore.scam_patterns.find({"active": True})
        docs = await cursor.to_list(length=None)
        result = []
        for d in docs:
            if d is None:
                continue
            result.append(
                {
                    "name": d.get("name"),
                    "description_en": d.get("description_en"),
                    "description_hi": d.get("description_hi"),
                    "reported_cities": d.get("reported_cities", []),
                }
            )
        return result
    except Exception:
        logger.exception("Failed to fetch scam patterns")
        raise HTTPException(status_code=500, detail="Failed to fetch scam patterns")
