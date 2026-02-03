"""Skills app - Skill definitions."""
from django.db import models


class Skill(models.Model):
    """Skills provided by plugins."""
    plugin = models.ForeignKey('plugins.Plugin', on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    file_path = models.TextField()
    allowed_tools = models.TextField(blank=True, help_text="Comma-separated tool list")
    content = models.TextField(help_text="Skill content/prompt")
    frontmatter = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['plugin', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.plugin.name}:{self.name}"
