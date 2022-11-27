from rest_framework.serializers import ModelSerializer, IntegerField, CharField
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
)
from users.serializers import CustomUserSerializer
from rest_framework.fields import (
    SerializerMethodField,
    ReadOnlyField,
)
from rest_framework.relations import PrimaryKeyRelatedField
from recipes.models import Favorite
from drf_extra_fields.fields import Base64ImageField


class TagSerializer(ModelSerializer):
    """
    Сериализатор для работы с тегами.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для работы с ингредиентами.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(ModelSerializer):
    """
    Сериализатор связи ингридиентов и рецепта.
    """

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    """
    Сериализатор для работы с рецептами.
    """

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField(method_name='get_ingredients')
    is_favorited = SerializerMethodField(method_name='get_is_favorited')
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)

        return RecipeIngredientsSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')

        if request.user.is_anonymous:
            return False

        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()


class IngredientsWriteSerializer(ModelSerializer):
    """
    Сериализатор для записи ингредиентов.
    """

    id = IngredientSerializer()
    name = CharField(required=False)
    measurement_unit = IntegerField(required=False)
    amount = IntegerField()

    class Meta:
        model = RecipeIngredientsSerializer
        fields = ('id', 'name', 'amount', 'measurement_unit')

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class CreateRecipeSerializer(ModelSerializer):
    """
    Сериализатор создания, изменения и удаления рецепта.
    """

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsWriteSerializer(
        source='recipe_ingredients', many=True, read_only=True
    )
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(use_url=True, required=False)

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredients.objects.bulk_create(
            [
                RecipeIngredients(
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    recipe=recipe,
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        ingredients_data = self.initial_data.get('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )

        self.create_ingredients(ingredients_data, recipe)

        recipe.tags.set(tags)
        return recipe

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
