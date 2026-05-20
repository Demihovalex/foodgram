from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentUserView,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionsView,
    SubscriptionView,
    TagViewSet,
)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', CurrentUserView.as_view(), name='current_user'),
    path('users/<int:user_id>/subscribe/',
         SubscriptionView.as_view(), name='subscribe'),
    path('users/subscriptions/', SubscriptionsView.as_view(),
         name='subscriptions'),
]
