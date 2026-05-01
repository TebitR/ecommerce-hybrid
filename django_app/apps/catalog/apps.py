from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    verbose_name = "Catalogue Produits"

    def ready(self):
        # Importer les signals pour les enregistrer
        import apps.catalog.signals  # noqa: F401
