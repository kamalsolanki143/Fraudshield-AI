"""
FastAPI router for analysis history.
Prefix: /history
"""

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from database.mongo import MongoClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["History"])

firestore = MongoClient()


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


@router.get("/")
async def get_history(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(verify_token),
):
    try:
        history_list, total = await firestore.get_user_history(
            user_id, limit=limit, offset=offset
        )
        return {
            "history": history_list,
            "total": total,
            "has_more": (offset + limit) < total,
        }
    except Exception:
        logger.exception("Failed to fetch history for user %s", user_id)
        raise HTTPException(status_code=500, detail="Failed to fetch history")


@router.get("/{history_id}")
async def get_history_item(
    history_id: str,
    user_id: str = Depends(verify_token),
):
    try:
        item = await firestore.get_history_item(history_id, user_id)
        if not item:
            raise HTTPException(status_code=404, detail="History item not found")
        return item
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to fetch history item %s", history_id)
        raise HTTPException(status_code=500, detail="Failed to fetch history item")


@router.delete("/{history_id}")
async def delete_history_item(
    history_id: str,
    user_id: str = Depends(verify_token),
):
    try:
        deleted = await firestore.soft_delete_history(history_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="History item not found or unauthorized")
        return {"success": True, "message": "History item deleted"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to delete history item %s", history_id)
        raise HTTPException(status_code=500, detail="Failed to delete history item")


@router.get("/stats/summary")
async def get_history_stats(user_id: str = Depends(verify_token)):
    try:
        stats = await firestore.get_user_history_stats(user_id)
        return stats
    except Exception:
        logger.exception("Failed to fetch history stats for user %s", user_id)
        raise HTTPException(status_code=500, detail="Failed to fetch stats")
