from django.contrib import admin
from ..domain.models import Movie, Genre, Subscription, Watchlist

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Subscription)
admin.site.register(Watchlist)
