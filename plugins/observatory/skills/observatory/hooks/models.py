"""Hooks app - Hook definitions and execution tracking."""
from django.db import models
from django.utils import timezone


class HookDefinition(models.Model):
    """Registered hook definitions."""
    EVENT_TYPE_CHOICES = [
        ('PreToolUse', 'Pre Tool Use'),
        ('PostToolUse', 'Post Tool Use'),
        ('PostToolUseFailure', 'Post Tool Use Failure'),  # NEW
        ('PermissionRequest', 'Permission Request'),       # NEW
        ('Stop', 'Stop'),
        ('SubagentStart', 'Subagent Start'),              # NEW
        ('SubagentStop', 'Subagent Stop'),
        ('Setup', 'Setup'),                                # NEW
        ('SessionStart', 'Session Start'),
        ('SessionEnd', 'Session End'),
        ('UserPromptSubmit', 'User Prompt Submit'),
        ('PreCompact', 'Pre Compact'),
        ('Notification', 'Notification'),
        ('ToolError', 'Tool Error'),
        ('ToolSuccess', 'Tool Success'),
        ('ModelResponse', 'Model Response'),
        ('Shutdown', 'Shutdown'),
    ]

    HOOK_TYPE_CHOICES = [
        ('command', 'Command'),
        ('prompt', 'Prompt'),
    ]

    SOURCE_CHOICES = [
        ('user', 'User (~/.claude/)'),
        ('project', 'Project (.claude/)'),
        ('local', 'Local (.claude/*.local.*)'),
        ('plugin', 'Plugin'),
        ('skill', 'Skill'),
        ('agent', 'Agent'),
        ('policy', 'Policy (Managed)'),
    ]

    plugin = models.ForeignKey(
        'plugins.Plugin', on_delete=models.CASCADE, null=True, blank=True,
        related_name='hook_definitions',
        help_text="Plugin that provides this hook (null for system hooks)"
    )
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES, db_index=True)
    script_path = models.TextField(blank=True, help_text="Path to hook script (for command type)")
    timeout_ms = models.IntegerField(default=5000)
    enabled = models.BooleanField(default=True, db_index=True)
    priority = models.IntegerField(default=100, help_text="Lower = higher priority")

    # New fields for hook type and matching
    hook_type = models.CharField(
        max_length=20,
        choices=HOOK_TYPE_CHOICES,
        default='command',
        help_text="'command' runs a script, 'prompt' injects text"
    )
    matcher = models.CharField(
        max_length=200,
        blank=True,
        help_text="Tool pattern matcher (regex) for tool-specific hooks"
    )
    prompt_text = models.TextField(
        blank=True,
        help_text="Prompt content for prompt-type hooks"
    )
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        blank=True,
        help_text="Origin of this hook definition"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['priority', 'event_type']
        indexes = [
            models.Index(fields=['event_type', 'enabled']),
            models.Index(fields=['priority']),
            models.Index(fields=['hook_type']),
        ]

    def __str__(self):
        plugin_name = self.plugin.name if self.plugin else 'system'
        return f"{self.event_type} ({plugin_name})"


class HookEvent(models.Model):
    """Hook execution log."""
    hook_definition = models.ForeignKey(
        HookDefinition, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='executions'
    )
    session = models.ForeignKey(
        'claude_sessions.Session', on_delete=models.CASCADE, null=True, blank=True,
        related_name='hook_events'
    )
    event_type = models.CharField(max_length=30, db_index=True)
    triggered_at = models.DateTimeField(default=timezone.now, db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(db_index=True)
    input_json = models.JSONField(null=True, blank=True)
    output_json = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    timeout_occurred = models.BooleanField(default=False)
    plugin_id = models.CharField(max_length=100, blank=True, help_text="Plugin identifier string")

    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['event_type', '-triggered_at']),
            models.Index(fields=['success', '-triggered_at']),
        ]

    def __str__(self):
        status = "OK" if self.success else "FAIL"
        return f"{self.event_type} [{status}] @ {self.triggered_at}"


# ============================================================================
# Event-specific hook detail tables (OneToOne pattern with primary_key=True)
# ============================================================================

class HookEventPreToolUse(models.Model):
    """PreToolUse event details."""
    DECISION_CHOICES = [('allow', 'Allow'), ('block', 'Block'), ('modify', 'Modify')]

    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='pretooluse_detail')
    tool_name = models.CharField(max_length=100, db_index=True)
    tool_input = models.TextField(blank=True)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES, default='allow', db_index=True)
    modified_input = models.TextField(blank=True)
    block_reason = models.TextField(blank=True)

    def __str__(self):
        return f"PreToolUse: {self.tool_name} -> {self.decision}"


class HookEventPostToolUse(models.Model):
    """PostToolUse event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='posttooluse_detail')
    tool_name = models.CharField(max_length=100, db_index=True)
    tool_input = models.TextField(blank=True)
    tool_output = models.TextField(blank=True)
    tool_success = models.BooleanField(null=True, blank=True)
    injected_context = models.TextField(blank=True)
    injected_at_position = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"PostToolUse: {self.tool_name}"


class HookEventPostToolUseFailure(models.Model):
    """PostToolUseFailure event details - NEW."""
    hook_event = models.OneToOneField(
        HookEvent, on_delete=models.CASCADE, primary_key=True,
        related_name='posttoolusefailure_detail'
    )
    tool_name = models.CharField(max_length=100, db_index=True)
    tool_input = models.TextField(blank=True)
    tool_use_id = models.CharField(max_length=64, blank=True)
    error_type = models.CharField(max_length=100, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    stderr = models.TextField(blank=True)

    class Meta:
        verbose_name = "Hook Event: Post Tool Use Failure"
        verbose_name_plural = "Hook Events: Post Tool Use Failures"

    def __str__(self):
        return f"PostToolUseFailure: {self.tool_name} - {self.error_type}"


class HookEventPermissionRequest(models.Model):
    """PermissionRequest event details - NEW."""
    DECISION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('pending', 'Pending'),
    ]

    hook_event = models.OneToOneField(
        HookEvent, on_delete=models.CASCADE, primary_key=True,
        related_name='permissionrequest_detail'
    )
    tool_name = models.CharField(max_length=100, db_index=True)
    tool_input = models.TextField(blank=True)
    tool_use_id = models.CharField(max_length=64, blank=True)
    permission_mode = models.CharField(max_length=30, blank=True)
    decision = models.CharField(
        max_length=10,
        choices=DECISION_CHOICES,
        default='pending',
        db_index=True
    )
    decision_source = models.CharField(max_length=30, blank=True)
    updated_input = models.TextField(blank=True)
    denial_message = models.TextField(blank=True)

    class Meta:
        verbose_name = "Hook Event: Permission Request"
        verbose_name_plural = "Hook Events: Permission Requests"

    def __str__(self):
        return f"PermissionRequest: {self.tool_name} -> {self.decision}"


class HookEventSubagentStart(models.Model):
    """SubagentStart event details - NEW."""
    hook_event = models.OneToOneField(
        HookEvent, on_delete=models.CASCADE, primary_key=True,
        related_name='subagentstart_detail'
    )
    agent_id = models.CharField(max_length=64, db_index=True)
    agent_type = models.CharField(max_length=50, db_index=True)
    parent_session_id = models.CharField(max_length=64, blank=True)
    task_description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Hook Event: Subagent Start"
        verbose_name_plural = "Hook Events: Subagent Starts"

    def __str__(self):
        return f"SubagentStart: {self.agent_type} ({self.agent_id})"


class HookEventSetup(models.Model):
    """Setup event details (--init, --init-only, --maintenance) - NEW."""
    TRIGGER_CHOICES = [
        ('init', 'Init'),
        ('init_only', 'Init Only'),
        ('maintenance', 'Maintenance'),
    ]

    hook_event = models.OneToOneField(
        HookEvent, on_delete=models.CASCADE, primary_key=True,
        related_name='setup_detail'
    )
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, db_index=True)
    working_directory = models.TextField(blank=True)
    additional_context = models.TextField(blank=True)
    env_vars_set = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Hook Event: Setup"
        verbose_name_plural = "Hook Events: Setup"

    def __str__(self):
        return f"Setup: {self.trigger}"


class HookEventStop(models.Model):
    """Stop event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='stop_detail')
    stop_reason = models.CharField(max_length=50, blank=True, db_index=True)
    message_count = models.IntegerField(null=True, blank=True)
    finish_reason = models.CharField(max_length=50, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Stop: {self.stop_reason}"


class HookEventSubagentStop(models.Model):
    """SubagentStop event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='subagentstop_detail')
    subagent_id = models.CharField(max_length=64, blank=True, db_index=True)
    subagent_type = models.CharField(max_length=50, blank=True)
    parent_session_id = models.CharField(max_length=64, blank=True)
    exit_status = models.CharField(max_length=20, blank=True, db_index=True)
    result_summary = models.TextField(blank=True)

    def __str__(self):
        return f"SubagentStop: {self.subagent_type} ({self.exit_status})"


class HookEventSessionStart(models.Model):
    """SessionStart event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='sessionstart_detail')
    working_directory = models.TextField(blank=True)
    user_id = models.CharField(max_length=100, blank=True, db_index=True)
    client_version = models.CharField(max_length=50, blank=True)
    model_id = models.CharField(max_length=100, blank=True, db_index=True)
    session_config = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"SessionStart: {self.model_id}"


class HookEventSessionEnd(models.Model):
    """SessionEnd event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='sessionend_detail')
    duration_seconds = models.IntegerField(null=True, blank=True)
    total_turns = models.IntegerField(null=True, blank=True)
    total_input_tokens = models.IntegerField(null=True, blank=True)
    total_output_tokens = models.IntegerField(null=True, blank=True)
    tools_used_count = models.IntegerField(null=True, blank=True)
    end_reason = models.CharField(max_length=50, blank=True, db_index=True)

    def __str__(self):
        return f"SessionEnd: {self.end_reason} ({self.duration_seconds}s)"


class HookEventUserPromptSubmit(models.Model):
    """UserPromptSubmit event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='userpromptsubmit_detail')
    prompt_text = models.TextField(blank=True)
    prompt_length = models.IntegerField(null=True, blank=True, db_index=True)
    attachments_count = models.IntegerField(default=0)
    is_continuation = models.BooleanField(default=False)
    context_size_tokens = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"UserPromptSubmit: {self.prompt_length} chars"


class HookEventPreCompact(models.Model):
    """PreCompact event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='precompact_detail')
    current_tokens = models.IntegerField(null=True, blank=True, db_index=True)
    max_tokens = models.IntegerField(null=True, blank=True)
    compaction_strategy = models.CharField(max_length=50, blank=True)
    messages_before = models.IntegerField(null=True, blank=True)
    messages_to_remove = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"PreCompact: {self.current_tokens}/{self.max_tokens} tokens"


class HookEventNotification(models.Model):
    """Notification event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='notification_detail')
    notification_type = models.CharField(max_length=50, blank=True, db_index=True)
    notification_title = models.CharField(max_length=200, blank=True)
    notification_message = models.TextField(blank=True)
    source = models.CharField(max_length=100, blank=True)
    action_required = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"Notification: {self.notification_type}"


class HookEventToolError(models.Model):
    """ToolError event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='toolerror_detail')
    tool_name = models.CharField(max_length=100, db_index=True)
    tool_input = models.TextField(blank=True)
    error_type = models.CharField(max_length=100, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    retry_attempted = models.BooleanField(default=False)

    def __str__(self):
        return f"ToolError: {self.tool_name} - {self.error_type}"


class HookEventToolSuccess(models.Model):
    """ToolSuccess event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='toolsuccess_detail')
    tool_name = models.CharField(max_length=100, db_index=True)
    tool_input = models.TextField(blank=True)
    tool_output = models.TextField(blank=True)
    execution_time_ms = models.IntegerField(null=True, blank=True, db_index=True)
    output_size_bytes = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"ToolSuccess: {self.tool_name} ({self.execution_time_ms}ms)"


class HookEventModelResponse(models.Model):
    """ModelResponse event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='modelresponse_detail')
    model_id = models.CharField(max_length=100, blank=True, db_index=True)
    input_tokens = models.IntegerField(null=True, blank=True)
    output_tokens = models.IntegerField(null=True, blank=True)
    finish_reason = models.CharField(max_length=50, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True, db_index=True)
    cache_hit = models.BooleanField(default=False)
    tool_calls_count = models.IntegerField(default=0)

    def __str__(self):
        return f"ModelResponse: {self.model_id} ({self.latency_ms}ms)"


class HookEventShutdown(models.Model):
    """Shutdown event details."""
    hook_event = models.OneToOneField(HookEvent, on_delete=models.CASCADE, primary_key=True, related_name='shutdown_detail')
    shutdown_reason = models.CharField(max_length=100, blank=True, db_index=True)
    uptime_seconds = models.IntegerField(null=True, blank=True)
    active_sessions = models.IntegerField(null=True, blank=True)
    pending_tasks = models.IntegerField(null=True, blank=True)
    cleanup_status = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Shutdown: {self.shutdown_reason}"
