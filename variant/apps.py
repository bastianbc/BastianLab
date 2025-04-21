from django.apps import AppConfig

class VariantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'variant'

    def ready(self):
        import variant.signals  # Initials the signals
