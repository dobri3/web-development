from rest_framework import mixins, viewsets, permissions, filters
from .models import Movie, Watchlist
from .serializers import MovieSerializer, WatchlistSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all().order_by("id")
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "genres__name"]
    ordering_fields = ["title", "release_year"]
    ordering = ["title"]

    def get_queryset(self):
        queryset = super().get_queryset()

        genre = self.request.query_params.get("genre")
        release_year = self.request.query_params.get("release_year")

        if genre:
            queryset = queryset.filter(genres__name__icontains=genre)

        if release_year:
            queryset = queryset.filter(release_year=release_year)

        return queryset.distinct()


class WatchlistViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Watchlist.objects
            .filter(user=self.request.user)
            .order_by("-added_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)