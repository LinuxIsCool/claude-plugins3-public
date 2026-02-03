"""Plugins app - Plugin registry."""
from django.db import models


class Plugin(models.Model):
    """Installed Claude Code plugins."""
    marketplace = models.CharField(max_length=100, db_index=True, help_text="Plugin marketplace/source")
    name = models.CharField(max_length=100, db_index=True)
    version = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=100, blank=True)
    repository_url = models.URLField(blank=True)
    install_path = models.TextField(help_text="Local installation path")
    cache_path = models.TextField(help_text="Cached plugin path")
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['marketplace', 'name', 'version']
        ordering = ['marketplace', 'name']
        indexes = [
            models.Index(fields=['enabled']),
            models.Index(fields=['-installed_at']),
        ]

    def __str__(self):
        return f"{self.name}@{self.marketplace} v{self.version}"


class PluginDependency(models.Model):
    """Plugin dependencies."""
    DEPENDENCY_TYPE_CHOICES = [
        ('plugin', 'Plugin'),
        ('system', 'System'),
        ('npm', 'NPM'),
        ('pip', 'Pip'),
    ]

    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='dependencies')
    dependency_name = models.CharField(max_length=100)
    dependency_version = models.CharField(max_length=50, blank=True)
    dependency_type = models.CharField(max_length=20, choices=DEPENDENCY_TYPE_CHOICES, default='plugin')
    required = models.BooleanField(default=True)

    class Meta:
        unique_together = ['plugin', 'dependency_name', 'dependency_type']

    def __str__(self):
        return f"{self.plugin.name} -> {self.dependency_name}"
