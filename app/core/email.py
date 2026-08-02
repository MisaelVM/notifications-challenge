from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def send_email(
    to_email: str, subject: str, plain_text: str, html_content: str | None = None
) -> tuple[dict[str, aiosmtplib.SMTPResponse], str]:
    message = EmailMessage()
    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(plain_text)

    if html_content:
        message.add_alternative(html_content, subtype="html")

    return await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=settings.mail_port,
        username=settings.mail_username or None,
        password=settings.mail_password.get_secret_value() or None,
        start_tls=settings.mail_use_tls,
    )
