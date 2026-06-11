from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.catalog.models import Product
from apps.catalog.tasks import sync_product_to_mongo, delete_product_from_mongo


@receiver(post_save, sender=Product)
def auto_sync_mongo_save(sender, instance, created, update_fields=None, **kwargs):
    """Déclenche l'ajout ou la mise à jour dans MongoDB à la sauvegarde."""
    if not instance.is_active:
        delete_product_from_mongo.delay(instance.id)
        print(f"👻 [SIGNAL] Produit {instance.sku} inactif. Demande de retrait MongoDB.")
    else:
        if created or update_fields is None:
            sync_product_to_mongo.delay(instance.id)
            print(f"🔄 [SIGNAL] Synchro/Upsert MongoDB déclenchée pour SKU: {instance.sku}")


@receiver(post_delete, sender=Product)
def auto_sync_mongo_delete(sender, instance, **kwargs):
    """Supprime automatiquement le produit de MongoDB lorsque supprimé de Postgres."""
    delete_product_from_mongo.delay(instance.id)
    print(f"🗑️ [SIGNAL] Produit {instance.sku} supprimé de Postgres. Nettoyage MongoDB lancé.")
