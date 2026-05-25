from rest_framework import mixins, viewsets, permissions, filters, status, generics
from rest_framework.response import Response

from domain.models import Movie, Watchlist, Subscription
from services.watchlist_service import add_to_watchlist, remove_from_watchlist
from services.subscription_service import get_user_subscription
from .serializers import (
    MovieSerializer,
    MovieFilterSerializer,
    WatchlistSerializer, 
    SubscriptionSerializer,
)
from services.movie_service import get_movies

from django.shortcuts import get_object_or_404

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all().order_by("id")
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]

    # Настройка query_params: ?search= и ?ordering=
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "genres__name"]
    ordering_fields = ["title", "release_year"]
    ordering = ["title"]

    def get_queryset(self):
        serializer = MovieFilterSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        return get_movies(serializer.validated_data)


class WatchlistViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    # queryset состоит из всех объектов watchlist, которыми
    # обладает автор запроса в порядке, начиная с 
    # недавно добавленных фильмов
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
    
class SubscriptionView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_user_subscription(user=self.request.user)