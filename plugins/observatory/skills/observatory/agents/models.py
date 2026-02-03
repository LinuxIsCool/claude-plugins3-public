"""Agents app - Agent definitions and subagent runtime tracking."""
from django.db import models


class Agent(models.Model):
    """Agents provided by plugins."""
    plugin = models.ForeignKey('plugins.Plugin', on_delete=models.CASCADE, related_name='agents')
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    file_path = models.TextField()
    tools = models.TextField(blank=True, help_text="Available tools")
    model = models.CharField(max_length=50, blank=True, db_index=True)
    prompt = models.TextField(help_text="Agent system prompt")
    frontmatter = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['plugin', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.plugin.name}:{self.name}"


class SubagentSession(models.Model):
    """Spawned subagent/task agent sessions."""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.CharField(max_length=64, primary_key=True, help_text="Subagent session ID")
    parent_session = models.ForeignKey('claude_sessions.Session', on_delete=models.CASCADE, related_name='subagents')
    parent_message_id = models.CharField(max_length=64, blank=True, db_index=True)
    subagent_type = models.CharField(max_length=50, db_index=True, help_text="e.g., Explore, code-architect")
    description = models.TextField(blank=True)
    prompt = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running', db_index=True)
    result_summary = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    transcript_file = models.TextField(blank=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['subagent_type', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]

    @property
    def duration_seconds(self):
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None

    def __str__(self):
        return f"{self.subagent_type} ({self.id[:8]}...)"


class SubagentHierarchy(models.Model):
    """Materialized path for nested subagent relationships."""
    subagent = models.OneToOneField(SubagentSession, on_delete=models.CASCADE, primary_key=True, related_name='hierarchy')
    root_session = models.ForeignKey('claude_sessions.Session', on_delete=models.CASCADE, related_name='subagent_hierarchy_roots')
    parent_session = models.ForeignKey('claude_sessions.Session', on_delete=models.CASCADE, related_name='direct_children')
    depth = models.IntegerField(default=0, db_index=True)
    path = models.TextField(help_text="Materialized path of session IDs")

    class Meta:
        indexes = [
            models.Index(fields=['root_session', 'depth']),
        ]

    def __str__(self):
        return f"Depth {self.depth}: {self.path[:50]}..."


class SubagentToolUse(models.Model):
    """Tools invoked by subagent sessions."""
    subagent = models.ForeignKey(SubagentSession, on_delete=models.CASCADE, related_name='tool_uses')
    tool_name = models.CharField(max_length=100, db_index=True)
    input_params = models.JSONField(null=True, blank=True)
    output_result = models.TextField(blank=True)
    success = models.BooleanField(default=True, db_index=True)
    error_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['tool_name', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.tool_name} by {self.subagent_id[:8]}..."


class SubagentResult(models.Model):
    """Structured capture of subagent return values."""
    RESULT_TYPE_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('partial', 'Partial'),
        ('timeout', 'Timeout'),
    ]

    subagent = models.OneToOneField(SubagentSession, on_delete=models.CASCADE, primary_key=True, related_name='result')
    result_type = models.CharField(max_length=20, choices=RESULT_TYPE_CHOICES, db_index=True)
    result_data = models.JSONField(null=True, blank=True)
    result_metadata = models.JSONField(null=True, blank=True)
    artifacts_generated = models.IntegerField(default=0)
    files_modified = models.IntegerField(default=0)
    lines_changed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.result_type} for {self.subagent_id[:8]}..."
