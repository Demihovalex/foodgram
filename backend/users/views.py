from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from recipes.models import Subscription
from .models import CustomUser
from .serializers import CustomUserSerializer, SubscriptionSerializer


class SubscriptionView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        author = get_object_or_404(CustomUser, id=user_id)
        serializer = SubscriptionSerializer(
            data={"user": request.user.id, "author": author.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        subscription, created = Subscription.objects.get_or_create(
            user=request.user, author=author
        )
        if not created:
            return Response(
                {"error": "Вы уже подписаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            CustomUserSerializer(author, context={"request": request}).data
        )

    def delete(self, request, user_id):
        author = get_object_or_404(CustomUser, id=user_id)
        subscription = Subscription.objects.filter(
            user=request.user, author=author
        )
        if not subscription.exists():
            return Response(
                {"error": "Вы не подписаны"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(following__user=self.request.user)
