"""
Handles /check command, image uploads, and text UPI/phone lookups.
"""

import io
import logging
import os
from typing import Optional

import httpx
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler

from database.mongo import MongoClient
from database.redis import RedisClient
from services.alert_service import AlertService

logger = logging.getLogger(__name__)

WAITING_FOR_INPUT = 0

firestore = MongoClient()
redis = RedisClient()
_alert_service: Optional[AlertService] = None


def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService(
            bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER"),
            smtp_pass=os.getenv("SMTP_PASS"),
        )
    return _alert_service


ANALYSIS_API_URL = os.getenv("ANALYSIS_API_URL", "")
RAZORPAY_PRO_LINK = os.getenv("RAZORPAY_PRO_PLAN_LINK", "")


async def check_command(update: Update, context):
    user_id = str(update.effective_user.id)

    user = await redis.get_cached_user(user_id)
    if user is None:
        user = await firestore.get_user(user_id)
        if user:
            await redis.set_cached_user(user_id, user)
    if user is None:
        await update.message.reply_text(
            "Pehle /start se setup karein. Phir /check use karein."
        )
        return ConversationHandler.END

    allowed = await redis.check_rate_limit(user_id, "check", 10)
    if not allowed:
        await update.message.reply_text(
            "Thoda wait karo bhai, bahut fast hai! "
            "Try again in a minute. ⏳"
        )
        return ConversationHandler.END

    checks_used = user.get("checks_used", 0)
    checks_limit = user.get("checks_limit", 5)

    if checks_used >= checks_limit:
        await update.message.reply_text(
            "⚠️ Aapka monthly check limit khatam ho gaya hai.\n\n"
            f"FraudShield Pro = ₹49/month\n"
            "Teen cups chai se bhi sasta — aur poora mahine protected. ☕\n\n"
            f"Upgrade karo: {RAZORPAY_PRO_LINK}"
        )
        return ConversationHandler.END

    if checks_used == checks_limit - 1:
        context.user_data["warn_upgrade"] = True

    await update.message.reply_text(
        "Screenshot bhejo ya UPI ID paste karo 👇\n"
        "(Image ya text dono accept hoga)"
    )
    return WAITING_FOR_INPUT


async def image_received(update: Update, context):
    user_id = str(update.effective_user.id)

    user = await firestore.get_user(user_id)
    if user is None:
        await update.message.reply_text("Pehle /start se setup karein.")
        return ConversationHandler.END

    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    sent_msg = await update.message.reply_text("Analysing... 🔍")

    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        photo_bytes = io.BytesIO()
        await file.download_to_memory(photo_bytes)
        photo_bytes.seek(0)

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                ANALYSIS_API_URL,
                files={"file": ("screenshot.jpg", photo_bytes, "image/jpeg")},
            )
            resp.raise_for_status()
            result = resp.json()

        await get_alert_service().send_result_alert(user_id, result)

        await firestore.save_analysis_history(user_id, result)

        new_used = user.get("checks_used", 0) + 1
        await firestore.update_user(user_id, {"checks_used": new_used})
        await redis.invalidate_user(user_id)

        await firestore.award_points(user_id, 2)
        await firestore.update_user(user_id, {})

        risk = result.get("risk_level")
        upi_ids = result.get("upi_ids_found", [])
        if risk == "HIGH" and upi_ids:
            await update.message.reply_text(
                f"💡 Yeh scam report karo: /report {upi_ids[0]}"
            )

        if context.user_data.get("warn_upgrade"):
            await update.message.reply_text(
                "⚠️ Aapka sirf 1 free check bacha hai is mahine.\n\n"
                "FraudShield Pro = ₹49/month\n"
                "Teen cups chai se bhi sasta — "
                "aur poora mahine protected. ☕\n\n"
                f"👇 Upgrade karo:\n{RAZORPAY_PRO_LINK}"
            )
            context.user_data["warn_upgrade"] = False

    except httpx.HTTPError:
        logger.exception("Analysis API call failed")
        await update.message.reply_text(
            "Analysis fail ho gayi. Please try again. 🔄"
        )
    except Exception:
        logger.exception("Image analysis failed")
        await update.message.reply_text(
            "Analysis fail ho gayi. Please try again. 🔄"
        )
    finally:
        try:
            await sent_msg.delete()
        except Exception:
            pass

    return ConversationHandler.END


async def text_received(update: Update, context):
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)

    user = await firestore.get_user(user_id)
    if user is None:
        await update.message.reply_text("Pehle /start se setup karein.")
        return ConversationHandler.END

    is_upi = "@" in text and len(text) >= 5
    is_phone = text.isdigit() and len(text) == 10

    if not is_upi and not is_phone:
        await update.message.reply_text(
            "Yeh UPI ID ya phone number nahi lagta.\n"
            "UPI ID: example@paytm\n"
            "Phone: 10 digits\n\n"
            "Ya phir ek screenshot bhejo. 📸"
        )
        return WAITING_FOR_INPUT

    cached = None
    if is_upi:
        cached = await redis.get_cached_upi(text)
    else:
        cached = await redis.get_cached_phone(text)

    if cached:
        result = cached
    elif is_upi:
        doc = await firestore.get_fraud_upi(text)
        if doc:
            result = doc
            await redis.set_cached_upi(text, doc)
        else:
            result = None
    else:
        doc = await firestore.get_fraud_phone(text)
        if doc:
            result = doc
            await redis.set_cached_phone(text, doc)
        else:
            result = None

    if result:
        risk_score = result.get("risk_score", 0)
        if risk_score >= 70:
            risk_icon = "🔴 HIGH RISK"
        elif risk_score >= 35:
            risk_icon = "🟡 MEDIUM RISK"
        else:
            risk_icon = "🟢 LOW RISK"

        verified = result.get("verified", False)
        verified_str = "Yes" if verified else "No"
        count = result.get("report_count", 0)
        scam_type = result.get("scam_type", "N/A")
        first_seen = result.get("first_seen", "")
        if hasattr(first_seen, "strftime"):
            first_seen = first_seen.strftime("%d %b %Y")
        else:
            first_seen = str(first_seen)[:10]

        msg = (
            "━━━━━━━━━━━━━━━━━━━\n"
            "🔍 FraudShield Lookup\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{risk_icon}\n\n"
            f"📋 {'UPI ID' if is_upi else 'Phone'}: {text}\n"
            f"📊 Reports: {count} users ne report kiya\n"
            f"🏷️ Scam Type: {scam_type}\n"
            f"📅 First seen: {first_seen}\n"
            f"✅ Verified: {verified_str}\n\n"
            "⚠️ Do NOT send money to this ID.\n\n"
            "Suspicious laga? /report karein"
        )
    else:
        msg = (
            "✅ No fraud reports found for this ID.\n\n"
            "Par phir bhi savdhaan rahein — "
            "naye scam IDs hamari DB mein nahi hote turant. 🛡️\n\n"
            "Suspicious laga? /report karein"
        )

    await update.message.reply_text(msg)
    return ConversationHandler.END


async def cancel(update: Update, context):
    await update.message.reply_text("Check cancel kar diya. /check phir se karein.")
    context.user_data.clear()
    return ConversationHandler.END


check_command_handler = ConversationHandler(
    entry_points=[CommandHandler("check", check_command)],
    states={
        WAITING_FOR_INPUT: [
            MessageHandler(filters.PHOTO, image_received),
            MessageHandler(filters.TEXT & ~filters.COMMAND, text_received),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="check_conversation",
    persistent=False,
)

image_handler = MessageHandler(filters.PHOTO, image_received)
text_lookup_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, text_received)
