from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from apps.orders.models import Order


@shared_task(bind=True, max_retries=3)
def send_order_confirmation(self, order_id):
    """Envoie un email HTML de confirmation accompagné de sa facture PDF de manière asynchrone."""
    try:
        # Récupération optimisée de la commande avec son utilisateur et ses produits
        order = Order.objects.select_related("user").prefetch_related("items__product").get(id=order_id)

        # 1. Génération de la facture PDF en mémoire (Buffer)
        html_invoice = render_to_string("orders/invoice.html", {"order": order})
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_invoice, dest=pdf_buffer)

        if pisa_status.err:
            print(f"⚠️ [PDF] Erreur de rendu pour la commande {order.order_number}. Envoi de l'email sans PDF.")
            pdf_buffer = None

        # 2. Préparation de l'email au format HTML
        subject = f"Confirmation de votre commande {order.order_number}"
        body_html = render_to_string("orders/confirmation_email.html", {"order": order})

        recipient_email = order.user.email if order.user.email else settings.DEFAULT_FROM_EMAIL

        email = EmailMessage(
            subject=subject,
            body=body_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.content_subtype = "html"  # Définit explicitement le format HTML

        # 3. Attachement de la facture PDF si la génération est réussie
        if pdf_buffer:
            pdf_buffer.seek(0)
            email.attach(f"Facture_{order.order_number}.pdf", pdf_buffer.read(), "application/pdf")

        # 4. Envoi de l'email
        email.send()
        print(f"✅ [EMAIL] Facture PDF envoyée avec succès pour {order.order_number} à {recipient_email}")
        return {"status": "success", "order_number": order.order_number}

    except Order.DoesNotExist:
        print(f"❌ [EMAIL] Commande ID {order_id} introuvable dans Postgres.")
    except Exception as e:
        print(f"❌ [EMAIL] Échec de la tâche pour la commande {order_id}: {e}")
        raise self.retry(exc=e, countdown=15)
