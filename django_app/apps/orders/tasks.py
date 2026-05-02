from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.orders.models import Order


@shared_task
def send_order_confirmation(order_id):
    """Envoie un email de confirmation HTML (sans PDF pour fiabilité immédiate)."""
    try:
        order = Order.objects.select_related("user").prefetch_related("items").get(id=order_id)

        subject = f"Confirmation commande {order.order_number}"
        body_html = render_to_string("orders/confirmation_email.html", {"order": order})

        to_addr = [order.user.email] if order.user.email else [settings.DEFAULT_FROM_EMAIL]

        email = EmailMessage(
            subject=subject,
            body=body_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_addr,
        )
        email.content_subtype = "html"
        email.send()
        print(f"✅ Email envoyé pour {order.order_number} à {order.user.email or settings.DEFAULT_FROM_EMAIL}")

    except Exception as e:
        print(f"❌ Échec email commande {order_id}: {e}")
