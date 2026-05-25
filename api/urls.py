from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import MovieViewSet, WatchlistViewSet, SubscriptionView

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')

urlpatterns = router.urls + [
    path("subscription/", SubscriptionView.as_view(), name="subscription"),
]