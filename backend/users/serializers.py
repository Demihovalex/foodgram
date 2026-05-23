from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Subscription
from rest_framework import serializers

from .models import CustomUser


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "avatar",
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("user", "author")

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data["author"]:
            raise serializers.ValidationError("Нельзя подписаться на себя")
        return data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ("avatar",)
