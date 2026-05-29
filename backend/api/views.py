from io import BytesIO

from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserCreateSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.filters import RecipeFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import CustomUser, Subscription


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserSerializer
    create_serializer_class = UserCreateSerializer
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(["get"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(["get"], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(
            following__user=request.user
        ).annotate(
            recipes_count=Count('recipes')
        ).prefetch_related('recipes')
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, many=True,
                                            context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(["post", "delete"], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(CustomUser, pk=id)
        if request.method == "POST":
            serializer = SubscribeSerializer(data={
                'user': request.user.id,
                'author': author.id
            })
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, author=author)
            serializer = SubscriptionSerializer(author,
                                                context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # DELETE
        deleted, _ = Subscription.objects.filter(user=request.user,
                                                 author=author).delete()
        if not deleted:
            return Response({"errors": "Вы не были подписаны"}, status=400)
        return Response(status=204)

    @action(["put", "delete"], detail=False, url_path="me/avatar",
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user
        if request.method == "PUT":
            if "avatar" not in request.data:
                return Response(
                    {"errors": "Поле avatar обязательно"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = AvatarSerializer(user, data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # DELETE
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(f"/recipes/{recipe.id}/")
        return Response({"short-link": short_link})

    def _add_to_relation(self, model, recipe, serializer_class):
        obj, created = model.objects.get_or_create(user=self.request.user,
                                                   recipe=recipe)
        if not created:
            return False, None
        return True, serializer_class(recipe).data

    def _remove_from_relation(self, model, recipe):
        deleted, _ = model.objects.filter(user=self.request.user,
                                          recipe=recipe).delete()
        return deleted

    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            created, data = self._add_to_relation(Favorite, recipe,
                                                  ShortRecipeSerializer)
            if not created:
                return Response({"errors": "Рецепт уже в избранном"},
                                status=400)
            return Response(data, status=201)
        deleted = self._remove_from_relation(Favorite, recipe)
        if not deleted:
            return Response({"errors": "Рецепт не в избранном"}, status=400)
        return Response(status=204)

    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart")
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            created, data = self._add_to_relation(ShoppingCart, recipe,
                                                  ShortRecipeSerializer)
            if not created:
                return Response({"errors": "Рецепт уже в списке покупок"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(data, status=status.HTTP_201_CREATED)
        deleted = self._remove_from_relation(ShoppingCart, recipe)
        if not deleted:
            return Response({"errors": "Рецепта нет в списке покупок"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _get_shopping_cart_ingredients(self, user):
        return (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

    @action(detail=False, methods=["get"], url_path="download_shopping_cart",
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = self._get_shopping_cart_ingredients(request.user)
        template = "{} ({}) — {}"
        content = "\n".join(
            template.format(
                ing["ingredient__name"],
                ing["ingredient__measurement_unit"],
                ing["total_amount"]
            )
            for ing in ingredients
        )
        file_like = BytesIO(content.encode("utf-8"))
        response = FileResponse(
            file_like,
            as_attachment=True,
            filename="shopping_list.txt",
            content_type="text/plain",
        )
        return response


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
