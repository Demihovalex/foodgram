from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvatarView,
    CurrentUserView,
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionsView,
    SubscriptionView,
    TagViewSet,
    UserDetailView,
)

router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("users/me/", CurrentUserView.as_view(), name="current_user"),
    path("users/me/avatar/", AvatarView.as_view(), name="avatar"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user_detail"),
    path(
        "users/<int:user_id>/subscribe/",
        SubscriptionView.as_view(),
        name="subscribe",
    ),
    path("users/subscriptions/", SubscriptionsView.as_view(),
         name="subscriptions"),
]
