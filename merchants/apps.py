from django.apps import AppConfig


class MerchantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'merchants'
    verbose_name = 'Merchants & Franchise'

    def ready(self):
        import merchants.signals  # noqa: F401
