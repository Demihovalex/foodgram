from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time')
    search_fields = ('name', 'author__email')
    list_filter = ('tags',)
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags',)

    def save_model(self, request, obj, form, change):
        if not obj.recipe_ingredients.exists():
            self.message_user(
                request, 'Нельзя сохранить рецепт без ингредиентов',
                level='ERROR'
            )
            return
        super().save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
