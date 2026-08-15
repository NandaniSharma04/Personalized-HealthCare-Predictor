import smtplib
from email.message import EmailMessage
import logging
from .core.config import settings

logger = logging.getLogger(__name__)


def send_email(subject: str, body: str, to: str):
    # Simple SMTP sender using localhost or configured SMTP. For production, use a third-party service.
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.DATABASE_URL.split("@")[0] if settings.DATABASE_URL else "noreply@example.com"
        msg["To"] = to
        msg.set_content(body)
        with smtplib.SMTP("localhost") as s:
            s.send_message(msg)
        return True
    except Exception as e:
        logger.warning("Failed to send email: %s", e)
        return False
