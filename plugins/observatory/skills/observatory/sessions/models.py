"""Sessions app - Core session and message tracking."""
import uuid as uuid_lib
from django.db import models


class Session(models.Model):
    """Core session tracking for Claude Code conversations."""
    id = models.CharField(max_length=64, primary_key=True, help_text="UUID session identifier")
    started_at = models.DateTimeField(help_text="Session start timestamp")
    ended_at = models.DateTimeField(null=True, blank=True, help_text="Session end timestamp")
    cwd = models.TextField(blank=True, help_text="Working directory")
    summary = models.TextField(blank=True, help_text="Session summary (auto-generated)")
    tags = models.JSONField(default=list, blank=True, help_text="Session tags")
    event_count = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)

    # NEW: Fields to match Claude Code session metadata
    slug = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Human-readable session name (e.g., 'calm-dreaming-backus')"
    )
    git_branch = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary git branch at session start"
    )
    version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Claude Code version"
    )
    user_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="User type: 'external', 'internal'"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['cwd']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        if self.slug:
            return f"{self.slug} ({self.started_at.date() if self.started_at else 'unknown'})"
        return f"{self.id[:8]}... ({self.started_at.date() if self.started_at else 'unknown'})"


class Event(models.Model):
    """Generic events within a session."""
    id = models.CharField(max_length=64, primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='events')
    type = models.CharField(max_length=50, db_index=True)
    ts = models.DateTimeField(help_text="Event timestamp")
    agent_session_num = models.IntegerField(default=0)
    data = models.JSONField(default=dict)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ['ts']
        indexes = [
            models.Index(fields=['session', 'ts']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.type} @ {self.ts}"


class Message(models.Model):
    """Transcript messages from Claude Code conversations."""
    TYPE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('progress', 'Progress'),
        ('system', 'System'),
        ('summary', 'Summary'),
        ('file-history-snapshot', 'File History Snapshot'),
        ('queue-operation', 'Queue Operation'),  # NEW: 7th message type
    ]
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    SYSTEM_SUBTYPE_CHOICES = [
        ('compact_boundary', 'Compact Boundary'),
        ('stop_hook_summary', 'Stop Hook Summary'),
        ('turn_duration', 'Turn Duration'),
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]
    PERMISSION_MODE_CHOICES = [
        ('default', 'Default'),
        ('acceptEdits', 'Accept Edits'),
        ('dontAsk', "Don't Ask"),
        ('bypassPermissions', 'Bypass Permissions'),
    ]

    id = models.CharField(max_length=64, primary_key=True, help_text="Message UUID")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='messages')
    parent_uuid = models.CharField(max_length=64, blank=True, db_index=True, help_text="Parent message for threading")
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    timestamp = models.DateTimeField(db_index=True)
    is_sidechain = models.BooleanField(default=False, help_text="Is this a subagent message?")

    # Context
    cwd = models.TextField(blank=True)
    git_branch = models.CharField(max_length=255, blank=True)
    version = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=100, blank=True, db_index=True)

    # NEW: Additional context fields
    slug = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Session slug reference"
    )
    user_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="User type: 'external', 'internal'"
    )

    # API details
    request_id = models.CharField(max_length=100, blank=True)
    stop_reason = models.CharField(max_length=50, blank=True)
    stop_sequence = models.CharField(max_length=50, blank=True)

    # NEW: API message ID (separate from our UUID)
    api_message_id = models.CharField(
        max_length=64,
        blank=True,
        help_text="API-level message ID from Claude"
    )

    # Tool references
    tool_use_id = models.CharField(max_length=64, blank=True, db_index=True)
    parent_tool_use_id = models.CharField(max_length=64, blank=True)

    # Content
    content_text = models.TextField(blank=True, help_text="Plain text content")
    content_json = models.JSONField(null=True, blank=True, help_text="Structured content")
    data_json = models.JSONField(null=True, blank=True, help_text="Additional data")

    # Snapshots (for file-history-snapshot type)
    snapshot_json = models.JSONField(null=True, blank=True)
    is_snapshot_update = models.BooleanField(null=True, blank=True)

    # NEW: System message subtypes and flags
    system_subtype = models.CharField(
        max_length=50,
        choices=SYSTEM_SUBTYPE_CHOICES,
        blank=True,
        db_index=True,
        help_text="Subtype for system messages: compact_boundary, stop_hook_summary, turn_duration"
    )
    is_meta = models.BooleanField(
        default=False,
        help_text="Meta message flag"
    )
    is_compact_summary = models.BooleanField(
        default=False,
        help_text="Message is a compact summary"
    )
    is_visible_in_transcript_only = models.BooleanField(
        default=False,
        help_text="Message visible only in transcript, not conversation"
    )
    permission_mode = models.CharField(
        max_length=30,
        choices=PERMISSION_MODE_CHOICES,
        blank=True,
        help_text="Permission mode during this message"
    )
    logical_parent_uuid = models.CharField(
        max_length=64,
        blank=True,
        help_text="Parent UUID for compact boundaries"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['type', '-timestamp']),
            models.Index(fields=['model', '-timestamp']),
            models.Index(fields=['system_subtype']),
        ]

    def __str__(self):
        return f"{self.type}/{self.role or 'none'} @ {self.timestamp}"


class MessageContentBlock(models.Model):
    """Content blocks within assistant messages (text, tool_use, tool_result, thinking)."""
    BLOCK_TYPE_CHOICES = [
        ('text', 'Text'),
        ('tool_use', 'Tool Use'),
        ('tool_result', 'Tool Result'),
        ('thinking', 'Thinking'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='content_blocks')
    block_index = models.IntegerField(help_text="Order within message")
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES, db_index=True)

    # Text content
    text_content = models.TextField(blank=True)

    # Tool use
    tool_use_id = models.CharField(max_length=64, blank=True, db_index=True)
    tool_name = models.CharField(max_length=100, blank=True)
    tool_input_json = models.JSONField(null=True, blank=True)
    tool_description = models.TextField(blank=True)

    # Tool result
    tool_result_content = models.TextField(blank=True)
    tool_result_is_error = models.BooleanField(null=True, blank=True)
    tool_result_for_tool_use_id = models.CharField(max_length=64, blank=True)

    # Thinking
    thinking_content = models.TextField(blank=True)
    thinking_signature = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['message', 'block_index']
        unique_together = ['message', 'block_index']
        indexes = [
            models.Index(fields=['block_type']),
            models.Index(fields=['tool_name']),
        ]

    def __str__(self):
        return f"{self.block_type} #{self.block_index} in {self.message_id[:8]}..."


class ToolUse(models.Model):
    """Tool invocations with their results."""
    id = models.CharField(max_length=64, primary_key=True, help_text="Tool use ID")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='tool_uses')
    tool_name = models.CharField(max_length=100, db_index=True)
    input_json = models.JSONField(help_text="Tool input parameters")
    description = models.TextField(blank=True)

    # Result tracking
    result_message = models.ForeignKey(
        Message, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tool_results_for'
    )
    result_content = models.TextField(blank=True)
    is_error = models.BooleanField(null=True, blank=True, db_index=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tool_name', '-created_at']),
            models.Index(fields=['is_error', '-created_at']),
        ]

    def __str__(self):
        return f"{self.tool_name} ({self.id[:8]}...)"


class TokenUsage(models.Model):
    """Token consumption per message."""
    message = models.OneToOneField(Message, on_delete=models.CASCADE, primary_key=True, related_name='token_usage')
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    cache_creation_input_tokens = models.IntegerField(default=0)
    cache_read_input_tokens = models.IntegerField(default=0)
    cache_creation_ephemeral_5m = models.IntegerField(default=0)
    cache_creation_ephemeral_1h = models.IntegerField(default=0)
    service_tier = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['input_tokens', 'output_tokens']),
        ]

    def __str__(self):
        return f"{self.input_tokens}in/{self.output_tokens}out for {self.message_id[:8]}..."


class ProgressEvent(models.Model):
    """
    Progress/hook events within transcripts.

    Supports multiple progress types from Claude Code:
    - hook_progress: Hook execution events
    - bash_progress: Bash command execution progress
    - agent_progress: Subagent execution progress
    - query_update: Query/search updates
    - search_results_received: Search results
    """
    PROGRESS_TYPE_CHOICES = [
        ('hook_progress', 'Hook Progress'),
        ('bash_progress', 'Bash Progress'),
        ('agent_progress', 'Agent Progress'),
        ('query_update', 'Query Update'),
        ('search_results_received', 'Search Results'),
        ('tool_progress', 'Tool Progress'),  # Generic tool progress
    ]

    message = models.OneToOneField(Message, on_delete=models.CASCADE, primary_key=True, related_name='progress_event')

    # Progress type discriminator
    progress_type = models.CharField(
        max_length=30,
        choices=PROGRESS_TYPE_CHOICES,
        default='hook_progress',
        db_index=True,
        help_text="Type of progress event"
    )

    # Hook progress fields (existing, but now properly typed)
    hook_event = models.CharField(max_length=50, blank=True, db_index=True)
    hook_name = models.CharField(max_length=100, blank=True, db_index=True)
    command = models.CharField(max_length=255, blank=True)

    # NEW: Bash progress fields
    output = models.TextField(
        blank=True,
        help_text="Current output for bash_progress"
    )
    full_output = models.TextField(
        blank=True,
        help_text="Complete output for bash_progress"
    )
    elapsed_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Duration for bash_progress"
    )
    total_lines = models.IntegerField(
        null=True,
        blank=True,
        help_text="Line count for bash_progress"
    )

    # NEW: Agent progress fields
    agent_id = models.CharField(
        max_length=64,
        blank=True,
        help_text="Agent ID for agent_progress"
    )
    prompt = models.TextField(
        blank=True,
        help_text="Agent prompt for agent_progress"
    )
    normalized_messages = models.JSONField(
        null=True,
        blank=True,
        help_text="Normalized messages for agent_progress"
    )

    # NEW: Query/search fields
    query = models.TextField(
        blank=True,
        help_text="Query text for query_update and search_results_received"
    )
    result_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of results for search_results_received"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['progress_type']),
            models.Index(fields=['hook_event']),
            models.Index(fields=['agent_id']),
        ]

    def __str__(self):
        if self.progress_type == 'hook_progress':
            return f"{self.hook_event}: {self.hook_name}"
        elif self.progress_type == 'bash_progress':
            return f"Bash: {self.elapsed_time_seconds}s, {self.total_lines} lines"
        elif self.progress_type == 'agent_progress':
            return f"Agent: {self.agent_id}"
        elif self.progress_type in ('query_update', 'search_results_received'):
            return f"Search: {self.result_count or 0} results"
        return f"{self.progress_type}"


class QueueOperation(models.Model):
    """
    Message queue operations for subagents.

    Tracks enqueue/remove operations that manage the subagent message queue.
    This is the 7th message type in Claude Code's JSONL format.
    """
    OPERATION_CHOICES = [
        ('enqueue', 'Enqueue'),
        ('remove', 'Remove'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid_lib.uuid4,
        help_text="Queue operation UUID"
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='queue_operations'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='queue_operations',
        help_text="Associated message if any"
    )
    operation = models.CharField(
        max_length=10,
        choices=OPERATION_CHOICES,
        db_index=True
    )
    timestamp = models.DateTimeField(db_index=True)
    content = models.TextField(
        blank=True,
        help_text="Queue item content"
    )
    queue_item_id = models.CharField(
        max_length=64,
        blank=True,
        help_text="ID of the queue item being operated on"
    )
    subagent_id = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="Subagent associated with this queue operation"
    )
    metadata_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional queue operation metadata"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['operation', '-timestamp']),
            models.Index(fields=['subagent_id']),
        ]

    def __str__(self):
        return f"{self.operation} @ {self.timestamp}"


class ThinkingMetadata(models.Model):
    """
    Extended thinking configuration per message.

    Tracks thinking budget and configuration for messages
    that use extended thinking mode.
    """
    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='thinking_metadata'
    )
    max_thinking_tokens = models.IntegerField(
        help_text="Maximum thinking tokens allowed"
    )
    budget_tokens = models.IntegerField(
        null=True,
        blank=True,
        help_text="Budget tokens allocated"
    )
    thinking_level = models.CharField(
        max_length=20,
        blank=True,
        help_text="Thinking level: low, medium, high, custom"
    )

    def __str__(self):
        return f"Thinking: {self.max_thinking_tokens} tokens for {self.message_id[:8]}..."


class SyncState(models.Model):
    """Sync state for incremental transcript processing."""
    session_id = models.CharField(max_length=64, primary_key=True)
    last_position = models.BigIntegerField(default=0, help_text="Byte position in JSONL file")
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sync state for {self.session_id[:8]}..."


class DailyIndex(models.Model):
    """Daily aggregated indices for quick lookups."""
    date = models.DateField(primary_key=True)
    session_count = models.IntegerField(default=0)
    event_count = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    summary = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name_plural = 'Daily indices'
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: {self.session_count} sessions, {self.total_tokens} tokens"
