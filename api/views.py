from rest_framework import mixins, viewsets, permissions, filters, status, generics
from rest_framework.response import Response

from rest_framework.decorators import action

from domain.models import Movie, Watchlist
from services.watchlist_service import add_to_watchlist, remove_from_watchlist
from .serializers import (
    MovieSerializer,
    MovieFilterSerializer,
    WatchlistSerializer, 
    SubscriptionSerializer,
)
from services.movie_service import get_movie, get_movies

from services.subscription_service import (
    create_or_extend_subscription,
    cancel_subscription,
    get_user_active_subscription,
    get_user_subscription,
)

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

    def retrieve(self, request, *args, **kwargs):
        movie = get_movie(kwargs["pk"])

        serializer = self.get_serializer(movie)
        return Response(serializer.data)

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
    

class SubscriptionViewSet(viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        subscription = get_user_subscription(request.user)

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        subscription = create_or_extend_subscription(request.user)

        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def active(self, request, *args, **kwargs):
        subscription = get_user_active_subscription(request.user)

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def cancel(self, request, *args, **kwargs):
        subscription = cancel_subscription(request.user)

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
