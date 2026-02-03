"""Settings app - Configuration profiles and values."""
from django.db import models


class SettingsProfile(models.Model):
    """Settings profiles with scope inheritance."""
    SCOPE_CHOICES = [
        ('user', 'User (~/.claude/)'),
        ('project', 'Project (.claude/)'),
        ('local', 'Local (.claude/*.local.*)'),
        ('managed', 'Managed (Enterprise)'),  # NEW: Enterprise managed settings
    ]

    profile_name = models.CharField(max_length=100)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False, db_index=True)
    parent_profile = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='child_profiles',
        help_text="Parent profile for inheritance"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata_json = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['profile_name', 'scope']
        ordering = ['scope', 'profile_name']

    def __str__(self):
        return f"{self.profile_name} ({self.scope})"


class SettingsValue(models.Model):
    """Key-value settings storage."""
    VALUE_TYPE_CHOICES = [
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('object', 'Object'),
        ('array', 'Array'),
        ('null', 'Null'),
    ]

    profile = models.ForeignKey(SettingsProfile, on_delete=models.CASCADE, related_name='values')
    setting_key = models.CharField(max_length=200, db_index=True)
    setting_value = models.TextField(blank=True)
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    is_sensitive = models.BooleanField(default=False, help_text="Hide value in UI")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata_json = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['profile', 'setting_key']
        ordering = ['category', 'setting_key']

    def __str__(self):
        return f"{self.setting_key} = {self.setting_value[:50]}..."


class ModelPreference(models.Model):
    """Model-related preferences."""
    THINKING_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('custom', 'Custom'),
    ]

    profile = models.OneToOneField(SettingsProfile, on_delete=models.CASCADE, primary_key=True, related_name='model_preferences')
    default_model = models.CharField(max_length=100, blank=True)
    thinking_level = models.CharField(max_length=20, choices=THINKING_LEVEL_CHOICES, blank=True)
    thinking_budget = models.IntegerField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    max_tokens = models.IntegerField(null=True, blank=True)
    top_p = models.FloatField(null=True, blank=True)
    top_k = models.IntegerField(null=True, blank=True)
    custom_params_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Model prefs for {self.profile}"


class PermissionRule(models.Model):
    """Permission rules for tools and resources."""
    RULE_TYPE_CHOICES = [
        ('allow', 'Allow'),
        ('ask', 'Ask'),    # NEW: Prompts user for confirmation
        ('deny', 'Deny'),
    ]
    ACCESS_LEVEL_CHOICES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('execute', 'Execute'),
        ('all', 'All'),
    ]

    profile = models.ForeignKey(SettingsProfile, on_delete=models.CASCADE, related_name='permission_rules')
    rule_type = models.CharField(max_length=10, choices=RULE_TYPE_CHOICES, db_index=True)
    tool_pattern = models.CharField(max_length=200, help_text="Tool name pattern (supports wildcards)")
    resource_pattern = models.CharField(max_length=500, blank=True, help_text="Resource path pattern")
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        blank=True,
        help_text="Access level for this rule"
    )
    priority = models.IntegerField(default=0, help_text="Higher = evaluated first")
    is_enabled = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata_json = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-priority']
        indexes = [
            models.Index(fields=['rule_type', '-priority']),
        ]

    def __str__(self):
        return f"{self.rule_type}: {self.tool_pattern}"


class ThemeSetting(models.Model):
    """Theme/appearance settings."""
    COLOR_SCHEME_CHOICES = [('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')]

    profile = models.OneToOneField(SettingsProfile, on_delete=models.CASCADE, primary_key=True, related_name='theme_settings')
    theme_name = models.CharField(max_length=100)
    color_scheme = models.CharField(max_length=20, choices=COLOR_SCHEME_CHOICES, blank=True)
    primary_color = models.CharField(max_length=20, blank=True)
    accent_color = models.CharField(max_length=20, blank=True)
    background_color = models.CharField(max_length=20, blank=True)
    text_color = models.CharField(max_length=20, blank=True)
    custom_css = models.TextField(blank=True)
    custom_colors_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.theme_name} ({self.profile})"


class ApiConfig(models.Model):
    """API configuration settings."""
    profile = models.OneToOneField(SettingsProfile, on_delete=models.CASCADE, primary_key=True, related_name='api_config')
    api_key_encrypted = models.TextField(blank=True, help_text="Encrypted API key")
    api_base_url = models.URLField(blank=True)
    organization_id = models.CharField(max_length=100, blank=True)
    timeout_seconds = models.IntegerField(null=True, blank=True)
    max_retries = models.IntegerField(null=True, blank=True)
    retry_delay_ms = models.IntegerField(null=True, blank=True)
    custom_headers_json = models.JSONField(default=dict, blank=True)
    proxy_url = models.URLField(blank=True)
    verify_ssl = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"API config for {self.profile}"


class SettingsHistory(models.Model):
    """Audit trail for settings changes."""
    profile = models.ForeignKey(SettingsProfile, on_delete=models.CASCADE, related_name='history')
    setting_key = models.CharField(max_length=200, db_index=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    changed_by = models.CharField(max_length=100, blank=True)
    change_reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Settings histories'

    def __str__(self):
        return f"{self.setting_key} changed @ {self.changed_at}"


# ============================================================================
# NEW MODELS: Sandbox, Environment Variables, Global Permissions
# ============================================================================

class SandboxConfig(models.Model):
    """Sandbox configuration for secure execution."""
    profile = models.OneToOneField(
        SettingsProfile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='sandbox_config'
    )
    enabled = models.BooleanField(default=False)
    auto_allow_bash_if_sandboxed = models.BooleanField(
        default=True,
        help_text="Auto-allow Bash commands when sandboxing is enabled"
    )
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sandbox Configuration"

    def __str__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"Sandbox ({status}) for {self.profile}"


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['profile', 'variable_name']]
        ordering = ['category', 'variable_name']

    def __str__(self):
        return f"{self.variable_name} ({self.profile})"


class GlobalPermissionSettings(models.Model):
    """Global permission settings beyond individual rules."""
    DEFAULT_MODE_CHOICES = [
        ('normal', 'Normal'),
        ('acceptEdits', 'Accept Edits'),
        ('dontAsk', "Don't Ask"),
        ('bypassPermissions', 'Bypass Permissions'),
    ]

    profile = models.OneToOneField(
        SettingsProfile,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='global_permissions'
    )
    additional_directories = models.JSONField(
        default=list,
        help_text="Additional directories Claude can access"
    )
    default_mode = models.CharField(
        max_length=30,
        choices=DEFAULT_MODE_CHOICES,
        default='normal',
        help_text="Default permission mode"
    )
    disable_bypass_mode = models.BooleanField(
        default=False,
        help_text="Restrict bypass mode availability"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Permission Settings"
        verbose_name_plural = "Global Permission Settings"

    def __str__(self):
        return f"Global permissions ({self.default_mode}) for {self.profile}"
