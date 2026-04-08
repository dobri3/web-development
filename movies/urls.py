from rest_framework.routers import DefaultRouter
from api.views import MovieViewSet, WatchlistViewSet

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movies')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = router.urls