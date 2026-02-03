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
        'claude_sessions.Session',
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
