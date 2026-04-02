from rest_framework.routers import DefaultRouter
from rest_framework.urls import urlpatterns

from .views import MovieViewSet, WatchlistViewSet

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = router.urls