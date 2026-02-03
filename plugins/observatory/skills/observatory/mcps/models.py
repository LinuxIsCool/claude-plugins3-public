"""MCPs app - MCP (Model Context Protocol) server configurations."""
from django.db import models


class McpServer(models.Model):
    """MCP (Model Context Protocol) server configurations."""
    profile = models.ForeignKey(
        'claude_settings.SettingsProfile', on_delete=models.CASCADE,
        related_name='mcp_servers'
    )
    server_name = models.CharField(max_length=100, db_index=True)
    command = models.TextField(help_text="Command to start the server")
    args_json = models.JSONField(default=list, blank=True)
    env_json = models.JSONField(default=dict, blank=True)
    is_enabled = models.BooleanField(default=True, db_index=True)
    auto_start = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata_json = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['profile', 'server_name']
        verbose_name = 'MCP Server'
        verbose_name_plural = 'MCP Servers'

    def __str__(self):
        return f"{self.server_name} ({self.profile})"
