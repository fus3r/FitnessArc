"""
Custom email backend using Brevo (Sendinblue) API
"""
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
except ImportError:
    sib_api_v3_sdk = None
    ApiException = None


class BrevoEmailBackend(BaseEmailBackend):
    """
    Email backend using Brevo (Sendinblue) API
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("BREVO_API_KEY is not configured in settings")
            logger.error("BREVO_API_KEY is not configured")
        
        if sib_api_v3_sdk:
            # Configure API key
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = self.api_key
            self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )
        else:
            self.api_instance = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not sib_api_v3_sdk:
            if not self.fail_silently:
                raise ImportError("sib-api-v3-sdk package is not installed. Install with: pip install sib-api-v3-sdk")
            logger.error("sib-api-v3-sdk package is not installed")
            return 0

        if not self.api_key or not self.api_instance:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception as e:
                logger.exception(f"Failed to send email via Brevo: {e}")
                if not self.fail_silently:
                    raise
        
        return num_sent

    def _send(self, message):
        """
        Send a single email message using Brevo API
        """
        if not message.recipients():
            return False

        from_email = message.from_email or settings.DEFAULT_FROM_EMAIL
        
        # Parse from email
        if '<' in from_email and '>' in from_email:
            # Format: "Name <email@example.com>"
            name = from_email.split('<')[0].strip().strip('"')
            email = from_email.split('<')[1].strip('>')
        else:
            name = None
            email = from_email

        # Build sender
        sender = {"email": email}
        if name:
            sender["name"] = name

        # Build recipients
        to = [{"email": recipient} for recipient in message.to]
        
        # Build email object
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            subject=message.subject,
        )

        # Add CC and BCC if present
        if message.cc:
            send_smtp_email.cc = [{"email": recipient} for recipient in message.cc]
        if message.bcc:
            send_smtp_email.bcc = [{"email": recipient} for recipient in message.bcc]

        # Handle HTML and text content
        html_content = None
        text_content = None
        
        if message.content_subtype == 'html':
            html_content = message.body
        else:
            text_content = message.body

        # Check for HTML alternative
        for alt_content, alt_mimetype in getattr(message, 'alternatives', []):
            if alt_mimetype == 'text/html':
                html_content = alt_content
                if not text_content:
                    text_content = message.body
                break

        if html_content:
            send_smtp_email.html_content = html_content
        if text_content:
            send_smtp_email.text_content = text_content

        # Send via Brevo
        try:
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Email sent successfully via Brevo. Message ID: {api_response.message_id}")
            return True
        except ApiException as e:
            logger.error(f"Brevo API error: {e}")
            if not self.fail_silently:
                raise
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if not self.fail_silently:
                raise
            return False
