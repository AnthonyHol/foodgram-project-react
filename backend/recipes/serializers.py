from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe
from rest_framework.serializers import ModelSerializer


class FavoriteRecipeSerializer(ModelSerializer):
    """
    Сериализатор для работы с избранными рецептами.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
