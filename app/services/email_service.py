import resend
from app.config import settings

resend.api_key = settings.RESEND_API_KEY

async def send_password_reset_email(email: str, token: str) -> None:
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": email,
        "subject": "Reset Your Password",
        "html": f"""
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password. This link expires in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
            <a href="{reset_link}">Reset Password</a>
            <p>If you did not request this, please ignore this email.</p>
        """,
    })