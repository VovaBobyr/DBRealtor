"""Optional email alert on scrape run failure.

Activated by setting ALERT_EMAIL in .env.  No external dependencies — uses
smtplib from the Python standard library.

Usage (called automatically by pipeline on failure):
    from src.alerts.email import send_failure_alert
    send_failure_alert(run_id="abc123", error_summary="UniqueViolationError …")
"""
import os
import smtplib
from email.message import EmailMessage


def send_failure_alert(run_id: str, error_summary: str) -> None:
    """Send one email if ALERT_EMAIL is configured; silently no-op otherwise."""
    to = os.getenv("ALERT_EMAIL")
    if not to:
        return

    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "25"))
    from_addr = os.getenv("SMTP_FROM", "scraper@localhost")

    msg = EmailMessage()
    msg["Subject"] = f"[sreality-scraper] Scrape run failed: {run_id}"
    msg["From"] = from_addr
    msg["To"] = to
    msg.set_content(
        f"Scrape run {run_id} failed.\n\n{error_summary}\n\n"
        f"Check logs/failed_runs.log for details."
    )

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.send_message(msg)
