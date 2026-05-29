from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError

from users.models import Subscription

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInlineForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    form = RecipeIngredientInlineForm
    min_num = 1
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        def clean_formset(formset):
            """Проверка, что есть хотя бы один ингредиент"""
            has_ingredients = False
            for form in formset.forms:
                if (
                    form.cleaned_data
                    and not form.cleaned_data.get('DELETE', False)
                ):
                    has_ingredients = True
                    break
            if not has_ingredients:
                raise ValidationError(
                    'Рецепт должен содержать хотя бы один ингредиент'
                )
        formset.clean = clean_formset
        return formset


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        if not image:
            self.add_error('image', 'Рецепт должен содержать изображение')
        return cleaned_data


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    form = RecipeAdminForm
    inlines = [RecipeIngredientInline]
    list_display = ("id", "name", "author", "cooking_time", "pub_date")
    search_fields = ("name", "author__email", "author__username")
    list_filter = ("tags",)
    readonly_fields = ("favorite_count",)

    def favorite_count(self, obj):
        return obj.favorites.count()
    favorite_count.short_description = "Добавлений в избранное"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    search_fields = ("user__email", "author__email")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__email",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__email",)
