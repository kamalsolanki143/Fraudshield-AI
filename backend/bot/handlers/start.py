"""
Telegram ConversationHandler for /start command.
Onboards new users with name, city, alert frequency, and Fraud IQ quiz.
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

from database.mongo import MongoClient
from services.report_service import ReportService

logger = logging.getLogger(__name__)

(
    GET_NAME,
    GET_CITY,
    GET_ALERT_FREQ,
    QUIZ_Q1,
    QUIZ_Q2,
    QUIZ_Q3,
    QUIZ_Q4,
    QUIZ_Q5,
) = range(8)

firestore = MongoClient()
report_service = ReportService()

WELCOME_LOGO = (
    "╔═══════════════════════╗\n"
    "║   🛡️  FraudShield     ║\n"
    "║  Real-time UPI Fraud  ║\n"
    "║     Detection AI      ║\n"
    "╚═══════════════════════╝"
)

CITIES = ["Mumbai", "Delhi", "Bangalore", "Kolkata", "Chennai", "Hyderabad", "Pune", "Other"]

ALERT_OPTIONS = [
    ("⚡ Instant Alerts", "instant"),
    ("📰 Daily Digest", "digest"),
    ("📋 Weekly Summary", "weekly"),
]

QUIZ = [
    {
        "question": (
            "Q1. A stranger offers to send you ₹500 via UPI. They send a "
            "collect request. What does approving it do?"
        ),
        "options": [
            ("A) Credits ₹500 to your account", "wrong"),
            ("B) Debits money FROM your account", "correct"),
            ("C) Nothing, it's just a request", "wrong"),
        ],
    },
    {
        "question": (
            "Q2. You get an SMS: Your KYC expired, account will be blocked. "
            "Update now at a link. What do you do?"
        ),
        "options": [
            ("A) Click the link immediately", "wrong"),
            ("B) Call your bank's official number", "correct"),
            ("C) Reply STOP to the SMS", "wrong"),
        ],
    },
    {
        "question": (
            "Q3. A QR code at a shop shows ₹2,500 pre-filled. Is this normal?"
        ),
        "options": [
            ("A) Yes, shops often do this", "wrong"),
            ("B) No, QR codes should never have pre-filled amounts", "correct"),
            ("C) Only if it's a big brand shop", "wrong"),
        ],
    },
    {
        "question": (
            "Q4. Someone calls claiming to be from Google Pay support and asks "
            "for your UPI PIN. What do you do?"
        ),
        "options": [
            ("A) Share it, they need it to fix your account", "wrong"),
            ("B) Never share UPI PIN with anyone ever", "correct"),
            ("C) Share only the first 2 digits", "wrong"),
        ],
    },
    {
        "question": (
            "Q5. You won a ₹10,000 lottery via WhatsApp. They ask for ₹200 "
            "processing fee via UPI. This is:"
        ),
        "options": [
            ("A) Legitimate, fees are normal", "wrong"),
            ("B) A scam, legitimate lotteries never ask for fees", "correct"),
            ("C) Real only if it's from a known brand", "wrong"),
        ],
    },
]


def _city_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for c in CITIES:
        row.append(InlineKeyboardButton(c, callback_data=f"city:{c}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def _alert_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"alert:{val}")]
        for label, val in ALERT_OPTIONS
    ]
    return InlineKeyboardMarkup(buttons)


def _quiz_keyboard(q_num: int) -> InlineKeyboardMarkup:
    q = QUIZ[q_num]
    buttons = []
    for label, _ in q["options"]:
        prefix = chr(65 + len(buttons))
        buttons.append(
            [InlineKeyboardButton(label, callback_data=f"quiz:{q_num}:{prefix}")]
        )
    return InlineKeyboardMarkup(buttons)


async def start_command(update: Update, context):
    user = update.effective_user
    context.user_data.clear()
    await update.message.reply_text(
        f"{WELCOME_LOGO}\n\n"
        f"Namaste {user.first_name}! Main hoon FraudShield 🛡️\n"
        "Aapka personal UPI fraud detector.\n\n"
        "Chaliye shuru karte hain — pehle aapka naam batayein? 👇"
    )
    return GET_NAME


async def get_name(update: Update, context):
    name = update.message.text.strip()
    if len(name) < 2 or len(name) > 50:
        await update.message.reply_text("Naam 2-50 characters ka hona chahiye. Phir batao?")
        return GET_NAME
    context.user_data["name"] = name
    await update.message.reply_text(
        f"Bahut khoob, {name}! 🎉\n\nAap kaunse city mein rehte hain?",
        reply_markup=_city_keyboard(),
    )
    return GET_CITY


async def get_city(update: Update, context):
    query = update.callback_query
    await query.answer()
    city = query.data.split(":", 1)[1]
    context.user_data["city"] = city
    await query.edit_message_text(
        f"📍 {city} — achha city hai!\n\n"
        "Ab alert frequency chuniye — kaise updates chahiye?",
        reply_markup=_alert_keyboard(),
    )
    return GET_ALERT_FREQ


async def get_alert_freq(update: Update, context):
    query = update.callback_query
    await query.answer()
    freq = query.data.split(":", 1)[1]
    context.user_data["alert_frequency"] = freq
    await query.edit_message_text(
        "🧠 Ab ek chhota Fraud IQ Quiz! 🧠\n\n"
        "5 sawaal hain — jo utna aware, utna safe.\n\n"
        "Chaliye shuru karte hain! 🚀\n\n"
        "Question 1/5 🧠",
        reply_markup=_quiz_keyboard(0),
    )
    return QUIZ_Q1


async def _handle_quiz_answer(update: Update, context, q_num: int, next_state: int):
    query = update.callback_query
    await query.answer()
    parts = query.data.split(":")
    selected = parts[2]
    q = QUIZ[q_num]
    option_idx = ord(selected) - 65
    if 0 <= option_idx < len(q["options"]):
        label, correctness = q["options"][option_idx]
        if correctness == "correct":
            context.user_data["quiz_score"] = context.user_data.get("quiz_score", 0) + 1

    total = len(QUIZ)
    if q_num + 1 < total:
        await query.edit_message_text(
            f"Question {q_num + 2}/{total} 🧠",
            reply_markup=_quiz_keyboard(q_num + 1),
        )
        return next_state

    return await _finish_quiz(update, context, query)


async def _finish_quiz(update: Update, context, query):
    score = context.user_data.get("quiz_score", 0)
    if score <= 2:
        risk_profile = "novice"
    elif score <= 4:
        risk_profile = "aware"
    else:
        risk_profile = "vigilant"

    context.user_data["risk_profile"] = risk_profile
    name = context.user_data.get("name", "User")
    city = context.user_data.get("city", "Unknown")
    freq = context.user_data.get("alert_frequency", "instant")
    user_id = str(update.effective_user.id)

    await firestore.save_user(
        user_id,
        {
            "name": name,
            "phone_last4": "",
            "plan": "free",
            "checks_used": 0,
            "checks_limit": 5,
            "guardian_points": 0,
            "badges": [],
            "city": city,
            "risk_profile": risk_profile,
            "alert_frequency": freq,
            "proactive_enabled": True,
            "referred_by": None,
        },
    )

    new_total = await report_service.award_points(user_id, "quiz_completion")

    profile_map = {"novice": "🔵 Novice (Beginner)", "aware": "🟡 Aware", "vigilant": "🟢 Vigilant"}
    await query.edit_message_text(
        f"✅ Setup complete, {name}!\n\n"
        f"Your profile:\n"
        f"📍 City: {city}\n"
        f"🎯 Risk Level: {profile_map.get(risk_profile, risk_profile)}\n"
        f"🔔 Alerts: {freq}\n"
        f"⭐ Points: {new_total} (quiz bonus!)\n\n"
        "Commands:\n"
        "/check — Analyse a screenshot\n"
        "/lookup — Check any UPI ID\n"
        "/report — Report a scammer\n"
        "/status — Your account\n"
        "/tip — Fraud awareness tip\n"
        "/help — All commands\n\n"
        "Shuru karo! 🚀"
    )
    return ConversationHandler.END


async def quiz_q1(update: Update, context):
    return await _handle_quiz_answer(update, context, 0, QUIZ_Q2)


async def quiz_q2(update: Update, context):
    return await _handle_quiz_answer(update, context, 1, QUIZ_Q3)


async def quiz_q3(update: Update, context):
    return await _handle_quiz_answer(update, context, 2, QUIZ_Q4)


async def quiz_q4(update: Update, context):
    return await _handle_quiz_answer(update, context, 3, QUIZ_Q5)


async def quiz_q5(update: Update, context):
    return await _handle_quiz_answer(update, context, 4, -1)


async def cancel(update: Update, context):
    await update.message.reply_text(
        "Setup cancel ho gaya. /start se phir se shuru karein."
    )
    context.user_data.clear()
    return ConversationHandler.END


start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        GET_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)
        ],
        GET_CITY: [CallbackQueryHandler(get_city, pattern=r"^city:")],
        GET_ALERT_FREQ: [CallbackQueryHandler(get_alert_freq, pattern=r"^alert:")],
        QUIZ_Q1: [CallbackQueryHandler(quiz_q1, pattern=r"^quiz:0:")],
        QUIZ_Q2: [CallbackQueryHandler(quiz_q2, pattern=r"^quiz:1:")],
        QUIZ_Q3: [CallbackQueryHandler(quiz_q3, pattern=r"^quiz:2:")],
        QUIZ_Q4: [CallbackQueryHandler(quiz_q4, pattern=r"^quiz:3:")],
        QUIZ_Q5: [CallbackQueryHandler(quiz_q5, pattern=r"^quiz:4:")],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False,
    name="start_onboarding",
    persistent=False,
)

cancel_handler = CommandHandler("cancel", cancel)
