"""
Main Telegram bot entry point for FraudShield.
Initialises all components and starts polling.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal

from telegram.ext import Application, MessageHandler, filters

from bot.handlers.start import start_handler
from bot.handlers.check import check_command_handler
from bot.handlers.lookup import lookup_cmd_handler
from bot.handlers.report import report_conversation_handler
from bot.handlers.help import help_cmd_handler, status_cmd_handler, tip_cmd_handler
from database.mongo import MongoClient
from database.redis import RedisClient
from services.alert_service import AlertService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

firestore = MongoClient()
redis = RedisClient()
_alert_service: AlertService | None = None
application: Application | None = None
scheduler = None


def get_alert_service() -> AlertService:
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService(
            bot_token=BOT_TOKEN,
            smtp_host=SMTP_HOST,
            smtp_port=SMTP_PORT,
            smtp_user=SMTP_USER,
            smtp_pass=SMTP_PASS,
        )
    return _alert_service


async def startup():
    await firestore.initialize()
    await redis.initialize()
    logger.info("FraudShield bot dependencies initialized")


async def shutdown():
    global scheduler, application
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
    if application:
        await application.stop()
        await application.shutdown()
        logger.info("Application stopped")
    await firestore.close()
    await redis.close()
    logger.info("FraudShield bot stopped cleanly")


def build_application() -> Application:
    global application
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(start_handler)
    app.add_handler(lookup_cmd_handler)
    app.add_handler(report_conversation_handler)
    app.add_handler(help_cmd_handler)
    app.add_handler(status_cmd_handler)
    app.add_handler(tip_cmd_handler)
    app.add_handler(check_command_handler)

    catchall = MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda update, context: update.message.reply_text(
            "I didn't understand that. Use /help for commands."
        ),
    )
    app.add_handler(catchall)

    application = app
    return app


async def main():
    global scheduler

    logger.info("Starting FraudShield bot...")

    await startup()

    app = build_application()

    scheduler = get_alert_service().setup_scheduler()
    scheduler.start()
    logger.info("APScheduler started")

    logger.info("Starting polling (drop_pending_updates=True)...")
    await app.run_polling(drop_pending_updates=True)


def handle_exit():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(shutdown())
    finally:
        loop.close()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda s, f: handle_exit())
    signal.signal(signal.SIGINT, lambda s, f: handle_exit())

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        handle_exit()
