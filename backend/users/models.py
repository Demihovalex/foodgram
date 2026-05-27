from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.conf import settings

from constants import (
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MAX_USERNAME_LENGTH,
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        help_text="Имя пользователя",
        verbose_name="Имя пользователя",
        validators=[username_validator],
    )
    email = models.EmailField(
        unique=True,
        max_length=MAX_EMAIL_LENGTH,
        help_text="Электронная почта",
        verbose_name="Электронная почта",
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=False,
        help_text="Имя",
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=False,
        help_text="Фамилия",
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Аватар",
        verbose_name="Аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["id"]

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="unique_subscription"),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="user_not_self_subscription"
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.author}"
