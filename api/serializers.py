from rest_framework import serializers
from domain.models import Movie, Genre, Watchlist, Subscription


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_year', 'genres']


# сериализатор для проверки query_params
class MovieFilterSerializer(serializers.Serializer):
    genre = serializers.CharField(required=False)
    release_year = serializers.IntegerField(required=False)

class WatchlistSerializer(serializers.ModelSerializer):
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all()) # Будет показывать ID, а не весь класс
    user = serializers.ReadOnlyField(source='user.username') # Будет показывать имя пользователя
    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'added_at']
        read_only_fields = ['user', 'added_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['expires_at']
        read_only_fields = ['expires_at']
