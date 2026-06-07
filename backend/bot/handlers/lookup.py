"""
Handles /lookup command — looks up a UPI ID or phone number in the fraud database.
"""

import logging

from telegram import Update
from telegram.ext import CommandHandler

from database.mongo import MongoClient
from database.redis import RedisClient

logger = logging.getLogger(__name__)

firestore = MongoClient()
redis = RedisClient()


async def lookup_handler(update: Update, context):
    args = context.args

    if not args:
        await update.message.reply_text(
            "Usage: /lookup <UPI ID ya phone number>\n\n"
            "Example:\n"
            "/lookup example@paytm\n"
            "/lookup 9876543210"
        )
        return

    identifier = args[0].strip()
    is_upi = "@" in identifier and len(identifier) >= 5
    is_phone = identifier.isdigit() and len(identifier) == 10

    if not is_upi and not is_phone:
        await update.message.reply_text(
            "Galat format. Yeh lo sahi format:\n\n"
            "UPI ID: example@paytm\n"
            "Phone: 9876543210 (10 digits)"
        )
        return

    if is_upi:
        cached = await redis.get_cached_upi(identifier)
        if cached:
            doc = cached
        else:
            doc = await firestore.get_fraud_upi(identifier)
            if doc:
                await redis.set_cached_upi(identifier, doc)
    else:
        cached = await redis.get_cached_phone(identifier)
        if cached:
            doc = cached
        else:
            doc = await firestore.get_fraud_phone(identifier)
            if doc:
                await redis.set_cached_phone(identifier, doc)

    if doc:
        risk_score = doc.get("risk_score", 0)
        if risk_score >= 70:
            risk_icon = "🔴 HIGH RISK"
        elif risk_score >= 35:
            risk_icon = "🟡 MEDIUM RISK"
        else:
            risk_icon = "🟢 LOW RISK"

        verified = doc.get("verified", False)
        verified_str = "Yes ✅" if verified else "No ❌"
        count = doc.get("report_count", 0)
        scam_type = doc.get("scam_type", "N/A")
        first_seen = doc.get("first_seen", "")
        if hasattr(first_seen, "strftime"):
            first_seen = first_seen.strftime("%d %b %Y")
        else:
            first_seen = str(first_seen)[:10]

        msg = (
            "━━━━━━━━━━━━━━━━━━━\n"
            "🔍 FraudShield Lookup\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{risk_icon}\n\n"
            f"📋 UPI ID: {identifier}\n"
            f"📊 Reports: {count} users ne report kiya\n"
            f"🏷️ Scam Type: {scam_type}\n"
            f"📅 First seen: {first_seen}\n"
            f"✅ Verified: {verified_str}\n\n"
            "⚠️ Do NOT send money to this ID."
        )
    else:
        msg = (
            "✅ No fraud reports found for this ID.\n\n"
            "Par phir bhi savdhaan rahein — "
            "naye scam IDs hamari DB mein nahi hote turant. 🛡️"
        )

    msg += "\n\nSuspicious laga? /report karein"
    await update.message.reply_text(msg)


lookup_cmd_handler = CommandHandler("lookup", lookup_handler)
