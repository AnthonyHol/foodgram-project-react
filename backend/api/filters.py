from django_filters import rest_framework
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter
from users.models import User


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.CharFilter()
    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        label="Tags",
        to_field_name="slug",
    )
    is_favorited = rest_framework.BooleanFilter(method="get_favorite")
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method="get_is_in_shopping_cart"
    )

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')


class IngredientFilter(SearchFilter):
    search_param = "name"
