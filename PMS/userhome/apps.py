from django.apps import AppConfig


class UserhomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userhome'
    def ready(self):
        import userhome.signals
