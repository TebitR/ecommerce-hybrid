from django.core.management.base import BaseCommand

from apps.catalog.models import Product
from apps.catalog.tasks import sync_product_to_mongo


class Command(BaseCommand):
    help = "Resynchronise tous les produits PostgreSQL vers MongoDB (images incluses)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--async",
            action="store_true",
            help="Envoie les tâches via Celery (.delay) au lieu d'une exécution synchrone.",
        )

    def handle(self, *args, **options):
        products = Product.objects.order_by("id")
        total = products.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("Aucun produit à synchroniser."))
            return

        use_async = options["async"]
        mode = "Celery" if use_async else "synchrone"

        self.stdout.write(f"Synchronisation {mode} de {total} produit(s) vers MongoDB…")

        for product in products:
            if use_async:
                sync_product_to_mongo.delay(product.id)
                self.stdout.write(f"  → {product.sku} : tâche Celery enfilée")
            else:
                result = sync_product_to_mongo(product.id)
                self.stdout.write(f"  → {product.sku} : {result.get('status', 'ok')}")

        self.stdout.write(self.style.SUCCESS(f"Terminé — {total} produit(s) traité(s)."))
