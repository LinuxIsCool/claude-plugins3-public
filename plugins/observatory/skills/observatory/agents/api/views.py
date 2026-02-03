"""agents app ViewSets - auto-generated."""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.apps import apps
from observatory.api_utils import create_model_serializer, create_model_viewset

app_config = apps.get_app_config('agents')
for model in app_config.get_models():
    serializer_class = create_model_serializer(model)
    viewset_class = create_model_viewset(model, serializer_class)
    globals()[f'{model.__name__}ViewSet'] = viewset_class
