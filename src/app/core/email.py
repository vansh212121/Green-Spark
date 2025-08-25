import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.app.core.config import settings

logger = logging.getLogger(__name__)


def _send_email_sync(email_to: str, subject: str, html_content: str):
    """
    A robust, synchronous function to send an email using Python's smtplib.
    This is designed to be called from a synchronous environment like a Celery worker.
    """
    msg = MIMEMultipart()
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(html_content, "html"))

    try:
        # Connect to the SMTP server with a timeout to prevent hanging.
        with smtplib.SMTP(
            settings.MAIL_SERVER, settings.MAIL_PORT, timeout=15
        ) as server:
            server.starttls()  # Upgrade the connection to a secure one
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {e}", exc_info=True)
        # Re-raising the exception is important so Celery knows the task failed.
        raise


def send_password_reset_email_sync(email_to: str, token: str):
    """Builds and sends the password reset email synchronously."""

    # Use the configurable frontend URL
    reset_url = f"http://localhost:8000/reset-password?token={token}"

    subject = "Reset Your GreenSpark Password"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; max-width: 600px; margin: auto; padding: 40px; }}
            .header {{ font-size: 24px; font-weight: 600; color: #212529; text-align: center; margin-bottom: 20px; }}
            .text {{ color: #495057; line-height: 1.6; }}
            .button-container {{ text-align: center; margin: 30px 0; }}
            .button {{ background-color: #28a745; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 500; display: inline-block; }}
            .footer {{ font-size: 12px; color: #6c757d; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Password Reset Request</div>
            <p class="text">We received a request to reset the password for your GreenSpark account. Please click the button below to set a new password.</p>
            <div class="button-container">
                <a href="{reset_url}" class="button" style="color: #ffffff;">Reset My Password</a>
            </div>
            <p class="text">This password reset link will expire in 1 hour.</p>
            <p class="text">If you did not request a password reset, you can safely ignore this email. Your password will not be changed.</p>
            <div class="footer">
                You received this email because a password reset was requested for your account.<br>
                GreenSpark, 123 Power Lane, Delhi, India
            </div>
        </div>
    </body>
    </html>
    """
    _send_email_sync(email_to, subject, html_content)


def send_verification_email_sync(email_to: str, token: str):
    """Builds and sends the verification email synchronously."""

    # Use the configurable frontend URL
    verification_url = f"http://localhost:3000/verify-email?token={token}"

    subject = "Verify Your Email for GreenSpark"

    # Using modern, clean HTML with inline CSS for email client compatibility
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; max-width: 600px; margin: auto; padding: 40px; }}
            .header {{ font-size: 24px; font-weight: 600; color: #212529; text-align: center; margin-bottom: 20px; }}
            .text {{ color: #495057; line-height: 1.6; }}
            .button-container {{ text-align: center; margin: 30px 0; }}
            .button {{ background-color: #28a745; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 500; display: inline-block; }}
            .footer {{ font-size: 12px; color: #6c757d; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">One Last Step to Activate Your Account</div>
            <p class="text">Welcome to GreenSpark! We're excited to help you gain clarity and control over your energy usage. Please click the button below to verify your email address.</p>
            <div class="button-container">
                <a href="{verification_url}" class="button" style="color: #ffffff;">Verify My Account</a>
            </div>
            <p class="text">This verification link will expire in 24 hours.</p>
            <p class="text">If you did not sign up for a GreenSpark account, you can safely ignore this email.</p>
            <div class="footer">
                You received this email because you signed up for GreenSpark.<br>
                GreenSpark, 123 Power Lane, Delhi, India
            </div>
        </div>
    </body>
    </html>
    """
    _send_email_sync(email_to, subject, html_content)


def send_welcome_email_sync(email_to: str, first_name: str):
    """Builds and sends the welcome email synchronously."""

    subject = f"Welcome to GreenSpark, {first_name}!"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; max-width: 600px; margin: auto; padding: 40px; }}
            .header {{ font-size: 24px; font-weight: 600; color: #212529; text-align: center; margin-bottom: 20px; }}
            .text {{ color: #495057; line-height: 1.6; }}
            .button-container {{ text-align: center; margin: 30px 0; }}
            .button {{ background-color: #28a745; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 500; display: inline-block; }}
            .footer {{ font-size: 12px; color: #6c757d; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Welcome to a Smarter Way to Use Energy, {first_name}!</div>
            <p class="text">Your GreenSpark account is active and ready to go. You're on your way to understanding your electricity consumption like never before.</p>
            <p class="text">The next step is to upload your first electricity bill to start seeing your personalized insights.</p>
            <div class="button-container">
                <a href="{settings.FRONTEND_URL}/dashboard" class="button" style="color: #ffffff;">Upload Your First Bill</a>
            </div>
            <p class="text">We're thrilled to have you on board!</p>
            <p class="text">- The GreenSpark Team</p>
        </div>
    </body>
    </html>
    """
    _send_email_sync(email_to, subject, html_content)


def send_email_change_confirmation_sync(email_to: str, token: str):
    """Builds and sends the email change confirmation email synchronously."""

    # Use the configurable frontend URL
    confirmation_url = f"http://localhost:3000/confirm-email-change?token={token}"

    subject = "Confirm Your New Email Address for GreenSpark"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
            .container {{ background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; max-width: 600px; margin: auto; padding: 40px; }}
            .header {{ font-size: 24px; font-weight: 600; color: #212529; text-align: center; margin-bottom: 20px; }}
            .text {{ color: #495057; line-height: 1.6; }}
            .button-container {{ text-align: center; margin: 30px 0; }}
            .button {{ background-color: #28a745; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 500; display: inline-block; }}
            .footer {{ font-size: 12px; color: #6c757d; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">Confirm Your New Email Address</div>
            <p class="text">You requested to change the email address for your GreenSpark account. To complete the process, please click the button below to confirm this is your new email.</p>
            <div class="button-container">
                <a href="{confirmation_url}" class="button" style="color: #ffffff;">Confirm New Email</a>
            </div>
            <p class="text">This confirmation link will expire in 1 hour.</p>
            <p class="text">If you did not request this change, you can safely ignore this email.</p>
            <div class="footer">
                You received this email because an email change was requested for your account.<br>
                GreenSpark, 123 Power Lane, Delhi, India
            </div>
        </div>
    </body>
    </html>
    """
    _send_email_sync(email_to, subject, html_content)
