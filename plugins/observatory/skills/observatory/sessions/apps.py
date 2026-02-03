from django.apps import AppConfig

class SessionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sessions'
    label = 'claude_sessions'  # Unique label to avoid conflict with django.contrib.sessions
    verbose_name = 'Sessions & Messages'
