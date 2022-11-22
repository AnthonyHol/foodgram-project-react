from rest_framework.serializers import ModelSerializer
from recipes.models import Tag, Ingredient


class TagSerializer(ModelSerializer):
    """Сериализатор просмотра тегов"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор просмотра ингрилиентов"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'units')
