"""
Knowledge Graph Models - 4 models for documentation crawling and semantic search.

Features:
- Resources: URLs with status tracking and priority scoring
- Edges: Graph relationships between resources
- Content: Extracted markdown, text, and metadata
- Embedding: Vector embeddings for semantic search (pgvector)
"""
import hashlib
from django.db import models

# Try to import pgvector, fall back gracefully
try:
    from pgvector.django import VectorField, HalfVectorField
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    VectorField = None
    HalfVectorField = None


def generate_resource_id(url: str) -> str:
    """Generate a deterministic ID from URL using SHA-256."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]


class Resource(models.Model):
    """
    Resources in the knowledge graph.

    Each resource represents a URL that can be crawled and processed.
    Uses URL-based hash IDs for deterministic identification.
    """
    STATUS_CHOICES = [
        ('seed', 'Seed'),
        ('queued', 'Queued'),
        ('fetched', 'Fetched'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('stale', 'Stale'),
    ]
    SOURCE_TYPE_CHOICES = [
        ('github_repo', 'GitHub Repository'),
        ('github_issue', 'GitHub Issue'),
        ('github_user', 'GitHub User'),
        ('github_file', 'GitHub File'),
        ('documentation', 'Documentation'),
        ('blog_post', 'Blog Post'),
        ('reddit_subreddit', 'Reddit Subreddit'),
        ('reddit_post', 'Reddit Post'),
        ('youtube_channel', 'YouTube Channel'),
        ('youtube_video', 'YouTube Video'),
        ('changelog_entry', 'Changelog Entry'),
        ('api_reference', 'API Reference'),
        ('other', 'Other'),
    ]

    id = models.CharField(
        max_length=16, primary_key=True,
        help_text="SHA-256 hash of URL (first 16 chars)"
    )
    url = models.URLField(max_length=2000, unique=True, db_index=True)
    canonical_url = models.URLField(max_length=2000, blank=True)
    source_type = models.CharField(max_length=30, choices=SOURCE_TYPE_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued', db_index=True)

    # Priority system
    priority = models.FloatField(default=0.5, db_index=True, help_text="0.0 to 1.0, higher = more important")
    priority_reasoning = models.TextField(blank=True)
    priority_computed_at = models.DateTimeField(null=True, blank=True)

    # Graph position
    depth = models.IntegerField(default=0, db_index=True, help_text="Distance from seed resources")
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children',
        help_text="Resource this was discovered from"
    )

    # Timestamps
    discovered_at = models.DateTimeField(auto_now_add=True)
    fetched_at = models.DateTimeField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Content tracking
    content_hash = models.CharField(max_length=64, blank=True, help_text="Hash of fetched content for change detection")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-priority', '-discovered_at']
        indexes = [
            models.Index(fields=['status', '-priority']),
            models.Index(fields=['source_type', 'status']),
            models.Index(fields=['depth', 'status']),
        ]

    def save(self, *args, **kwargs):
        # Auto-generate ID from URL if not set
        if not self.id:
            self.id = generate_resource_id(self.url)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.source_type}] {self.url[:60]}..."


class Edge(models.Model):
    """
    Edges (relationships) between resources in the knowledge graph.

    Examples:
    - links_to: A page links to another page
    - mentioned_in: A resource is mentioned in another
    - related_to: Semantic relationship
    - depends_on: Code dependency
    """
    EDGE_TYPE_CHOICES = [
        ('links_to', 'Links To'),
        ('mentioned_in', 'Mentioned In'),
        ('related_to', 'Related To'),
        ('depends_on', 'Depends On'),
        ('authored_by', 'Authored By'),
        ('belongs_to', 'Belongs To'),
        ('references', 'References'),
    ]

    source = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='outgoing_edges')
    target = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='incoming_edges')
    edge_type = models.CharField(max_length=30, choices=EDGE_TYPE_CHOICES, db_index=True)
    context = models.TextField(blank=True, help_text="Context where relationship was found")
    discovered_at = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField(default=1.0, help_text="Confidence score 0.0-1.0")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['source', 'target', 'edge_type']
        ordering = ['-discovered_at']
        indexes = [
            models.Index(fields=['source', 'edge_type']),
            models.Index(fields=['target', 'edge_type']),
        ]

    def __str__(self):
        return f"{self.source_id} --[{self.edge_type}]--> {self.target_id}"


class Content(models.Model):
    """
    Extracted content from resources.

    Stores markdown, plain text, and extracted metadata for each processed resource.
    """
    resource = models.OneToOneField(Resource, on_delete=models.CASCADE, primary_key=True, related_name='content')
    markdown = models.TextField(blank=True, help_text="Original or converted markdown")
    extracted_text = models.TextField(blank=True, help_text="Plain text for search/embedding")
    summary = models.TextField(blank=True, help_text="AI-generated summary")

    # Extracted metadata
    title = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    last_modified_at = models.DateTimeField(null=True, blank=True)

    # Structured data
    extracted_links = models.JSONField(default=list, blank=True, help_text="URLs found in content")
    code_examples = models.JSONField(default=list, blank=True, help_text="Code blocks extracted")
    headings = models.JSONField(default=list, blank=True, help_text="Document structure")
    metadata = models.JSONField(default=dict, blank=True)

    # Versioning
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Contents'

    def __str__(self):
        return f"Content for {self.resource_id}"


# Embedding model with pgvector support
if PGVECTOR_AVAILABLE:
    class Embedding(models.Model):
        """
        Vector embeddings for semantic search using pgvector.

        Supports multiple embedding types:
        - full: Full precision float32 (1536 dims for OpenAI, 384 for all-MiniLM)
        - half: Half precision float16 for memory efficiency
        - sparse: Sparse vectors for hybrid search
        """
        EMBEDDING_TYPE_CHOICES = [
            ('content', 'Content Embedding'),
            ('summary', 'Summary Embedding'),
            ('title', 'Title Embedding'),
            ('code', 'Code Embedding'),
        ]
        MODEL_CHOICES = [
            ('text-embedding-3-small', 'OpenAI text-embedding-3-small (1536d)'),
            ('text-embedding-3-large', 'OpenAI text-embedding-3-large (3072d)'),
            ('all-MiniLM-L6-v2', 'all-MiniLM-L6-v2 (384d)'),
            ('voyage-code-2', 'Voyage Code 2 (1024d)'),
        ]

        resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='embeddings')
        embedding_type = models.CharField(max_length=20, choices=EMBEDDING_TYPE_CHOICES, db_index=True)
        model = models.CharField(max_length=50, choices=MODEL_CHOICES)

        # Vector storage (dimensions depend on model)
        # Using 384 as default for all-MiniLM-L6-v2 (lightweight, fast)
        embedding = VectorField(dimensions=384, null=True, blank=True)
        embedding_half = HalfVectorField(dimensions=384, null=True, blank=True)

        # Metadata
        created_at = models.DateTimeField(auto_now_add=True)
        metadata = models.JSONField(default=dict, blank=True)

        class Meta:
            unique_together = ['resource', 'embedding_type', 'model']
            indexes = [
                models.Index(fields=['embedding_type', 'model']),
            ]

        def __str__(self):
            return f"{self.embedding_type} embedding for {self.resource_id}"

else:
    # Fallback model without vector fields (for SQLite)
    class Embedding(models.Model):
        """
        Embedding storage (without pgvector).

        Note: pgvector is not available. Install psycopg and pgvector packages
        and use PostgreSQL for vector search capabilities.
        """
        EMBEDDING_TYPE_CHOICES = [
            ('content', 'Content Embedding'),
            ('summary', 'Summary Embedding'),
            ('title', 'Title Embedding'),
            ('code', 'Code Embedding'),
        ]
        MODEL_CHOICES = [
            ('text-embedding-3-small', 'OpenAI text-embedding-3-small (1536d)'),
            ('text-embedding-3-large', 'OpenAI text-embedding-3-large (3072d)'),
            ('all-MiniLM-L6-v2', 'all-MiniLM-L6-v2 (384d)'),
            ('voyage-code-2', 'Voyage Code 2 (1024d)'),
        ]

        resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='embeddings')
        embedding_type = models.CharField(max_length=20, choices=EMBEDDING_TYPE_CHOICES, db_index=True)
        model = models.CharField(max_length=50, choices=MODEL_CHOICES)

        # Fallback: Store as JSON (no vector operations)
        embedding_json = models.JSONField(null=True, blank=True, help_text="Vector stored as JSON array (no pgvector)")

        created_at = models.DateTimeField(auto_now_add=True)
        metadata = models.JSONField(default=dict, blank=True)

        class Meta:
            unique_together = ['resource', 'embedding_type', 'model']

        def __str__(self):
            return f"{self.embedding_type} embedding for {self.resource_id} (no pgvector)"
