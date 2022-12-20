from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import ReadOnlyField, SerializerMethodField
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    ValidationError,
)

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from recipes.serializers import FavoriteRecipeSerializer
from users.serializers import CustomUserSerializer


class TagsSerializer(ModelSerializer):
    """
    Сериализатор для работы с тегами.
    """

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientsSerializer(ModelSerializer):
    """
    Сериализатор для работы с ингредиентами.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientsSerializer(ModelSerializer):
    """
    Сериализатор связи ингредиентов с рецептом.
    """

    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(source="ingredient.measurement_unit")
    amount = IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "amount", "measurement_unit")


class RecipeSerializer(ModelSerializer):
    """
    Сериализатор для просмотра рецепта.
    """

    author = CustomUserSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    tags = TagsSerializer(many=True)
    is_favorited = SerializerMethodField(
        read_only=True, method_name="get_is_favorited"
    )
    is_in_shopping_cart = SerializerMethodField(
        read_only=True, method_name="get_is_in_shopping_cart"
    )

    def get_is_favorited(self, recipe):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=recipe.id
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=recipe.id
        ).exists()

    class Meta:
        fields = (
            "is_favorited",
            "is_in_shopping_cart",
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe


class CreateRecipeSerializer(ModelSerializer):
    """
    Сериализатор для создания рецепта.
    """

    author = CustomUserSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    image = Base64ImageField()

    def validate(self, data):
        """
        Метод валидации ингредиентов для рецепта.
        """
        ingredients_data = self.initial_data.get("ingredients")

        if not ingredients_data:
            raise ValidationError("Добавьте хотя бы один ингредиент!")

        ingredients_list = []
        for ingredient in ingredients_data:
            ingredient_id = ingredient["id"]

            if int(ingredient["amount"]) <= 0:
                raise ValidationError(
                    "Количество ингредиентов должно быть не меньше 1!"
                )

            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise ValidationError(
                    f"Не существует ингредиента с id={ingredient_id}!"
                )

            if ingredient_id in ingredients_list:
                raise ValidationError("Ингредиент не должен повторяться!")

            ingredients_list.append(ingredient_id)

        return data

    def create_ingridients(self, ingredients_data, recipe):
        """
        Метод создания ингредиентов для рецепта.
        """
        for ingredient in ingredients_data:
            RecipeIngredients(
                recipe=recipe,
                ingredient_id=ingredient["id"],
                amount=ingredient.get("amount"),
            ).save()

    def create(self, validated_data):
        """
        Метод создания рецепта.
        """
        ingredients_data = self.initial_data.get("ingredients")
        tags = validated_data.pop("tags")

        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )

        self.create_ingridients(ingredients_data, recipe)
        recipe.tags.set(tags)

        return recipe

    def update(self, recipe, validated_data):
        """
        Метод изменения рецепта.
        """
        recipe.ingredients.clear()
        recipe.tags.clear()
        ingredients_data = self.initial_data.get("ingredients")
        tags = validated_data.pop("tags")
        recipe.tags.set(tags)
        RecipeIngredients.objects.filter(recipe=recipe).all().delete()

        self.create_ingridients(ingredients_data, recipe)

        return super().update(recipe, validated_data)

    class Meta:
        fields = (
            "id",
            "tags",
            "ingredients",
            "author",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe


class RecipeShortInfo(ModelSerializer):
    """Сериализатор отображения избранного"""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(ModelSerializer):
    """
    Сериализатор списка покупок.
    """

    def validate(self, data):
        request = self.context.get("request")
        recipe = data["recipe"]

        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise ValidationError({"errors": "Рецепт уже есть в Корзине!"})

        return data

    def to_representation(self, instance):
        return RecipeShortInfo(
            instance.recipe, context={"request": self.context.get("request")}
        ).data

    class Meta:
        model = ShoppingCart
        fields = ("recipe", "user")


class FavoriteSerializer(ModelSerializer):
    """Сериализатор избранного"""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise ValidationError({'errors': 'Уже есть в избранном.'})
        return data

    def to_representation(self, instance):
        return RecipeShortInfo(
            instance.recipe, context={'request': self.context.get('request')}
        ).data


# class FavoriteSerializer(ModelSerializer):
#     """
#     Сериализатор избранных рецептов.
#     """

#     def validate(self, data):
#         request = self.context.get("request")
#         if not request or request.user.is_anonymous:
#             return False

#         recipe = data["recipe"]

#         if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
#             raise ValidationError({"errors": "Рецепт уже есть в Избранном!"})

#         return data

#     def to_representation(self, instance):
#         return FavoriteRecipeSerializer(
#             instance.recipe, context={"request": self.context.get("request")}
#         ).data

#     class Meta:
#         model = Favorite
#         fields = ("user", "recipe")
