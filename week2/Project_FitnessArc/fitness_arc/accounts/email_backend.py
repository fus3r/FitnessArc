"""
Custom email backend using Resend API
"""
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import resend
except ImportError:
    resend = None


class ResendEmailBackend(BaseEmailBackend):
    """
    Email backend using Resend API
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'RESEND_API_KEY', None)
        
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("RESEND_API_KEY is not configured in settings")
            logger.error("RESEND_API_KEY is not configured")
        
        if resend:
            resend.api_key = self.api_key

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not resend:
            if not self.fail_silently:
                raise ImportError("resend package is not installed. Install with: pip install resend")
            logger.error("resend package is not installed")
            return 0

        if not self.api_key:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.exception(f"Failed to send email via Resend: {e}")
                if not self.fail_silently:
                    raise
        
        return num_sent

    def _send(self, message):
        """
        Send a single email message using Resend API
        """
        if not message.recipients():
            return False

        from_email = message.from_email or settings.DEFAULT_FROM_EMAIL
        
        # Build email parameters
        params = {
            "from": from_email,
            "to": message.to,
            "subject": message.subject,
        }

        # Add CC and BCC if present
        if message.cc:
            params["cc"] = message.cc
        if message.bcc:
            params["bcc"] = message.bcc

        # Handle HTML and text content
        if message.content_subtype == 'html':
            params["html"] = message.body
        else:
            params["text"] = message.body

        # Check for HTML alternative
        for alt_content, alt_mimetype in getattr(message, 'alternatives', []):
            if alt_mimetype == 'text/html':
                params["html"] = alt_content
                if message.content_subtype != 'html':
                    params["text"] = message.body
                break

        # Send via Resend
        try:
            response = resend.Emails.send(params)
            logger.info(f"Email sent successfully via Resend. ID: {response.get('id', 'N/A')}")
            return True
        except Exception as e:
            logger.error(f"Resend API error: {e}")
            if not self.fail_silently:
                raise
            return False
