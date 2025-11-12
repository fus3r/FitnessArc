from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Enregistre les signaux au démarrage de l’app
        from . import signals  # noqa: F401

