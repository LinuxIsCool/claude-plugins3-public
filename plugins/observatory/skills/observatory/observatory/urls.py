"""
URL configuration for Claude Code Observatory.

API endpoints are under /api/
Admin is under /admin/
API documentation is under /api/docs/
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints - Claude Code domain apps
    path('api/sessions/', include('sessions.api.urls')),
    path('api/plugins/', include('plugins.api.urls')),
    path('api/skills/', include('skills.api.urls')),
    path('api/commands/', include('commands.api.urls')),
    path('api/agents/', include('agents.api.urls')),
    path('api/hooks/', include('hooks.api.urls')),
    path('api/settings/', include('settings.api.urls')),
    path('api/output-styles/', include('output_styles.api.urls')),
    path('api/mcps/', include('mcps.api.urls')),

    # Knowledge graph
    path('api/knowledge/', include('knowledge.api.urls')),

    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]
