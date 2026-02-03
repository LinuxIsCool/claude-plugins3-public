from django.apps import AppConfig

class SettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings'
    verbose_name = 'Settings'
    label = 'claude_settings'  # Avoid conflict with Django's settings module
