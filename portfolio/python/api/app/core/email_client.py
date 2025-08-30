import smtplib
from email.message import EmailMessage
from environs import Env

from app.core.logging_config import get_logger
from app.config import settings

env = Env()

logger = get_logger(__name__)


def send_forgot_password_email(recipient_email: str, reset_url: str):
    """
    Sends a password reset email with a unique token.
    """
    try:
        logger.info(f"Sending forgot password email to {recipient_email}")

        msg = EmailMessage()
        msg["Subject"] = "Password Reset Request"
        msg["From"] = settings.EMAIL_HOST_USER
        msg["To"] = recipient_email

        html_template_path = settings.STATIC_FILE_PATH / "password_reset_email.html"
        if not html_template_path.exists():
            print(f"Error: The HTML file {html_template_path} was not found.")
            return

        html_content = html_template_path.read_text()
        # Simple placeholder replacement. For complex templates,
        # a full templating engine like Jinja2 is recommended.
        html_content = html_content.replace("{{reset_link}}", reset_url)
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.set_debuglevel(1)
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.send_message(msg)
            logger.info(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
