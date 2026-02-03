"""hooks app serializers - auto-generated."""
from observatory.api_utils import create_model_serializer
from django.apps import apps

app_config = apps.get_app_config('hooks')
for model in app_config.get_models():
    serializer_class = create_model_serializer(model)
    globals()[f'{model.__name__}Serializer'] = serializer_class
