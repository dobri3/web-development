from django.contrib import admin

from domain.models import Genre, Movie, Subscription, Watchlist


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "release_year")
    search_fields = ("title", "description", "genres__name")
    list_filter = ("release_year", "genres")
    filter_horizontal = ("genres",)
    ordering = ("title",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "expires_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("expires_at",)
    ordering = ("-expires_at",)


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "movie", "added_at")
    search_fields = ("user__username", "user__email", "movie__title")
    list_filter = ("added_at",)
    ordering = ("-added_at",)