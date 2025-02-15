import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from app import config

logger = logging.getLogger(__name__)


async def send_welcome_email(email: str, name: str):
    if not config.SEND_EMAILS:
        logger.info(f"Not sending welcome email to {email}")
        return

    subject = "Welcome to {app_name}"

    # HTML version of the email
    html_content = """
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #353535; }}
            .cta-button {{ 
                display: inline-block; 
                padding: 10px 20px; 
                background-color: #007bff; 
                color: #ffffff !important; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 10px 0;
            }}
            .cta-button:visited {{
                color: #ffffff !important;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to {app_name}, {name}!</h1>
            <p>Thank you for joining us! We're excited to have you on board.</p>
            <p>To help you get started, check out our getting started guide:</p>
            <p>
                <a href="{docs_url}" class="cta-button">View Documentation</a>
            </p>
            <p>Have questions or want to connect with other users? Join our community:</p>
            <p>
                <a href="{community_url}" class="cta-button">Join Our Community</a>
            </p>
            <p>Ready to begin? Head to your dashboard:</p>
            <p>
                <a href="{dashboard_url}" class="cta-button">Go to Dashboard</a>
            </p>
            <p>We're looking forward to helping you achieve your goals!</p>
            <p>Best regards,<br>The {app_name} Team</p>
        </div>
    </body>
    </html>
    """

    # Plain text version of the email
    text_content = """
    Welcome to {app_name}, {name}!

    Thank you for joining us! We're excited to have you on board.

    To help you get started, check out our getting started guide:
    {docs_url}

    Have questions or want to connect with other users? Join our community:
    {community_url}

    Ready to begin? Head to your dashboard:
    {dashboard_url}

    We're looking forward to helping you achieve your goals!

    Best regards,
    The {app_name} Team
    """

    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_SENDER
    msg["To"] = email

    # Attach both plain text and HTML versions
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        async with aiosmtplib.SMTP(
            hostname="smtp.gmail.com", port=465, use_tls=True
        ) as smtp:
            await smtp.login(config.EMAIL_LOGIN, config.EMAIL_PASSWORD)
            msg["From"] = config.EMAIL_SENDER
            await smtp.send_message(msg)
        logger.info(f"Welcome email sent successfully to {email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
