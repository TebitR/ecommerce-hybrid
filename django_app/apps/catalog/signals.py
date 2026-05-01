import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Product
from .tasks import sync_product_to_mongo

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Product)
def on_product_saved(sender, instance, created, **kwargs):
    """
    Déclenche la synchro MongoDB quand un produit est créé ou modifié.
    Utilise .delay() pour exécuter la tâche de façon asynchrone.
    """
    if instance.is_active:  # Ne sync que les produits actifs
        logger.info("Signal post_save pour Product#%s (sku=%s)", instance.id, instance.sku)
        sync_product_to_mongo.delay(instance.id)
    else:
        logger.info("Produit #%s désactivé → suppression MongoDB planifiée", instance.id)
        # Optionnel : supprimer de MongoDB quand désactivé
        # delete_product_from_mongo.delay(instance.id)


@receiver(post_delete, sender=Product)
def on_product_deleted(sender, instance, **kwargs):
    """
    Supprime le produit de MongoDB quand il est supprimé de PostgreSQL.
    """
    from .tasks import delete_product_from_mongo

    logger.info("Signal post_delete pour Product#%s (sku=%s)", instance.id, instance.sku)
    delete_product_from_mongo.delay(instance.id)
