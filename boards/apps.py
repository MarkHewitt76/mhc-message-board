"""
boards app configuration
"""
from django.apps import AppConfig


class BoardsConfig(AppConfig):
    """
    Standard config for auto incrementing.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'boards'

    def ready(self):
        """
        Imports signals module (for automatic creation of
        user profiles) when boards app configured.
        """
        import boards.signals
