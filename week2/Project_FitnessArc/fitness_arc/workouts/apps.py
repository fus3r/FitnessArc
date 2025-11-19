from django.apps import AppConfig


class WorkoutsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workouts'

    def ready(self):
        """Import signals when Django starts"""
        import workouts.signals
