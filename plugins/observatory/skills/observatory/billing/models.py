"""
Billing Models - Comprehensive Cost Tracking for Claude Code Observatory

This app provides complete cost tracking with:
- Effective-dated pricing (historical pricing support)
- Three-tier aggregation: MessageCost -> SessionCost -> DailyCost
- Dimensional breakdowns by model and tool
- Rate limiting with consumption tracking
- Manual adjustment support with approval workflow

Architecture follows Observatory patterns:
- OneToOne with primary_key=True for extension models
- Pre-aggregation for fast queries
- JSONField for flexible metadata
- Extensive indexing on filter/sort fields
"""
from decimal import Decimal
from django.db import models


class PricingTier(models.Model):
    """
    Token pricing with effective dates for historical accuracy.

    Prices are stored per MTok (million tokens) to match Anthropic's
    pricing model. Supports cache tiers, extended thinking, and batch pricing.
    """
    # Identification
    model_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Model identifier (e.g., 'claude-opus-4-5-20251101')"
    )
    model_family = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Model family: opus, sonnet, haiku"
    )
    model_generation = models.CharField(
        max_length=20,
        blank=True,
        help_text="Model generation: 4.5, 4.1, 4, 3.5, etc."
    )

    # Standard token pricing (per MTok)
    input_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Input token price per million tokens"
    )
    output_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Output token price per million tokens"
    )

    # Cache pricing (per MTok)
    cache_write_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Cache creation price per million tokens"
    )
    cache_read_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Cache read price per million tokens"
    )
    cache_ephemeral_5m_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        help_text="5-minute ephemeral cache price per MTok"
    )
    cache_ephemeral_1h_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        help_text="1-hour ephemeral cache price per MTok"
    )

    # Extended thinking pricing
    thinking_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        help_text="Extended thinking token price per MTok"
    )

    # Batch pricing (typically 50% discount)
    batch_input_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Batch API input price per MTok"
    )
    batch_output_price_mtok = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Batch API output price per MTok"
    )

    # Effective date range
    effective_from = models.DateField(
        db_index=True,
        help_text="Date this pricing becomes effective"
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text="Date this pricing ends (null = still current)"
    )
    is_deprecated = models.BooleanField(
        default=False,
        help_text="Model is deprecated"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['model_name', 'effective_from']]
        ordering = ['-effective_from', 'model_family']
        indexes = [
            models.Index(fields=['model_name', '-effective_from']),
            models.Index(fields=['model_family', '-effective_from']),
        ]

    def __str__(self):
        return f"{self.model_name} (from {self.effective_from})"


class MessageCost(models.Model):
    """
    Per-message cost tracking - the source of truth for cost calculations.

    This model enables:
    - Recalculating costs when pricing changes
    - Detailed cost breakdown by component
    - Audit trail with calculation versioning
    """
    # OneToOne with Message (primary key pattern)
    message = models.OneToOneField(
        'claude_sessions.Message',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cost'
    )

    # Denormalized for fast queries (avoid joins)
    session = models.ForeignKey(
        'claude_sessions.Session',
        on_delete=models.CASCADE,
        related_name='message_costs'
    )

    # Pricing reference
    pricing_tier = models.ForeignKey(
        PricingTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='message_costs',
        help_text="Pricing used for calculation"
    )

    # Token counts (copied from TokenUsage for calculation record)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    cache_creation_tokens = models.IntegerField(default=0)
    cache_read_tokens = models.IntegerField(default=0)
    cache_ephemeral_5m_tokens = models.IntegerField(default=0)
    cache_ephemeral_1h_tokens = models.IntegerField(default=0)
    thinking_tokens = models.IntegerField(default=0)

    # Cost breakdown (in USD)
    input_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )
    output_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )
    cache_write_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )
    cache_read_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )
    cache_ephemeral_5m_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )
    cache_ephemeral_1h_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )
    thinking_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0')
    )

    # Context (denormalized for analytics)
    model = models.CharField(max_length=100, blank=True, db_index=True)
    service_tier = models.CharField(max_length=50, blank=True)
    message_timestamp = models.DateTimeField(db_index=True)
    is_batch = models.BooleanField(default=False)

    # Adjustments
    adjustment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('0'),
        help_text="Manual adjustment applied"
    )
    adjustment_reason = models.TextField(
        blank=True,
        help_text="Reason for adjustment"
    )

    # Calculation metadata
    calculation_version = models.IntegerField(
        default=1,
        help_text="Version of cost calculation algorithm"
    )
    calculated_at = models.DateTimeField(auto_now_add=True)
    recalculated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-message_timestamp']
        indexes = [
            models.Index(fields=['session', '-message_timestamp']),
            models.Index(fields=['model', '-message_timestamp']),
            models.Index(fields=['-total_cost']),
            models.Index(fields=['-calculated_at']),
        ]

    def __str__(self):
        return f"${self.total_cost} for {str(self.pk)[:8]}..."


class SessionCost(models.Model):
    """
    Pre-aggregated session cost totals for fast dashboard queries.

    Aggregates all MessageCost records for a session with breakdowns
    stored in related SessionCostByModel and SessionCostByTool records.
    """
    # OneToOne with Session (primary key pattern)
    session = models.OneToOneField(
        'claude_sessions.Session',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='cost'
    )

    # Token totals
    total_input_tokens = models.BigIntegerField(default=0)
    total_output_tokens = models.BigIntegerField(default=0)
    total_cache_write_tokens = models.BigIntegerField(default=0)
    total_cache_read_tokens = models.BigIntegerField(default=0)
    total_thinking_tokens = models.BigIntegerField(default=0)

    # Cost totals
    total_input_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_output_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_cache_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_thinking_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_adjustment = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0'),
        help_text="Sum of all adjustments"
    )
    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    adjusted_total = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0'),
        help_text="Total cost after adjustments"
    )

    # Counts
    message_count = models.IntegerField(default=0)
    billable_message_count = models.IntegerField(
        default=0,
        help_text="Messages with non-zero cost"
    )

    # Context (denormalized)
    primary_model = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Most-used model in session"
    )
    project_path = models.TextField(
        blank=True,
        help_text="Session working directory"
    )
    session_started_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )

    # Aggregation metadata
    is_complete = models.BooleanField(
        default=False,
        help_text="Session has ended and costs are final"
    )
    aggregated_at = models.DateTimeField(auto_now=True)
    message_cost_count = models.IntegerField(
        default=0,
        help_text="Number of MessageCost records aggregated"
    )

    class Meta:
        ordering = ['-total_cost']
        indexes = [
            models.Index(fields=['-total_cost']),
            models.Index(fields=['primary_model', '-total_cost']),
            models.Index(fields=['is_complete', '-aggregated_at']),
            models.Index(fields=['-session_started_at']),
        ]

    def __str__(self):
        return f"${self.total_cost} for session {str(self.pk)[:8]}..."


class SessionCostByModel(models.Model):
    """
    Session cost breakdown by model.

    Enables analysis of multi-model sessions (e.g., Opus for complex tasks,
    Haiku for simple queries) and cost attribution per model.
    """
    session_cost = models.ForeignKey(
        SessionCost,
        on_delete=models.CASCADE,
        related_name='by_model'
    )
    session = models.ForeignKey(
        'claude_sessions.Session',
        on_delete=models.CASCADE,
        related_name='cost_by_model'
    )

    model = models.CharField(max_length=100, db_index=True)

    # Token counts
    input_tokens = models.BigIntegerField(default=0)
    output_tokens = models.BigIntegerField(default=0)
    cache_tokens = models.BigIntegerField(default=0)
    thinking_tokens = models.BigIntegerField(default=0)

    # Costs
    input_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    output_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    cache_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    thinking_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )

    message_count = models.IntegerField(default=0)

    class Meta:
        unique_together = [['session_cost', 'model']]
        ordering = ['-total_cost']
        indexes = [
            models.Index(fields=['session', 'model']),
            models.Index(fields=['model', '-total_cost']),
        ]

    def __str__(self):
        return f"{self.model}: ${self.total_cost}"


class SessionCostByTool(models.Model):
    """
    Session cost breakdown by tool usage.

    Attributes costs to tools by analyzing messages containing tool invocations.
    Helps identify expensive tools (e.g., WebSearch at $10/1000 searches).
    """
    session_cost = models.ForeignKey(
        SessionCost,
        on_delete=models.CASCADE,
        related_name='by_tool'
    )
    session = models.ForeignKey(
        'claude_sessions.Session',
        on_delete=models.CASCADE,
        related_name='cost_by_tool'
    )

    tool_name = models.CharField(max_length=100, db_index=True)

    # Tokens attributed to this tool
    input_tokens = models.BigIntegerField(default=0)
    output_tokens = models.BigIntegerField(default=0)

    # Costs
    input_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    output_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )

    # Usage counts
    tool_use_count = models.IntegerField(default=0)
    message_count = models.IntegerField(default=0)

    class Meta:
        unique_together = [['session_cost', 'tool_name']]
        ordering = ['-total_cost']
        indexes = [
            models.Index(fields=['session', 'tool_name']),
            models.Index(fields=['tool_name', '-total_cost']),
        ]

    def __str__(self):
        return f"{self.tool_name}: ${self.total_cost} ({self.tool_use_count} uses)"


class DailyCost(models.Model):
    """
    Daily cost aggregation with dimensional rollups.

    Supports fast dashboard queries with pre-computed totals by date and dimensions.
    Dimensions: project_path, model, user_type (blank = "all values")
    """
    # Composite natural key: date + dimensions
    date = models.DateField(db_index=True)
    project_path = models.TextField(
        blank=True,
        help_text="Empty = all projects"
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        help_text="Empty = all models"
    )
    user_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="Empty = all user types"
    )

    # Token totals
    total_input_tokens = models.BigIntegerField(default=0)
    total_output_tokens = models.BigIntegerField(default=0)
    total_cache_write_tokens = models.BigIntegerField(default=0)
    total_cache_read_tokens = models.BigIntegerField(default=0)
    total_thinking_tokens = models.BigIntegerField(default=0)

    # Cost totals
    total_input_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_output_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_cache_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_thinking_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )

    # Counts
    session_count = models.IntegerField(default=0)
    message_count = models.IntegerField(default=0)
    unique_project_count = models.IntegerField(
        default=0,
        help_text="Only for all-projects rollup"
    )

    # Aggregation metadata
    aggregated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['date', 'project_path', 'model', 'user_type']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date', 'project_path']),
            models.Index(fields=['-date', 'model']),
            models.Index(fields=['-date', 'user_type']),
            models.Index(fields=['-total_cost']),
        ]

    def __str__(self):
        dims = []
        if self.project_path:
            dims.append(f"project={self.project_path[:20]}")
        if self.model:
            dims.append(f"model={self.model}")
        if self.user_type:
            dims.append(f"user={self.user_type}")
        dim_str = ', '.join(dims) if dims else 'all'
        return f"{self.date} ({dim_str}): ${self.total_cost}"


class RateLimit(models.Model):
    """
    Rate limit configuration for usage budgets.

    Supports multiple limit types (tokens, requests, cost) and scopes
    (global, user, project, model) with effective dating.
    """
    SCOPE_CHOICES = [
        ('global', 'Global'),
        ('user', 'User'),
        ('project', 'Project'),
        ('model', 'Model'),
    ]
    LIMIT_TYPE_CHOICES = [
        ('tokens', 'Tokens'),
        ('input_tokens', 'Input Tokens'),
        ('output_tokens', 'Output Tokens'),
        ('requests', 'Requests'),
        ('cost', 'Cost (USD)'),
    ]
    PERIOD_CHOICES = [
        ('minute', 'Per Minute'),
        ('hour', 'Per Hour'),
        ('day', 'Per Day'),
        ('month', 'Per Month'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Scope
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, db_index=True)
    scope_value = models.CharField(
        max_length=200,
        blank=True,
        help_text="Specific value for scope (e.g., project path, model name)"
    )

    # Limit specification
    limit_type = models.CharField(max_length=20, choices=LIMIT_TYPE_CHOICES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    limit_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Maximum value for the period"
    )

    # Behavior
    is_active = models.BooleanField(default=True, db_index=True)
    is_hard_limit = models.BooleanField(
        default=False,
        help_text="If True, block requests when exceeded"
    )
    alert_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.80'),
        help_text="Percentage at which to trigger alert (0.80 = 80%)"
    )

    # Effective dating
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scope', 'name']
        indexes = [
            models.Index(fields=['scope', 'scope_value', 'is_active']),
            models.Index(fields=['limit_type', 'period']),
        ]

    def __str__(self):
        return f"{self.name}: {self.limit_value} {self.limit_type}/{self.period}"


class RateLimitUsage(models.Model):
    """
    Rate limit consumption tracking per period.

    Tracks current consumption against rate limits for alert
    triggering and limit enforcement.
    """
    rate_limit = models.ForeignKey(
        RateLimit,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )

    # Period
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField()

    # Scope value (for user/project/model scoped limits)
    scope_value = models.CharField(
        max_length=200,
        blank=True,
        help_text="Actual scope value for this usage record"
    )

    # Consumption
    consumed_value = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )
    consumed_input_tokens = models.BigIntegerField(default=0)
    consumed_output_tokens = models.BigIntegerField(default=0)
    consumed_requests = models.IntegerField(default=0)
    consumed_cost = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        default=Decimal('0')
    )

    # Status
    alert_triggered = models.BooleanField(default=False)
    alert_triggered_at = models.DateTimeField(null=True, blank=True)
    limit_exceeded = models.BooleanField(default=False)
    limit_exceeded_at = models.DateTimeField(null=True, blank=True)

    message_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['rate_limit', 'period_start', 'scope_value']]
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['rate_limit', '-period_start']),
            models.Index(fields=['limit_exceeded', '-period_start']),
            models.Index(fields=['alert_triggered', '-period_start']),
        ]

    @property
    def utilization_percent(self):
        """Calculate current utilization as a percentage."""
        if self.rate_limit.limit_value == 0:
            return Decimal('0')
        return (self.consumed_value / self.rate_limit.limit_value) * 100

    def __str__(self):
        return f"{self.rate_limit.name}: {self.consumed_value}/{self.rate_limit.limit_value}"


class CostAdjustment(models.Model):
    """
    Manual cost adjustments for credits, refunds, and corrections.

    Provides complete audit trail with optional approval workflow.
    """
    ADJUSTMENT_TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('refund', 'Refund'),
        ('correction', 'Correction'),
        ('discount', 'Discount'),
        ('promo', 'Promotional'),
    ]

    # Scope (optional - can be global)
    session = models.ForeignKey(
        'claude_sessions.Session',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cost_adjustments'
    )
    message = models.ForeignKey(
        'claude_sessions.Message',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cost_adjustments'
    )

    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPE_CHOICES,
        db_index=True
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=6,
        help_text="Positive = credit, Negative = debit"
    )

    # Audit
    reason = models.TextField()
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference (ticket, invoice, etc.)"
    )
    adjusted_by = models.CharField(
        max_length=100,
        blank=True,
        help_text="User who made the adjustment"
    )

    # Approval workflow
    requires_approval = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    approved_by = models.CharField(max_length=100, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    # Application status
    is_applied = models.BooleanField(
        default=False,
        help_text="Has this been applied to costs?"
    )
    applied_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', '-created_at']),
            models.Index(fields=['adjustment_type', '-created_at']),
            models.Index(fields=['is_applied', '-created_at']),
            models.Index(fields=['requires_approval', 'is_approved']),
        ]

    def __str__(self):
        scope = f"session {str(self.session_id)[:8]}" if self.session_id else "global"
        return f"{self.adjustment_type}: ${self.amount} ({scope})"
