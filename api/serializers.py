from rest_framework import serializers
from domain.models import Movie, Genre, Watchlist


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
        fields = ['title', 'description', 'release_year', 'genres']
        read_only_fields = ['release_year']



class WatchlistSerializer(serializers.ModelSerializer):
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all()) # Будет показывать ID, а не весь класс
    user = serializers.ReadOnlyField(source='user.username') # Будет показывать имя пользователя
    """Надо будет подкорректировать обращение к имени пользователя, когда создадим класс пользователя"""
    class Meta:
        model = Watchlist
        fields = ['user', 'movie', 'added_at']
        read_only_fields = ['user', 'added_at']


