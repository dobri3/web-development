from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, WatchlistViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')
router.register(r"subscription", SubscriptionViewSet, basename="subscription")

urlpatterns = router.urls