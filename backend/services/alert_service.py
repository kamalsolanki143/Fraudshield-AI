"""
Alert service for FraudShield Telegram bot.
Handles result delivery, critical case escalation, proactive alerts,
and scheduled digest/summary jobs.
"""

from __future__ import annotations

import asyncio
import logging
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.error import TelegramError

from database.mongo import MongoClient
from database.redis import RedisClient

logger = logging.getLogger(__name__)

BATCH_DELAY = 1 / 30


class AlertService:
    def __init__(
        self,
        bot_token: str,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_user: str | None = None,
        smtp_pass: str | None = None,
    ) -> None:
        self.bot = Bot(token=bot_token)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass
        self.firestore = MongoClient()
        self.redis = RedisClient()

    # ── REACTIVE ALERTS ───────────────────────────────────

    async def send_result_alert(self, user_id: str, result: dict) -> bool:
        risk = result.get("risk_level", "UNKNOWN")
        score = result.get("confidence_score", 0)
        scam_type = result.get("scam_type")
        reasons_en = result.get("reasons_en", [])
        reasons_hi = result.get("reasons_hi", [])
        verdict_en = result.get("verdict_en", "")
        verdict_hi = result.get("verdict_hi", "")
        action_en = result.get("action_en", "")
        action_hi = result.get("action_hi", "")
        upi_ids = result.get("upi_ids_found", [])

        if risk == "HIGH":
            symbol = "🔴"
            title = "HIGH RISK"
        elif risk == "MEDIUM":
            symbol = "🟡"
            title = "MEDIUM RISK"
        elif risk == "SAFE":
            symbol = "🟢"
            title = "SAFE"
        else:
            msg = (
                "🤔 Yeh image clear nahi hai.\n\n"
                "Kripya ek achhi quality screenshot bhej\n"
                "jahan UPI ID ya transaction details\n"
                "saaf dikh rahe hon.\n\n"
                "Please retake with better lighting. 📸"
            )
            return await self._send_telegram_message(user_id, msg)

        lines = [
            "━━━━━━━━━━━━━━━━━━━━━",
            "🛡️ FraudShield Analysis",
            "━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"{symbol} {title}  |  Confidence: {score}%",
            "",
        ]
        if scam_type:
            lines.append(f"📌 {scam_type}")
            lines.append("")

        if reasons_en:
            lines.append("⚠️ Red Flags:")
            for r in reasons_en[:3]:
                lines.append(f"- {r}")
            lines.append("")

        if reasons_hi:
            lines.append("🇮🇳 क्यों संदिग्ध है:")
            for r in reasons_hi[:3]:
                lines.append(f"- {r}")
            lines.append("")

        lines.append(f"📋 {verdict_en}")
        lines.append(f"   {verdict_hi}")
        lines.append("")
        lines.append(f"✅ {action_en}")
        lines.append(f"   {action_hi}")
        lines.append("")

        if risk == "HIGH" and upi_ids:
            lines.append(f"⚡ Report: /report {upi_ids[0]}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")

        sent = await self._send_telegram_message(user_id, "\n".join(lines))
        if not sent:
            return False

        if result.get("is_critical"):
            await self.handle_critical_case(user_id, result)

        return True

    async def handle_critical_case(self, user_id: str, result: dict) -> str | None:
        case_id = None
        try:
            upi_ids = result.get("upi_ids_found", [])
            phones = result.get("phone_numbers_found", [])
            scam_type = result.get("scam_type", "Unknown")
            score = result.get("confidence_score", 0)
            loss = result.get("estimated_loss_inr")

            email_tasks = []
            email_tasks.append(self.send_npci_email(result))
            email_tasks.append(self.send_cert_in_email(result))
            npci_ok, cert_ok = await asyncio.gather(*email_tasks)

            complaint = self.generate_complaint_template(result)

            case_id = await self.firestore.save_critical_report(
                {
                    "user_id": user_id,
                    "upi_ids": upi_ids,
                    "phone_numbers": phones,
                    "scam_type": scam_type,
                    "critical_reason": result.get("critical_reason", ""),
                    "confidence_score": score,
                    "estimated_loss_inr": loss,
                    "npci_email_sent": npci_ok,
                    "cert_in_email_sent": cert_ok,
                }
            )

            msg = (
                "🚨 CRITICAL FRAUD DETECTED\n\n"
                f"Estimated amount at risk: ₹{loss or 'Unknown'}\n\n"
                "We have automatically:\n"
                f"{'✅' if npci_ok else '❌'} Reported to NPCI\n"
                f"{'✅' if cert_ok else '❌'} Reported to CERT-In\n\n"
                f"Case ID: {case_id}\n\n"
                "👇 File police complaint — copy this template\n"
                "and paste at cybercrime.gov.in:\n\n"
                f"```\n{complaint}\n```"
            )
            await self._send_telegram_message(user_id, msg)
        except Exception:
            logger.exception("handle_critical_case failed for user %s", user_id)
        return case_id

    async def send_npci_email(self, result: dict) -> bool:
        return await self._send_email(
            to=os.getenv("NPCI_EMAIL", "helpdesk@npci.org.in"),
            subject=(
                f"[FraudShield AUTO-REPORT] {result.get('scam_type', 'Fraud')}"
                f" — Confidence {result.get('confidence_score', 0)}%"
            ),
            body=self._build_email_body(result),
        )

    async def send_cert_in_email(self, result: dict) -> bool:
        return await self._send_email(
            to=os.getenv("CERT_IN_EMAIL", "incident@cert-in.org.in"),
            subject=(
                f"[FraudShield AUTO-REPORT] {result.get('scam_type', 'Fraud')}"
                f" — Confidence {result.get('confidence_score', 0)}%"
            ),
            body=self._build_email_body(result),
        )

    def generate_complaint_template(self, result: dict) -> str:
        upi_ids = ", ".join(result.get("upi_ids_found", [])) or "Not available"
        phones = ", ".join(result.get("phone_numbers_found", [])) or "Not available"
        loss = result.get("estimated_loss_inr", "Unknown")
        score = result.get("confidence_score", 0)
        scam_type = result.get("scam_type", "Unknown")

        return (
            "Complaint Type: Online Financial Fraud / UPI Fraud\n"
            f"Fraud Type: {scam_type}\n"
            f"UPI IDs involved: {upi_ids}\n"
            f"Phone numbers: {phones}\n"
            f"Estimated loss: ₹{loss}\n"
            f"Detection confidence: {score}%\n"
            "Detected by: FraudShield AI System\n"
            f"Description: I received a suspicious {scam_type}. "
            f"The AI fraud detection system flagged this with {score}% confidence. "
            "Please investigate the above UPI IDs and phone numbers."
        )

    async def send_rewatch_alert(self, user_id: str, upi_id: str, new_count: int) -> bool:
        msg = (
            "👀 FraudShield Rewatch\n\n"
            f"UPI ID {upi_id} ko aur {new_count} naye reports aaye hain.\n"
            "Isse avoid karein aur family ko alert karein.\n\n"
            f"/lookup {upi_id} — naya score check karein"
        )
        return await self._send_telegram_message(user_id, msg)

    # ── PROACTIVE ALERTS ──────────────────────────────────

    async def send_city_scam_alert(
        self, city: str, pattern_name: str, description_en: str, description_hi: str
    ) -> int:
        count = 0
        try:
            users = await self.firestore.get_users_by_city(city)
            for user in users:
                uid = user.get("telegram_id")
                if not uid:
                    continue
                msg = (
                    f"⚠️ {city} mein naya scam alert!\n\n"
                    f"Pattern: {pattern_name}\n"
                    f"{description_en}\n\n"
                    f"{description_hi}\n\n"
                    "Sachet rahein, safe rahein. 🛡️"
                )
                ok = await self._send_telegram_message(uid, msg)
                if ok:
                    count += 1
                await asyncio.sleep(BATCH_DELAY)
        except Exception:
            logger.exception("send_city_scam_alert failed for city %s", city)
        return count

    async def push_advisory_alert(self, advisory: dict) -> int:
        count = 0
        try:
            users = await self.firestore.get_users_by_alert_frequency("instant")
            for user in users:
                uid = user.get("telegram_id")
                if not uid:
                    continue
                title = advisory.get("raw_title", "Fraud Advisory")
                severity = advisory.get("severity", "MEDIUM")
                sev_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "ℹ️"}.get(severity, "ℹ️")
                summaries = advisory.get("summary_en", [])
                msg = (
                    f"📢 {sev_icon} Fraud Advisory: {title}\n\n"
                    + "\n".join(f"• {s}" for s in summaries)
                    + "\n\nSafe rahein! 🛡️"
                )
                ok = await self._send_telegram_message(uid, msg)
                if ok:
                    count += 1
                await asyncio.sleep(BATCH_DELAY)

            doc_id = advisory.get("_id")
            if doc_id:
                await self.firestore.mark_advisory_pushed(doc_id)
        except Exception:
            logger.exception("push_advisory_alert failed")
        return count

    # ── SCHEDULED JOBS ────────────────────────────────────

    async def send_daily_digest(self) -> int:
        count = 0
        try:
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)

            top_upis_cursor = self.firestore.fraud_upi_ids.find(
                {"last_reported": {"$gte": yesterday}}
            ).sort("report_count", -1).limit(3)
            top_upis = await top_upis_cursor.to_list(length=3)

            total_checks = await self.firestore.analysis_history.count_documents(
                {"analysed_at": {"$gte": yesterday}}
            )

            high_adv = await self.firestore.advisories.find(
                {"severity": "HIGH", "ingested_at": {"$gte": yesterday}}
            ).to_list(length=5)

            upi_lines = []
            for u in top_upis:
                upi = u.get("upi_id", "Unknown")
                rc = u.get("report_count", 0)
                upi_lines.append(f"🔴 {upi} — {rc} reports")

            msg_parts = ["📰 FraudShield Daily Digest\n"]
            if upi_lines:
                msg_parts.append("Top reported UPI IDs (24h):")
                msg_parts.extend(upi_lines)
            else:
                msg_parts.append("No new UPI reports in last 24 hours.")
            msg_parts.append(f"\nTotal checks performed: {total_checks}")
            if high_adv:
                msg_parts.append(f"\nNew HIGH severity advisories: {len(high_adv)}")

            users = await self.firestore.get_users_by_alert_frequency("digest")
            for user in users:
                uid = user.get("telegram_id")
                if not uid:
                    continue
                ok = await self._send_telegram_message(uid, "\n".join(msg_parts))
                if ok:
                    count += 1
                await asyncio.sleep(BATCH_DELAY)
        except Exception:
            logger.exception("send_daily_digest failed")
        return count

    async def send_weekly_summary(self) -> int:
        count = 0
        try:
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)

            total_checks = await self.firestore.analysis_history.count_documents(
                {"analysed_at": {"$gte": week_ago}}
            )
            high_count = await self.firestore.analysis_history.count_documents(
                {"analysed_at": {"$gte": week_ago}, "risk_level": "HIGH"}
            )
            critical_count = await self.firestore.analysis_history.count_documents(
                {"analysed_at": {"$gte": week_ago}, "is_critical": True}
            )
            new_reports = await self.firestore.community_reports.count_documents(
                {"submitted_at": {"$gte": week_ago}}
            )

            msg = (
                "📋 FraudShield Weekly Summary\n\n"
                f"Total checks this week: {total_checks}\n"
                f"High risk caught: {high_count}\n"
                f"Critical cases: {critical_count}\n"
                f"Community reports: {new_reports}\n\n"
                "Safe rahein, alert rahein! 🛡️"
            )

            users = await self.firestore.get_users_by_alert_frequency("weekly")
            for user in users:
                uid = user.get("telegram_id")
                if not uid:
                    continue
                ok = await self._send_telegram_message(uid, msg)
                if ok:
                    count += 1
                await asyncio.sleep(BATCH_DELAY)
        except Exception:
            logger.exception("send_weekly_summary failed")
        return count

    def setup_scheduler(self) -> AsyncIOScheduler:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            self.send_daily_digest,
            "cron",
            hour=3,
            minute=30,
            id="daily_digest",
            replace_existing=True,
        )
        scheduler.add_job(
            self.send_weekly_summary,
            "cron",
            day_of_week="mon",
            hour=3,
            minute=30,
            id="weekly_summary",
            replace_existing=True,
        )
        logger.info("APScheduler configured: daily 03:30 UTC, Monday 03:30 UTC")
        return scheduler

    # ── HELPERS ───────────────────────────────────────────

    async def _send_telegram_message(self, user_id: str, text: str) -> bool:
        if not user_id:
            return False
        try:
            await self.bot.send_message(chat_id=user_id, text=text)
            return True
        except TelegramError:
            logger.warning("Failed to send Telegram message to %s", user_id)
            return False

    def _build_email_body(self, result: dict) -> str:
        upi_ids = ", ".join(result.get("upi_ids_found", [])) or "None"
        phones = ", ".join(result.get("phone_numbers_found", [])) or "None"
        return (
            f"Fraud Type: {result.get('scam_type', 'Unknown')}\n"
            f"Confidence: {result.get('confidence_score', 0)}%\n"
            f"UPI IDs: {upi_ids}\n"
            f"Phone Numbers: {phones}\n"
            f"Estimated Loss: ₹{result.get('estimated_loss_inr', 'Unknown')}\n"
            f"Verdict: {result.get('verdict_en', '')}\n"
            f"Reasons:\n"
            + "\n".join(f"  - {r}" for r in result.get("reasons_en", []))
            + "\n\n-- FraudShield AI System"
        )

    async def _send_email(self, to: str, subject: str, body: str) -> bool:
        if not self.smtp_user or not self.smtp_pass:
            logger.warning("SMTP not configured — skipping email to %s", to)
            return False
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            logger.info("Email sent to %s: %s", to, subject)
            return True
        except Exception:
            logger.exception("Failed to send email to %s", to)
            return False
