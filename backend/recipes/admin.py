from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingList, Tag


class IngredientsRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "units")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "—"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name", "slug")
    list_filter = ("name",)
    empty_value_display = "—"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "favorites",
    )
    search_fields = ("author", "name")
    list_filter = ("tags",)
    filter_horizontal = ("tags",)
    inlines = (IngredientsRecipeInline,)
    empty_value_display = "—"

    def favorites(self, obj):
        if Favorite.objects.filter(recipe=obj).exists():
            return Favorite.objects.filter(recipe=obj).count()
        return 0

    favorites.short_description = "Количество добавлений в избранное"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    list_filter = ("user", "recipe")
    search_fields = ("user", "recipe")
    empty_value_display = "—"


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user")
    list_filter = ("recipe", "user")
    search_fields = ("user",)
    empty_value_display = "—"
