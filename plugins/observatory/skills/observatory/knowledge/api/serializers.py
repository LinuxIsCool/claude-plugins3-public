"""
Serializers for Knowledge Graph models.
"""
from rest_framework import serializers
from knowledge.models import Resource, Edge, Content, Embedding


class ResourceSerializer(serializers.ModelSerializer):
    """Resource serializer with computed fields."""
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ['id', 'discovered_at']

    def get_children_count(self, obj):
        return obj.children.count()


class ResourceDetailSerializer(serializers.ModelSerializer):
    """Resource with nested content and edges."""
    content = serializers.SerializerMethodField()
    outgoing_edges = serializers.SerializerMethodField()
    incoming_edges = serializers.SerializerMethodField()
    embeddings_count = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = '__all__'

    def get_content(self, obj):
        try:
            return ContentSerializer(obj.content).data
        except Content.DoesNotExist:
            return None

    def get_outgoing_edges(self, obj):
        edges = obj.outgoing_edges.select_related('target')[:20]
        return EdgeSerializer(edges, many=True).data

    def get_incoming_edges(self, obj):
        edges = obj.incoming_edges.select_related('source')[:20]
        return EdgeSerializer(edges, many=True).data

    def get_embeddings_count(self, obj):
        return obj.embeddings.count()


class EdgeSerializer(serializers.ModelSerializer):
    """Edge serializer."""
    source_url = serializers.CharField(source='source.url', read_only=True)
    target_url = serializers.CharField(source='target.url', read_only=True)

    class Meta:
        model = Edge
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    """Content serializer."""
    resource_url = serializers.CharField(source='resource.url', read_only=True)

    class Meta:
        model = Content
        fields = '__all__'


class EmbeddingSerializer(serializers.ModelSerializer):
    """Embedding serializer (without vector data for list views)."""
    resource_url = serializers.CharField(source='resource.url', read_only=True)

    class Meta:
        model = Embedding
        fields = ['id', 'resource', 'resource_url', 'embedding_type', 'model', 'created_at']


class EmbeddingDetailSerializer(serializers.ModelSerializer):
    """Embedding with vector data."""
    resource_url = serializers.CharField(source='resource.url', read_only=True)
    vector_dimensions = serializers.SerializerMethodField()

    class Meta:
        model = Embedding
        fields = '__all__'

    def get_vector_dimensions(self, obj):
        if hasattr(obj, 'embedding') and obj.embedding is not None:
            return len(obj.embedding)
        if hasattr(obj, 'embedding_json') and obj.embedding_json is not None:
            return len(obj.embedding_json)
        return None


class GraphStatsSerializer(serializers.Serializer):
    """Serializer for graph statistics."""
    total_resources = serializers.IntegerField()
    total_edges = serializers.IntegerField()
    total_content = serializers.IntegerField()
    total_embeddings = serializers.IntegerField()
    status_counts = serializers.DictField()
    source_type_counts = serializers.DictField()
    edge_type_counts = serializers.DictField()
