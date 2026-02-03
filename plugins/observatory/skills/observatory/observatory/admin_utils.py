"""Shared admin utilities for dynamic ModelAdmin generation."""
from django.contrib import admin


def create_model_admin(model):
    """Factory to create ModelAdmin with sensible defaults based on field types."""
    meta = model._meta

    list_display_fields = ['__str__']
    search_fields_list = []
    list_filter_fields = []
    ordering_fields = []

    for field in meta.get_fields():
        if not field.concrete or field.many_to_many:
            continue

        field_type = field.get_internal_type()
        field_name = field.name

        # Skip primary key in display if it's long (like UUIDs)
        if field.primary_key and field_type == 'CharField':
            continue

        # Add to list_display (limit to 6 fields)
        if len(list_display_fields) < 7:
            if field_type in ('CharField', 'IntegerField', 'FloatField', 'BooleanField',
                            'DateTimeField', 'DateField'):
                list_display_fields.append(field_name)

        # Add to search_fields
        if field_type in ('CharField', 'TextField') and len(search_fields_list) < 4:
            search_fields_list.append(field_name)

        # Add to list_filter
        if field_type in ('BooleanField', 'CharField') and len(list_filter_fields) < 4:
            if field_type == 'BooleanField' or (hasattr(field, 'choices') and field.choices):
                list_filter_fields.append(field_name)

        # Add to ordering
        if field_type == 'DateTimeField' and 'created' in field_name.lower():
            ordering_fields.insert(0, f'-{field_name}')

    class DynamicModelAdmin(admin.ModelAdmin):
        list_display = list_display_fields[:7]
        search_fields = search_fields_list[:4]
        list_filter = list_filter_fields[:4]
        ordering = ordering_fields[:2] if ordering_fields else None
        list_per_page = 50

    DynamicModelAdmin.__name__ = f'{model.__name__}Admin'
    return DynamicModelAdmin


def register_app_models(app_name):
    """Register all models from an app with auto-generated admin classes."""
    from django.apps import apps

    try:
        app_config = apps.get_app_config(app_name)
    except LookupError:
        return

    for model in app_config.get_models():
        if not admin.site.is_registered(model):
            admin_class = create_model_admin(model)
            admin.site.register(model, admin_class)
