import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


async def send_password_reset_email(email: str, token: str) -> None:
    reset_link = f"http://localhost:5173/reset-password?token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset Your Password"
    msg["From"] = settings.GMAIL_USER
    msg["To"] = email

    html = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password. 
        This link expires in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        <a href="{reset_link}">Reset Password</a>
        <p>If you did not request this, please ignore this email.</p>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
        server.sendmail(settings.GMAIL_USER, email, msg.as_string())