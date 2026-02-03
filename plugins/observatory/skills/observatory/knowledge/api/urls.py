"""
URL routing for Knowledge Graph API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'resources', views.ResourceViewSet, basename='resource')
router.register(r'edges', views.EdgeViewSet, basename='edge')
router.register(r'content', views.ContentViewSet, basename='content')
router.register(r'embeddings', views.EmbeddingViewSet, basename='embedding')

urlpatterns = [
    path('', include(router.urls)),
]
