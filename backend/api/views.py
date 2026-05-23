from constants import PAGE_SIZE
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
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
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import CustomUser
from users.serializers import CustomUserSerializer, AvatarSerializer

from .filters import IngredientFilter
from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeReadSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        return self._toggle_subscription(request, user_id)

    def delete(self, request, user_id):
        return self._toggle_subscription(request, user_id)

    def _toggle_subscription(self, request, user_id):
        author = get_object_or_404(CustomUser, id=user_id)
        if request.user == author:
            return Response(
                {"error": "Нельзя подписаться на себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Subscription.objects.create(user=request.user, author=author)
            return Response(
                CustomUserSerializer(author,
                                     context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )


class SubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        subscriptions = Subscription.objects.filter(
            user=request.user
        ).select_related("author")

        results = []
        for sub in subscriptions:
            author = sub.author
            recipes = Recipe.objects.filter(
                author=author).order_by("-pub_date")
            recipes_serializer = RecipeReadSerializer(
                recipes, many=True, context={"request": request}
            )
            author_data = CustomUserSerializer(
                author, context={"request": request}).data
            author_data["recipes"] = recipes_serializer.data
            results.append(author_data)

        paginator = self.pagination_class()
        paginator.page_size = request.query_params.get("limit", PAGE_SIZE)
        page = paginator.paginate_queryset(results, request)
        return paginator.get_paginated_response(page)


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


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
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
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
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
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
        recipe = self.get_object()
        base_url = request.build_absolute_uri("/").rstrip("/")
        short_link = f"{base_url}/recipes/{recipe.id}/"
        return Response({"short_link": short_link})


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class UserDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user, context={"request": request})
        return Response(serializer.data)


from users.serializers import AvatarSerializer

class AvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = AvatarSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
