"""
Django Admin configuration for Knowledge Graph models.

Uses the same dynamic ModelAdmin pattern as claude_code app.
"""
from django.contrib import admin
from django.apps import apps
from django.db import models


def create_model_admin(model):
    """Factory to create ModelAdmin with sensible defaults."""
    meta = model._meta
    all_fields = [f for f in meta.get_fields() if f.concrete and not f.many_to_many]

    # list_display: First 6 simple fields
    display_fields = []
    for f in all_fields:
        if len(display_fields) >= 6:
            break
        if isinstance(f, (models.CharField, models.TextField, models.IntegerField,
                         models.FloatField, models.BooleanField, models.DateTimeField,
                         models.DateField, models.AutoField, models.BigAutoField, models.URLField)):
            display_fields.append(f.name)

    # search_fields: All text fields
    search = [f.name for f in all_fields
              if isinstance(f, (models.CharField, models.TextField, models.URLField))
              and not f.primary_key]

    # list_filter: Boolean, DateTime, and choice fields
    filters = []
    for f in all_fields:
        if isinstance(f, models.BooleanField):
            filters.append(f.name)
        elif isinstance(f, (models.DateTimeField, models.DateField)):
            filters.append(f.name)
        elif hasattr(f, 'choices') and f.choices:
            filters.append(f.name)

    # date_hierarchy: First DateTimeField
    date_field = None
    for f in all_fields:
        if isinstance(f, (models.DateTimeField, models.DateField)) and not f.primary_key:
            date_field = f.name
            break

    # ordering
    ordering = None
    for field_name in ['created_at', 'discovered_at', 'updated_at']:
        if any(f.name == field_name for f in all_fields):
            ordering = [f'-{field_name}']
            break

    attrs = {
        'list_display': display_fields or ['__str__'],
        'search_fields': search[:5] if search else [],
        'list_filter': filters[:5] if filters else [],
        'ordering': ordering,
        'list_per_page': 50,
        'show_full_result_count': False,
    }

    if date_field:
        attrs['date_hierarchy'] = date_field

    return type(f'{model.__name__}Admin', (admin.ModelAdmin,), attrs)


# Auto-register all models in the knowledge app
app_config = apps.get_app_config('knowledge')
for model in app_config.get_models():
    try:
        admin_class = create_model_admin(model)
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass
