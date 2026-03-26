from rest_framework import serializers
from .models import Movie, Genre, Watchlist


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']
        read_only_fields = ['id']


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_year', 'genres']
        read_only_fields = ['id']



class WatchlistSerializer(serializers.ModelSerializer):
    movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all()) # Будет показывать ID, а не весь класс
    user = serializers.ReadOnlyField(source='user.username') # Будет показывать имя пользователя
    """Надо будет подкорректировать обращение к имени пользователя, когда создадим класс пользователя"""
    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'added_at']
        read_only_fields = ['id', 'user', 'added_at']