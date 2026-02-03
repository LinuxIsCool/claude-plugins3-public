"""
ViewSets for Knowledge Graph models.

Provides CRUD + semantic search + graph traversal.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from knowledge.models import Resource, Edge, Content, Embedding
from . import serializers


class ResourceViewSet(viewsets.ModelViewSet):
    """
    Resource ViewSet with graph operations.
    """
    queryset = Resource.objects.all()
    serializer_class = serializers.ResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source_type', 'depth']
    search_fields = ['url', 'canonical_url']
    ordering_fields = ['priority', 'discovered_at', 'fetched_at', 'depth']
    ordering = ['-priority', '-discovered_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.ResourceDetailSerializer
        return serializers.ResourceSerializer

    @action(detail=False, methods=['get'])
    def queue(self, request):
        """Get prioritized queue of resources to process."""
        status_filter = request.query_params.get('status', 'queued')
        limit = min(int(request.query_params.get('limit', 50)), 200)

        resources = self.get_queryset().filter(
            status=status_filter
        ).order_by('-priority', 'discovered_at')[:limit]

        return Response(serializers.ResourceSerializer(resources, many=True).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get knowledge graph statistics."""
        qs = self.get_queryset()

        # Status counts
        status_counts = dict(qs.values('status').annotate(count=Count('id')).values_list('status', 'count'))

        # Source type counts
        source_counts = dict(qs.values('source_type').annotate(count=Count('id')).values_list('source_type', 'count'))

        # Edge type counts
        edge_counts = dict(Edge.objects.values('edge_type').annotate(count=Count('id')).values_list('edge_type', 'count'))

        return Response(serializers.GraphStatsSerializer({
            'total_resources': qs.count(),
            'total_edges': Edge.objects.count(),
            'total_content': Content.objects.count(),
            'total_embeddings': Embedding.objects.count(),
            'status_counts': status_counts,
            'source_type_counts': source_counts,
            'edge_type_counts': edge_counts,
        }).data)

    @action(detail=False, methods=['get'])
    def hubs(self, request):
        """Get most-connected resources (hubs)."""
        limit = min(int(request.query_params.get('limit', 20)), 100)

        # Resources with most incoming edges
        hubs = self.get_queryset().annotate(
            incoming_count=Count('incoming_edges'),
            outgoing_count=Count('outgoing_edges'),
        ).order_by('-incoming_count')[:limit]

        data = []
        for r in hubs:
            data.append({
                'id': r.id,
                'url': r.url,
                'source_type': r.source_type,
                'incoming_edges': r.incoming_count,
                'outgoing_edges': r.outgoing_count,
            })

        return Response(data)

    @action(detail=True, methods=['get'])
    def graph(self, request, pk=None):
        """Get local graph neighborhood for a resource."""
        resource = self.get_object()
        depth = min(int(request.query_params.get('depth', 1)), 3)

        # Get nodes in neighborhood
        nodes = {resource.id: serializers.ResourceSerializer(resource).data}
        edges = []
        seen_edges = set()  # Track (source, target, type) to avoid duplicates

        # BFS to collect neighborhood - batch queries per depth level
        frontier = set([resource.id])
        for d in range(depth):
            if not frontier:
                break

            # Batch fetch ALL outgoing edges for current frontier
            outgoing_edges = Edge.objects.filter(
                source_id__in=frontier
            ).select_related('target')

            # Batch fetch ALL incoming edges for current frontier
            incoming_edges = Edge.objects.filter(
                target_id__in=frontier
            ).select_related('source')

            next_frontier = set()

            # Process outgoing edges
            for edge in outgoing_edges:
                edge_key = (edge.source_id, edge.target_id, edge.edge_type)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append(serializers.EdgeSerializer(edge).data)
                    if edge.target_id not in nodes:
                        nodes[edge.target_id] = serializers.ResourceSerializer(edge.target).data
                        next_frontier.add(edge.target_id)

            # Process incoming edges
            for edge in incoming_edges:
                edge_key = (edge.source_id, edge.target_id, edge.edge_type)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    edges.append(serializers.EdgeSerializer(edge).data)
                    if edge.source_id not in nodes:
                        nodes[edge.source_id] = serializers.ResourceSerializer(edge.source).data
                        next_frontier.add(edge.source_id)

            frontier = next_frontier

        return Response({
            'center': pk,
            'depth': depth,
            'nodes': list(nodes.values()),
            'edges': edges,
        })

    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search resources by content."""
        query = request.data.get('q', '')
        source_types = request.data.get('source_types', [])
        statuses = request.data.get('statuses', ['processed'])
        limit = min(int(request.data.get('limit', 50)), 200)

        # Search in content
        content_matches = Content.objects.filter(
            Q(extracted_text__icontains=query) |
            Q(summary__icontains=query) |
            Q(title__icontains=query)
        )

        if source_types:
            content_matches = content_matches.filter(resource__source_type__in=source_types)
        if statuses:
            content_matches = content_matches.filter(resource__status__in=statuses)

        content_matches = content_matches.select_related('resource')[:limit]

        results = []
        for content in content_matches:
            results.append({
                'resource': serializers.ResourceSerializer(content.resource).data,
                'title': content.title,
                'summary': content.summary[:300] if content.summary else None,
                'match_context': self._extract_context(content.extracted_text, query),
            })

        return Response({
            'query': query,
            'count': len(results),
            'results': results,
        })

    def _extract_context(self, text, query, context_chars=150):
        """Extract text context around query match."""
        if not text or not query:
            return None
        query_lower = query.lower()
        text_lower = text.lower()
        pos = text_lower.find(query_lower)
        if pos == -1:
            return text[:context_chars] + '...' if len(text) > context_chars else text
        start = max(0, pos - context_chars // 2)
        end = min(len(text), pos + len(query) + context_chars // 2)
        context = text[start:end]
        if start > 0:
            context = '...' + context
        if end < len(text):
            context = context + '...'
        return context


class EdgeViewSet(viewsets.ModelViewSet):
    """Edge ViewSet."""
    queryset = Edge.objects.select_related('source', 'target').all()
    serializer_class = serializers.EdgeSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['edge_type', 'source', 'target']
    ordering_fields = ['discovered_at', 'confidence']
    ordering = ['-discovered_at']

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get edges grouped by type."""
        edge_type = request.query_params.get('type')
        limit = min(int(request.query_params.get('limit', 50)), 200)

        qs = self.get_queryset()
        if edge_type:
            qs = qs.filter(edge_type=edge_type)

        return Response(serializers.EdgeSerializer(qs[:limit], many=True).data)


class ContentViewSet(viewsets.ModelViewSet):
    """Content ViewSet."""
    queryset = Content.objects.select_related('resource').all()
    serializer_class = serializers.ContentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource__status', 'resource__source_type']
    search_fields = ['title', 'extracted_text', 'summary']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    @action(detail=False, methods=['post'])
    def full_text_search(self, request):
        """Full-text search across all content."""
        query = request.data.get('q', '')
        limit = min(int(request.data.get('limit', 50)), 200)

        results = self.get_queryset().filter(
            Q(extracted_text__icontains=query) |
            Q(summary__icontains=query) |
            Q(title__icontains=query)
        )[:limit]

        return Response(serializers.ContentSerializer(results, many=True).data)


class EmbeddingViewSet(viewsets.ModelViewSet):
    """Embedding ViewSet with semantic search."""
    queryset = Embedding.objects.select_related('resource').all()
    serializer_class = serializers.EmbeddingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['embedding_type', 'model', 'resource']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.EmbeddingDetailSerializer
        return serializers.EmbeddingSerializer

    @action(detail=False, methods=['post'])
    def semantic_search(self, request):
        """
        Semantic similarity search using pgvector.

        Requires:
        - query_embedding: List of floats (same dimensions as stored embeddings)
        - embedding_type: Type of embedding to search
        - limit: Max results (default 10)
        """
        query_embedding = request.data.get('query_embedding')
        embedding_type = request.data.get('embedding_type', 'content')
        limit = min(int(request.data.get('limit', 10)), 50)

        if not query_embedding:
            return Response(
                {'error': 'query_embedding is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if pgvector is available
        from knowledge.models import PGVECTOR_AVAILABLE
        if not PGVECTOR_AVAILABLE:
            return Response(
                {'error': 'pgvector is not available. Use PostgreSQL with pgvector extension.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )

        # Perform vector similarity search
        from pgvector.django import L2Distance

        results = Embedding.objects.filter(
            embedding_type=embedding_type
        ).annotate(
            distance=L2Distance('embedding', query_embedding)
        ).order_by('distance')[:limit]

        data = []
        for emb in results:
            data.append({
                'resource_id': emb.resource_id,
                'resource_url': emb.resource.url if emb.resource else None,
                'embedding_type': emb.embedding_type,
                'model': emb.model,
                'distance': float(emb.distance),
                'similarity': 1.0 / (1.0 + float(emb.distance)),  # Convert distance to similarity
            })

        return Response({
            'embedding_type': embedding_type,
            'count': len(data),
            'results': data,
        })
