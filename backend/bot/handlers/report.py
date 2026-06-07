"""
Telegram ConversationHandler for /report command.
Collects scam type and optional description, submits via ReportService.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    CallbackQueryHandler,
)

from services.report_service import ReportService

logger = logging.getLogger(__name__)

GET_SCAM_TYPE, GET_DESCRIPTION = range(2)

report_service = ReportService()

SCAM_TYPES = [
    ("💸 Fake Refund", "Fake Refund"),
    ("🪪 KYC Scam", "KYC Scam"),
    ("📤 Collect Request", "Collect Request"),
    ("📞 Fake Customer Care", "Fake Customer Care"),
    ("🎰 Lottery Scam", "Lottery Scam"),
    ("❓ Other", "Other"),
]


def _scam_type_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"scam:{val}")]
        for label, val in SCAM_TYPES
    ]
    return InlineKeyboardMarkup(buttons)


async def report_command(update: Update, context):
    args = context.args
    identifier = " ".join(args).strip() if args else ""

    if not identifier:
        await update.message.reply_text(
            "Usage: /report <UPI ID ya phone number>\n\n"
            "Example:\n"
            "/report example@paytm\n"
            "/report 9876543210"
        )
        return ConversationHandler.END

    input_type, sanitised = ReportService.validate_input(identifier)
    if input_type == "invalid":
        await update.message.reply_text(
            "Galat format. Sahi format:\n\n"
            "UPI ID: example@paytm\n"
            "Phone: 9876543210 (10 digits)"
        )
        return ConversationHandler.END

    context.user_data["report_identifier"] = sanitised
    context.user_data["report_type"] = input_type

    await update.message.reply_text(
        f"Identifier: {sanitised}\n\n"
        "Kis type ka scam hai?",
        reply_markup=_scam_type_keyboard(),
    )
    return GET_SCAM_TYPE


async def get_scam_type(update: Update, context):
    query = update.callback_query
    await query.answer()
    scam_type = query.data.split(":", 1)[1]
    context.user_data["scam_type"] = scam_type

    await query.edit_message_text(
        "Ek line mein kya hua batao (optional)\n"
        'Skip karna ho toh /skip type karo.\n\n'
        "Aapke paas 60 seconds hain. ⏱️",
    )
    return GET_DESCRIPTION


async def get_description(update: Update, context):
    description = update.message.text.strip()
    context.user_data["description"] = description
    return await _submit_report(update, context)


async def skip_description(update: Update, context):
    context.user_data["description"] = None
    return await _submit_report(update, context)


async def _submit_report(update: Update, context) -> int:
    user_id = str(update.effective_user.id)
    identifier = context.user_data.get("report_identifier", "")
    scam_type = context.user_data.get("scam_type", "Other")
    description = context.user_data.get("description")

    result = await report_service.submit_report(
        user_id=user_id,
        upi_or_phone=identifier,
        scam_type=scam_type,
        description=description,
    )

    await update.message.reply_text(result["message"])

    if result["badge_earned"]:
        badge_msg = ReportService.get_badge_unlock_message(result["badge_earned"])
        await update.message.reply_text(f"🏅 BADGE UNLOCKED: {result['badge_earned']}\n\n{badge_msg}")

    context.user_data.clear()
    return ConversationHandler.END


async def timeout(update: Update, context):
    await update.message.reply_text(
        "Time khatam! /report phir se karein."
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context):
    await update.message.reply_text(
        "Report cancel kar diya. /report se phir se karein."
    )
    context.user_data.clear()
    return ConversationHandler.END


report_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("report", report_command)],
    states={
        GET_SCAM_TYPE: [
            CallbackQueryHandler(get_scam_type, pattern=r"^scam:")
        ],
        GET_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_description),
            CommandHandler("skip", skip_description),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.COMMAND, timeout),
    ],
    per_message=False,
    conversation_timeout=60,
    name="report_conversation",
    persistent=False,
)
