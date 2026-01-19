from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


DEFAULT_EMAIL_CONTEXT = {
    "logo_url": "https://melanomalab.ucsf.edu/static/assets/images/bastianlablogo.png",
    "icon_url": "https://melanomalab.ucsf.edu/static/assets/images/icon-positive-vote-2.svg",
    "site_name": "Bastian Lab",
    "site_url": "https://melanomalab.ucsf.edu",
    "support_phone": "+31 6 3344 55 56",
    "support_email": "melanomalab@ucsf.edu",
    "support_url": "https://melanomalab.ucsf.edu",
}


def send_email(
    *,
    subject: str,
    template_name: str,
    recipients: list[str],
    context: dict,
    from_email: str | None = None,
    fail_silently: bool = False,
) -> bool:
    """
    Sends a branded HTML + plain-text email using a Django template.

    Base template:
        core/templates/basic_email_template.html
    """

    try:
        merged_context = {
            **DEFAULT_EMAIL_CONTEXT,
            **context,
        }

        html_message = render_to_string(template_name, merged_context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=fail_silently,
        )

        logger.info(
            "Email sent | subject=%s | recipients=%s | template=%s",
            subject,
            recipients,
            template_name,
        )

        return True

    except Exception as exc:
        logger.exception(
            "Email send failed | subject=%s | recipients=%s | template=%s | error=%s",
            subject,
            recipients,
            template_name,
            exc,
        )

        if not fail_silently:
            raise

        return False
