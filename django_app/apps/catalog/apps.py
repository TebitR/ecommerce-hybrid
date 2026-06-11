from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalog'

    def ready(self):
        # Cette ligne est CRUCIALE pour connecter les signaux
        import apps.catalog.signals
