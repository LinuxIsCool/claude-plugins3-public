# Observatory Schema Consolidation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Systematically implement ~185 schema changes across 10 existing Django apps and create 8 new apps to fully model Claude Code's data structures.

**Architecture:** Phased approach starting with critical foundation fixes (output_styles redesign, missing hook events), then cost tracking, then incremental app enhancements. Each phase is independently deployable with migrations.

**Tech Stack:** Django 5.0+, PostgreSQL with pgvector, Django REST Framework, drf-spectacular for API docs.

---

## Overview

**Total Scope:**
- 10 existing apps requiring updates
- 8 new apps to create
- ~46 current models → ~115 models
- ~185 total schema modifications

**Phase Structure:**
1. **Phase 1: Critical Foundation** - Fix fundamentally broken models (output_styles, hooks)
2. **Phase 2: Sessions Enhancement** - Add missing message types and fields
3. **Phase 3: Billing App** - New app for cost tracking
4. **Phase 4: Plugin/Skill Enhancement** - Multi-scope installations, invocation tracking
5. **Phase 5: File & Workspace Apps** - New apps for file operations and workspace state
6. **Phase 6: Identity & Compliance** - New apps for accounts, organizations, SSO

---

## Phase 1: Critical Foundation

### Task 1.1: Output Styles Complete Redesign

**Context:** Current `OutputPreference` model is fundamentally incorrect. Output styles are NOT formatting preferences - they are **complete system prompt replacements**.

**Files:**
- Delete content: `output_styles/models.py`
- Create migration: `output_styles/migrations/0002_redesign_output_styles.py`
- Modify: `output_styles/admin.py`

**Step 1: Read current models**

Run: `cat plugins/observatory/skills/observatory/output_styles/models.py`

**Step 2: Write new models.py**

```python
"""
Output Styles Models

CRITICAL: Output styles are NOT formatting preferences.
They are COMPLETE SYSTEM PROMPT REPLACEMENTS that can
dramatically alter Claude's behavior.

Example built-in styles: concise, verbose, code-only, explanatory
Each replaces the entire system prompt with custom instructions.
"""
from django.db import models


class OutputStyle(models.Model):
    """
    Output style = complete system prompt replacement.

    NOT a formatting preference. The system_prompt field contains
    the ENTIRE system prompt that replaces Claude's default behavior.
    """
    SOURCE_CHOICES = [
        ('builtin', 'Built-in'),
        ('user', 'User Custom'),
        ('project', 'Project'),
        ('plugin', 'Plugin'),
        ('managed', 'Managed'),
    ]
    CATEGORY_CHOICES = [
        ('communication', 'Communication Style'),
        ('expertise', 'Expertise Level'),
        ('format', 'Response Format'),
        ('context', 'Context-specific'),
        ('custom', 'Custom'),
    ]

    style_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Unique identifier (e.g., 'concise', 'verbose', 'explanatory')"
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Human-readable name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this style does"
    )

    # The actual content - THIS IS THE KEY FIELD
    system_prompt = models.TextField(
        help_text="Complete system prompt content that REPLACES the default"
    )

    # Behavior control
    keep_coding_instructions = models.BooleanField(
        default=False,
        help_text="If True, coding instructions are preserved alongside this style"
    )

    # Metadata
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='user'
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='custom'
    )
    is_active = models.BooleanField(default=True)

    # Plugin association (optional)
    plugin = models.ForeignKey(
        'plugins.Plugin',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='output_styles'
    )

    # Analytics
    usage_count = models.IntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['source', 'style_name']]
        ordering = ['source', 'style_name']

    def __str__(self):
        return f"{self.display_name} ({self.source})"


class OutputStyleActivation(models.Model):
    """
    Track when output styles are activated in sessions.

    Allows analyzing which styles are used most, session duration
    with each style, and style switching patterns.
    """
    ACTIVATION_SOURCE_CHOICES = [
        ('settings', 'Settings Default'),
        ('command', 'Slash Command'),
        ('hook', 'Hook'),
        ('api', 'API Override'),
    ]

    style = models.ForeignKey(
        OutputStyle,
        on_delete=models.CASCADE,
        related_name='activations'
    )
    session = models.ForeignKey(
        'sessions.Session',
        on_delete=models.CASCADE,
        related_name='style_activations'
    )

    activated_at = models.DateTimeField(auto_now_add=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    activation_source = models.CharField(
        max_length=30,
        choices=ACTIVATION_SOURCE_CHOICES,
        default='settings'
    )

    class Meta:
        ordering = ['-activated_at']

    def __str__(self):
        return f"{self.style.style_name} in {self.session_id}"
```

**Step 3: Create migration**

Run: `cd plugins/observatory/skills/observatory && python manage.py makemigrations output_styles --name redesign_output_styles`

**Step 4: Update admin.py**

```python
from django.contrib import admin
from .models import OutputStyle, OutputStyleActivation


@admin.register(OutputStyle)
class OutputStyleAdmin(admin.ModelAdmin):
    list_display = ['style_name', 'display_name', 'source', 'category', 'is_active', 'usage_count']
    list_filter = ['source', 'category', 'is_active']
    search_fields = ['style_name', 'display_name', 'description']
    readonly_fields = ['usage_count', 'last_used_at', 'created_at', 'updated_at']


@admin.register(OutputStyleActivation)
class OutputStyleActivationAdmin(admin.ModelAdmin):
    list_display = ['style', 'session', 'activation_source', 'activated_at']
    list_filter = ['activation_source', 'activated_at']
    raw_id_fields = ['style', 'session']
```

**Step 5: Run migration**

Run: `cd plugins/observatory/skills/observatory && python manage.py migrate output_styles`

**Step 6: Commit**

```bash
git add plugins/observatory/skills/observatory/output_styles/
git commit -m "feat(output_styles): Complete redesign - styles are system prompts

BREAKING CHANGE: OutputPreference model replaced with OutputStyle.
Output styles are NOT formatting preferences - they are complete
system prompt replacements that alter Claude's behavior.

New models:
- OutputStyle: Complete system prompt with metadata
- OutputStyleActivation: Track style usage in sessions

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 1.2: Hooks - Add Missing Event Types

**Context:** Current model has 13 event types but is missing 4 official Claude Code events: `PostToolUseFailure`, `PermissionRequest`, `SubagentStart`, `Setup`.

**Files:**
- Modify: `hooks/models.py` (add EVENT_TYPE choices)
- Create: `hooks/migrations/0002_add_missing_event_types.py`

**Step 1: Read current hooks/models.py**

Run: `cat plugins/observatory/skills/observatory/hooks/models.py`

**Step 2: Update EVENT_TYPE_CHOICES in HookDefinition**

Add to the choices list:
```python
EVENT_TYPE_CHOICES = [
    ('PreToolUse', 'Pre Tool Use'),
    ('PostToolUse', 'Post Tool Use'),
    ('PostToolUseFailure', 'Post Tool Use Failure'),  # NEW
    ('PermissionRequest', 'Permission Request'),       # NEW
    ('UserPromptSubmit', 'User Prompt Submit'),
    ('Notification', 'Notification'),
    ('Stop', 'Stop'),
    ('SubagentStart', 'Subagent Start'),              # NEW
    ('SubagentStop', 'Subagent Stop'),
    ('Setup', 'Setup'),                                # NEW
    ('SessionStart', 'Session Start'),
    ('SessionEnd', 'Session End'),
    ('PreCompact', 'Pre Compact'),
]
```

**Step 3: Add new event detail models**

```python
class HookEventPostToolUseFailure(models.Model):
    """Post tool use failure event details."""
    hook_event = models.OneToOneField(
        HookEvent,
        on_delete=models.CASCADE,
        related_name='post_tool_use_failure_details'
    )
    tool_name = models.CharField(max_length=100, db_index=True)
    tool_input = models.TextField(blank=True)
    tool_use_id = models.CharField(max_length=64, blank=True)
    error_type = models.CharField(max_length=100, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    exit_code = models.IntegerField(null=True)
    stderr = models.TextField(blank=True)

    class Meta:
        verbose_name = "Hook Event: Post Tool Use Failure"
        verbose_name_plural = "Hook Events: Post Tool Use Failures"


class HookEventPermissionRequest(models.Model):
    """Permission request event details."""
    DECISION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('pending', 'Pending'),
    ]

    hook_event = models.OneToOneField(
        HookEvent,
        on_delete=models.CASCADE,
        related_name='permission_request_details'
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


class HookEventSubagentStart(models.Model):
    """Subagent start event details."""
    hook_event = models.OneToOneField(
        HookEvent,
        on_delete=models.CASCADE,
        related_name='subagent_start_details'
    )
    agent_id = models.CharField(max_length=64, db_index=True)
    agent_type = models.CharField(max_length=50, db_index=True)
    parent_session_id = models.CharField(max_length=64, blank=True)
    task_description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Hook Event: Subagent Start"
        verbose_name_plural = "Hook Events: Subagent Starts"


class HookEventSetup(models.Model):
    """Setup event details (--init, --init-only, --maintenance)."""
    TRIGGER_CHOICES = [
        ('init', 'Init'),
        ('init_only', 'Init Only'),
        ('maintenance', 'Maintenance'),
    ]

    hook_event = models.OneToOneField(
        HookEvent,
        on_delete=models.CASCADE,
        related_name='setup_details'
    )
    trigger = models.CharField(max_length=20, choices=TRIGGER_CHOICES, db_index=True)
    working_directory = models.TextField(blank=True)
    additional_context = models.TextField(blank=True)
    env_vars_set = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Hook Event: Setup"
        verbose_name_plural = "Hook Events: Setup"
```

**Step 4: Add hook_type and matcher fields to HookDefinition**

```python
# In HookDefinition model, add:
HOOK_TYPE_CHOICES = [
    ('command', 'Command'),
    ('prompt', 'Prompt'),
]

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
    blank=True,
    help_text="Origin: user/project/local/plugin/skill/agent/policy"
)
```

**Step 5: Create migration**

Run: `cd plugins/observatory/skills/observatory && python manage.py makemigrations hooks --name add_missing_event_types`

**Step 6: Run migration**

Run: `cd plugins/observatory/skills/observatory && python manage.py migrate hooks`

**Step 7: Commit**

```bash
git add plugins/observatory/skills/observatory/hooks/
git commit -m "feat(hooks): Add 4 missing event types and hook_type field

Add missing official Claude Code hook events:
- PostToolUseFailure: After tool execution fails
- PermissionRequest: Permission dialog shown
- SubagentStart: When subagent spawns
- Setup: --init, --init-only, --maintenance

Also add:
- hook_type field (command vs prompt)
- matcher field for tool-specific hooks
- source field for hook origin tracking

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 1.3: Settings - Add Missing Scopes and Permission States

**Context:** Settings has 3 scopes but Claude Code has 4 (missing `managed`). Permission rules have 2 states but Claude Code has 3 (missing `ask`).

**Files:**
- Modify: `settings/models.py`
- Create: `settings/migrations/0002_add_managed_scope_ask_permission.py`

**Step 1: Read current settings/models.py**

Run: `cat plugins/observatory/skills/observatory/settings/models.py`

**Step 2: Update SCOPE_CHOICES in SettingsProfile**

```python
SCOPE_CHOICES = [
    ('user', 'User (~/.claude/)'),
    ('project', 'Project (.claude/)'),
    ('local', 'Local (.claude/*.local.*)'),
    ('managed', 'Managed (Enterprise)'),  # NEW
]
```

**Step 3: Update RULE_TYPE_CHOICES in PermissionRule**

```python
RULE_TYPE_CHOICES = [
    ('allow', 'Allow'),
    ('ask', 'Ask'),    # NEW - prompts user for confirmation
    ('deny', 'Deny'),
]
```

**Step 4: Add new settings-related models**

```python
class SandboxConfig(models.Model):
    """Sandbox configuration for secure execution."""
    profile = models.OneToOneField(
        SettingsProfile,
        on_delete=models.CASCADE,
        related_name='sandbox_config'
    )
    enabled = models.BooleanField(default=False)
    auto_allow_bash_if_sandboxed = models.BooleanField(default=True)
    excluded_commands = models.JSONField(
        default=list,
        help_text="Commands excluded from sandboxing"
    )
    allow_unsandboxed_commands = models.BooleanField(default=False)
    enable_weaker_nested_sandbox = models.BooleanField(default=False)
    allow_unix_sockets = models.JSONField(
        default=list,
        help_text="Unix socket paths allowed"
    )
    allow_local_binding = models.BooleanField(default=True)
    http_proxy_port = models.IntegerField(null=True, blank=True)
    socks_proxy_port = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Sandbox Configuration"


class EnvironmentVariable(models.Model):
    """Environment variables for sessions."""
    profile = models.ForeignKey(
        SettingsProfile,
        on_delete=models.CASCADE,
        related_name='environment_variables'
    )
    variable_name = models.CharField(max_length=100)
    variable_value = models.TextField()
    is_sensitive = models.BooleanField(
        default=False,
        help_text="If True, value is masked in UI"
    )
    is_script = models.BooleanField(
        default=False,
        help_text="If True, value is result of script execution"
    )
    category = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = [['profile', 'variable_name']]
        ordering = ['category', 'variable_name']


class GlobalPermissionSettings(models.Model):
    """Global permission settings beyond individual rules."""
    profile = models.OneToOneField(
        SettingsProfile,
        on_delete=models.CASCADE,
        related_name='global_permissions'
    )
    additional_directories = models.JSONField(
        default=list,
        help_text="Additional directories Claude can access"
    )
    default_mode = models.CharField(
        max_length=30,
        default='normal',
        help_text="Default permission mode: normal, acceptEdits, dontAsk, bypassPermissions"
    )
    disable_bypass_mode = models.CharField(
        max_length=20,
        blank=True,
        help_text="Restrict bypass mode availability"
    )

    class Meta:
        verbose_name = "Global Permission Settings"
        verbose_name_plural = "Global Permission Settings"
```

**Step 5: Create and run migration**

Run:
```bash
cd plugins/observatory/skills/observatory && \
python manage.py makemigrations settings --name add_managed_scope_ask_permission && \
python manage.py migrate settings
```

**Step 6: Commit**

```bash
git add plugins/observatory/skills/observatory/settings/
git commit -m "feat(settings): Add managed scope, ask permission, sandbox config

- Add 'managed' to SCOPE_CHOICES for enterprise settings
- Add 'ask' to RULE_TYPE_CHOICES (allow/ask/deny)
- Add SandboxConfig model for secure execution settings
- Add EnvironmentVariable model for env var management
- Add GlobalPermissionSettings for default modes

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Sessions Enhancement

### Task 2.1: Add Missing Session Fields

**Files:**
- Modify: `sessions/models.py`
- Create migration

**Step 1: Read current Session model**

**Step 2: Add fields to Session model**

```python
# Add to Session model:
slug = models.CharField(
    max_length=100,
    blank=True,
    db_index=True,
    help_text="Human-readable name (e.g., 'calm-dreaming-backus')"
)
git_branch = models.CharField(
    max_length=255,
    blank=True,
    help_text="Primary git branch at session start"
)
version = models.CharField(
    max_length=20,
    blank=True,
    help_text="Claude Code version"
)
user_type = models.CharField(
    max_length=20,
    blank=True,
    help_text="'external' or 'internal'"
)
```

**Step 3: Create and run migration**

**Step 4: Commit**

---

### Task 2.2: Add Missing Message Fields

**Files:**
- Modify: `sessions/models.py`
- Create migration

**Step 1: Add fields to Message model**

```python
# Add to Message model:
system_subtype = models.CharField(
    max_length=50,
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
permission_mode = models.CharField(
    max_length=30,
    blank=True,
    help_text="Permission mode: bypassPermissions, acceptEdits, etc."
)
logical_parent_uuid = models.CharField(
    max_length=64,
    blank=True,
    help_text="Parent UUID for compact boundaries"
)
```

**Step 2: Create and run migration**

**Step 3: Commit**

---

### Task 2.3: Add QueueOperation Model

**Context:** Missing `queue-operation` message type for subagent queue management.

**Files:**
- Modify: `sessions/models.py`
- Create migration

**Step 1: Add model**

```python
class QueueOperation(models.Model):
    """
    Message queue operations for subagents.

    Tracks enqueue/remove operations that manage the subagent message queue.
    This is the 7th message type (missing from original schema).
    """
    OPERATION_CHOICES = [
        ('enqueue', 'Enqueue'),
        ('remove', 'Remove'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
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
        related_name='queue_operations'
    )
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    timestamp = models.DateTimeField(db_index=True)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ['timestamp']
```

**Step 2: Create and run migration**

**Step 3: Commit**

---

### Task 2.4: Add Missing ProgressEvent Types

**Context:** Model only has 1 progress type but Claude Code has 5.

**Step 1: Update ProgressEvent or create subtype models**

```python
# Add to ProgressEvent:
PROGRESS_TYPE_CHOICES = [
    ('tool_progress', 'Tool Progress'),
    ('bash_progress', 'Bash Progress'),
    ('agent_progress', 'Agent Progress'),
    ('query_update', 'Query Update'),
    ('search_results_received', 'Search Results Received'),
]

progress_type = models.CharField(
    max_length=30,
    choices=PROGRESS_TYPE_CHOICES,
    default='tool_progress'
)

# Bash progress fields
full_output = models.TextField(blank=True)
elapsed_time_seconds = models.FloatField(null=True)
total_lines = models.IntegerField(null=True)

# Agent progress fields
agent_id = models.CharField(max_length=64, blank=True)
normalized_messages = models.JSONField(null=True)

# Query/search fields
query = models.TextField(blank=True)
result_count = models.IntegerField(null=True)
```

**Step 2: Create and run migration**

**Step 3: Commit**

---

## Phase 3: Billing App (New)

### Task 3.1: Create Billing App Structure

**Files:**
- Create: `billing/` directory structure
- Create: `billing/__init__.py`
- Create: `billing/apps.py`
- Create: `billing/models.py`
- Create: `billing/admin.py`

**Step 1: Create app**

Run: `cd plugins/observatory/skills/observatory && python manage.py startapp billing`

**Step 2: Write models.py**

```python
"""
Billing Models

Tracks costs, pricing, budgets, and rate limits for Claude Code usage.
Critical for cost management and usage analytics.
"""
from django.db import models
from decimal import Decimal


class ModelPricing(models.Model):
    """
    Token pricing by model.

    Prices are per MTok (million tokens). Supports:
    - Standard input/output pricing
    - Cache write/read pricing (5m ephemeral, 1h ephemeral)
    - Long context surcharges (>200k tokens)
    - Batch pricing discounts
    """
    model_id = models.CharField(max_length=100, primary_key=True)
    model_family = models.CharField(
        max_length=50,
        db_index=True,
        help_text="opus, sonnet, haiku"
    )
    model_generation = models.CharField(
        max_length=20,
        help_text="4.5, 4.1, 4, 3.5, etc."
    )

    # Standard pricing (per MTok)
    input_price_mtok = models.DecimalField(max_digits=10, decimal_places=4)
    output_price_mtok = models.DecimalField(max_digits=10, decimal_places=4)

    # Cache pricing (per MTok)
    cache_write_5m_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="5-minute ephemeral cache write"
    )
    cache_write_1h_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="1-hour ephemeral cache write"
    )
    cache_read_price_mtok = models.DecimalField(max_digits=10, decimal_places=4)

    # Long context pricing
    long_context_threshold = models.IntegerField(
        null=True,
        help_text="Token count threshold for long context pricing"
    )
    long_context_input_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True
    )
    long_context_output_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True
    )

    # Batch pricing
    batch_input_price_mtok = models.DecimalField(max_digits=10, decimal_places=4)
    batch_output_price_mtok = models.DecimalField(max_digits=10, decimal_places=4)

    # Validity period
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_deprecated = models.BooleanField(default=False)

    class Meta:
        ordering = ['-effective_from', 'model_family']

    def __str__(self):
        return f"{self.model_id} (from {self.effective_from})"


class ToolPricing(models.Model):
    """Tool-specific pricing (e.g., web search, code execution)."""
    PRICING_TYPE_CHOICES = [
        ('tokens', 'Per Token'),
        ('per_use', 'Per Use'),
        ('per_hour', 'Per Hour'),
        ('per_search', 'Per Search'),
    ]

    tool_name = models.CharField(max_length=100, primary_key=True)
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPE_CHOICES)
    cost_amount = models.DecimalField(max_digits=10, decimal_places=4)
    cost_unit = models.CharField(
        max_length=50,
        help_text="e.g., '1000 searches', 'hour', 'use'"
    )
    base_tokens = models.IntegerField(
        default=0,
        help_text="Base token cost per invocation"
    )
    free_tier_amount = models.IntegerField(
        default=0,
        help_text="Free tier allocation (e.g., 1550 hours for code execution)"
    )
    effective_from = models.DateField()

    def __str__(self):
        return f"{self.tool_name}: ${self.cost_amount}/{self.cost_unit}"


class MessageCost(models.Model):
    """Computed cost for each message."""
    message = models.OneToOneField(
        'sessions.Message',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cost'
    )
    model_pricing = models.ForeignKey(
        ModelPricing,
        on_delete=models.SET_NULL,
        null=True
    )

    # Cost breakdown
    input_cost = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    output_cost = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    cache_write_cost = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    cache_read_cost = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    tool_cost = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    web_search_cost = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    total_cost = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))

    # Flags
    is_batch = models.BooleanField(default=False)
    is_long_context = models.BooleanField(default=False)

    def __str__(self):
        return f"${self.total_cost} for message {self.message_id}"


class SessionCost(models.Model):
    """Aggregated costs per session."""
    session = models.OneToOneField(
        'sessions.Session',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cost'
    )

    # Token totals
    total_input_tokens = models.BigIntegerField(default=0)
    total_output_tokens = models.BigIntegerField(default=0)

    # Cost totals
    total_token_cost = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal('0'))
    total_tool_cost = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal('0'))
    total_cost = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal('0'))

    # Breakdowns
    cost_by_model = models.JSONField(default=dict)
    cost_by_tool = models.JSONField(default=dict)

    def __str__(self):
        return f"${self.total_cost} for session {self.session_id}"


class DailyCost(models.Model):
    """Daily cost aggregation."""
    date = models.DateField(primary_key=True)
    total_sessions = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal('0'))
    cost_by_model = models.JSONField(default=dict)
    cost_by_tool = models.JSONField(default=dict)
    cost_by_project = models.JSONField(default=dict)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: ${self.total_cost}"


class Budget(models.Model):
    """Budget limits and alerts."""
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('project', 'Project'),
        ('workspace', 'Workspace'),
        ('model', 'Model'),
    ]
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    ACTION_CHOICES = [
        ('warn', 'Warn Only'),
        ('soft_limit', 'Soft Limit'),
        ('hard_limit', 'Hard Limit'),
    ]

    name = models.CharField(max_length=100)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    scope_identifier = models.CharField(
        max_length=200,
        blank=True,
        help_text="Project path, workspace ID, or model ID"
    )
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    limit_amount = models.DecimalField(max_digits=14, decimal_places=2)
    soft_limit_pct = models.IntegerField(
        default=80,
        help_text="Percentage at which to send warning"
    )
    current_spend = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal('0'))
    period_start = models.DateField()
    period_end = models.DateField()
    hard_limit_action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        default='warn'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['scope', 'name']

    def __str__(self):
        return f"{self.name}: ${self.limit_amount}/{self.period}"


class BudgetAlert(models.Model):
    """Budget alert history."""
    ALERT_TYPE_CHOICES = [
        ('soft_warning', 'Soft Warning'),
        ('hard_warning', 'Hard Warning'),
        ('limit_reached', 'Limit Reached'),
    ]

    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    threshold_pct = models.IntegerField()
    current_spend = models.DecimalField(max_digits=14, decimal_places=6)
    message = models.TextField()
    is_acknowledged = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-triggered_at']


class WebSearchUsage(models.Model):
    """Web search usage tracking ($10/1000 searches)."""
    session = models.ForeignKey(
        'sessions.Session',
        on_delete=models.CASCADE,
        related_name='web_searches'
    )
    message = models.ForeignKey(
        'sessions.Message',
        on_delete=models.CASCADE,
        related_name='web_searches'
    )
    search_count = models.IntegerField(default=1)
    query_preview = models.CharField(max_length=200, blank=True)
    result_count = models.IntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=12, decimal_places=6)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
```

**Step 3: Register in INSTALLED_APPS**

Add `'billing',` to settings.py INSTALLED_APPS.

**Step 4: Create admin.py**

**Step 5: Create and run migrations**

**Step 6: Commit**

```bash
git add plugins/observatory/skills/observatory/billing/
git commit -m "feat(billing): Add new billing app for cost tracking

New models:
- ModelPricing: Token pricing by model with cache/batch/long-context tiers
- ToolPricing: Tool-specific pricing (web search, code execution)
- MessageCost: Per-message cost breakdown
- SessionCost: Session cost aggregation
- DailyCost: Daily cost aggregation
- Budget: Budget limits and alerts
- BudgetAlert: Alert history
- WebSearchUsage: Web search usage tracking

Addresses the critical gap where TokenUsage exists but costUSD=0.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 4: Plugin/Skill Enhancement

### Task 4.1: Add Marketplace Model

### Task 4.2: Add PluginInstallation Model (Multi-Scope)

### Task 4.3: Add PluginComponent Model

### Task 4.4: Add SkillInvocation Model

### Task 4.5: Add CommandInvocation Model

### Task 4.6: Update Plugin Model Fields

### Task 4.7: Update Skill Model Fields

### Task 4.8: Update Command Model Fields

---

## Phase 5: File & Workspace Apps (New)

### Task 5.1: Create file_operations App

**Models:**
- FileOperation
- FileVersion
- FileHistorySnapshot
- FileAccessPattern

### Task 5.2: Create workspace App

**Models:**
- Project
- WorkspaceContext
- WorkingDirectoryChange
- ShellSnapshot

### Task 5.3: Create git_tracking App

**Models:**
- GitOperation
- GitBranchTransition
- CommitAuthor

### Task 5.4: Create tasks App

**Models:**
- Task
- TaskDependency
- Instance

---

## Phase 6: Identity & Compliance (New)

### Task 6.1: Create accounts App

**Models:**
- User
- AuthCredential
- AuthEvent

### Task 6.2: Create organizations App

**Models:**
- Organization
- ParentOrganization
- OrganizationMembership
- Workspace

### Task 6.3: Create compliance App

**Models:**
- AuditLog
- DataRetentionPolicy
- ComplianceApiAccess
- BusinessAssociateAgreement
- DataSubjectRequest

### Task 6.4: Create sso App

**Models:**
- SSOConfiguration
- SCIMConfiguration
- DomainVerification

---

## Phase 7: Agents & MCPs Enhancement

### Task 7.1: Update Agent Model Fields

### Task 7.2: Update SubagentSession Model Fields

### Task 7.3: Add AgentScope Model

### Task 7.4: Add SubagentMetrics Model

### Task 7.5: Add SubagentPermission Model

### Task 7.6: Update McpServer Model (Transport Types)

### Task 7.7: Add McpServerCapability Model

### Task 7.8: Add McpTool Model

### Task 7.9: Add McpResource Model

### Task 7.10: Add McpPrompt Model

### Task 7.11: Add McpConnectionStatus Model

---

## Execution Notes

### Database Migrations Strategy

1. **Run migrations incrementally** - Each phase should be independently deployable
2. **Use `--fake` if needed** - For complex model replacements
3. **Data migrations** - Create separate data migrations for any data transformations

### Testing Strategy

1. **Model tests** - Test each new model's fields, constraints, relationships
2. **Admin tests** - Verify admin interfaces work
3. **Migration tests** - Test migrations can be applied and reversed

### Deployment Order

```
Phase 1 (Critical) → Phase 2 (Sessions) → Phase 3 (Billing) → Phase 4 (Plugins) → Phase 5 (Files) → Phase 6 (Identity) → Phase 7 (Agents/MCPs)
```

Each phase can be deployed independently once migrations pass.
