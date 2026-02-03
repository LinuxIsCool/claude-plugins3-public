"""Shared API utilities for dynamic serializer and viewset generation."""
from rest_framework import serializers, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend


def create_model_serializer(model):
    """Factory to create a ModelSerializer for any model."""
    class DynamicSerializer(serializers.ModelSerializer):
        class Meta:
            model_class = model
            fields = '__all__'

    # Workaround: Meta.model must be set after class creation for dynamic models
    DynamicSerializer.Meta.model = model
    DynamicSerializer.__name__ = f'{model.__name__}Serializer'
    return DynamicSerializer


def create_model_viewset(model, model_serializer_class):
    """Factory to create ModelViewSet with sensible defaults."""
    meta = model._meta

    # Determine filterable fields
    filter_fields_list = []
    search_fields_list = []
    ordering_fields_list = []

    for f in meta.get_fields():
        if not f.concrete or f.many_to_many:
            continue
        field_type = f.get_internal_type()
        if field_type in ('CharField', 'TextField', 'IntegerField', 'FloatField',
                          'BooleanField', 'DateTimeField', 'DateField'):
            filter_fields_list.append(f.name)
            ordering_fields_list.append(f.name)
        if field_type in ('CharField', 'TextField'):
            search_fields_list.append(f.name)

    class DynamicViewSet(viewsets.ModelViewSet):
        queryset = model.objects.all()
        serializer_class = model_serializer_class
        filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        filterset_fields = filter_fields_list[:15]
        search_fields = search_fields_list[:5]
        ordering_fields = ordering_fields_list

    DynamicViewSet.__name__ = f'{model.__name__}ViewSet'
    return DynamicViewSet


def generate_app_api(app_name, router):
    """Generate serializers and viewsets for all models in an app and register with router."""
    from django.apps import apps

    try:
        app_config = apps.get_app_config(app_name)
    except LookupError:
        return {}, {}

    serializers_dict = {}
    viewsets_dict = {}

    for model in app_config.get_models():
        # Create serializer
        serializer_class = create_model_serializer(model)
        serializers_dict[f'{model.__name__}Serializer'] = serializer_class

        # Create viewset
        viewset_class = create_model_viewset(model, serializer_class)
        viewsets_dict[f'{model.__name__}ViewSet'] = viewset_class

        # Register with router using model name as URL basename
        # Convert CamelCase to kebab-case
        import re
        url_name = re.sub(r'(?<!^)(?=[A-Z])', '-', model.__name__).lower()
        router.register(url_name, viewset_class, basename=url_name)

    return serializers_dict, viewsets_dict
