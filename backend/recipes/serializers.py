from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe


class FavoriteRecipe(ModelSerializer):
    """
    Сериализатор для работы с избранными рецептами.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
