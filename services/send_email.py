from fastapi_mail import FastMail, MessageSchema
from config import conf, reset_link


async def send_password_reset_email(email: str, reset_token: str):

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"""
        Dear user,

        We have received a request to reset your password.
        To reset your password, please click the following link:

        {reset_link+f'{reset_token}'}

        If you did not request a password reset, please ignore this email.

        Best regards,
        Your App Team
        """,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)