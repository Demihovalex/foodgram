from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from users.serializers import CustomUserSerializer

from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeReadSerializer,
    TagSerializer,
)


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        author = get_object_or_404(CustomUser, id=user_id)
        if request.user == author:
            return Response({'error': 'Нельзя подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription, created = Subscription.objects.get_or_create(
            user=request.user, author=author
        )
        if not created:
            return Response({'error': 'Вы уже подписаны'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(CustomUserSerializer(author, context={'request':
                                                              request}).data)

    def delete(self, request, user_id):
        author = get_object_or_404(CustomUser, id=user_id)
        deleted, _ = Subscription.objects.filter(
            user=request.user, author=author
        ).delete()
        if not deleted:
            return Response({'error': 'Вы не подписаны'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Получаем авторов, на которых подписан пользователь
        subscriptions = Subscription.objects.filter(
            user=request.user).select_related('author')
        authors = [sub.author for sub in subscriptions]

        # Получаем рецепты этих авторов, сортируем по дате (новые выше)
        recipes = Recipe.objects.filter(
            author__in=authors).order_by('-pub_date')

        # Пагинация
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('limit', 6)
        page = paginator.paginate_queryset(recipes, request)

        serializer = RecipeReadSerializer(
            page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist("tags")
        author = self.request.query_params.get("author")
        is_favorited = self.request.query_params.get("is_favorited")
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart")

        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if author:
            queryset = queryset.filter(author_id=author)
        if is_favorited and self.request.user.is_authenticated:
            queryset = queryset.filter(favorites__user=self.request.user)
        if is_in_shopping_cart and self.request.user.is_authenticated:
            queryset = queryset.filter(shopping_cart__user=self.request.user)

        return queryset

    @action(detail=True, methods=["post", "delete"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            favorite, created = Favorite.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == "POST":
            cart, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:
                return Response(status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(shopping_cart__user=request.user)
        ingredients = {}
        for recipe in recipes:
            for ingredient in recipe.recipe_ingredients.all():
                name = ingredient.ingredient.name
                unit = ingredient.ingredient.measurement_unit
                key = (name, unit)
                ingredients[key] = ingredients.get(key, 0) + ingredient.amount

        shopping_list = []
        for (name, unit), amount in ingredients.items():
            shopping_list.append(f"{name} ({unit}) — {amount}\n")
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = self.get_object()
        base_url = request.build_absolute_uri('/').rstrip('/')
        short_link = f"{base_url}/recipes/{recipe.id}/"
        return Response({"short_link": short_link})


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)
