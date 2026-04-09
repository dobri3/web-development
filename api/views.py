from rest_framework import mixins, viewsets, permissions, filters, status
from rest_framework.response import Response

from domain.models import Movie, Watchlist
from services.watchlist_service import add_to_watchlist, remove_from_watchlist
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
            .select_related("movie")
            .order_by("-added_at")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movie = serializer.validated_data["movie"]

        watchlist_item = add_to_watchlist(
            user=request.user,
            movie_id=movie.id,
        )

        output_serializer = self.get_serializer(watchlist_item)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        watchlist_item = self.get_object()

        remove_from_watchlist(
            user=request.user,
            movie_id=watchlist_item.movie_id,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)