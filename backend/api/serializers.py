from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)
from recipes.serializers import FavoriteRecipeSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ReadOnlyField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    ValidationError,
)
from users.serializers import CustomUserSerializer


class TagSerializer(ModelSerializer):
    """
    Сериализатор для работы с тегами.
    """

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для работы с ингредиентами.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientsSerializer(ModelSerializer):
    """
    Сериализатор связи ингридиентов и рецепта.
    """

    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(ModelSerializer):
    """
    Сериализатор для работы с рецептами.
    """

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField(method_name="get_ingredients")
    is_favorited = SerializerMethodField(method_name="get_is_favorited")
    is_in_shopping_cart = SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)

        return RecipeIngredientsSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")

        if request.user.is_anonymous:
            return False

        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request.user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class IngredientsWriteSerializer(ModelSerializer):
    """
    Сериализатор для записи ингредиентов.
    """

    id = IngredientSerializer()
    name = CharField(required=False)
    measurement_unit = IntegerField(required=False)
    amount = IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ("id", "name", "amount", "measurement_unit")


class CreateRecipeSerializer(ModelSerializer):
    """
    Сериализатор создания, изменения и удаления рецепта.
    """

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsWriteSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(use_url=True, required=False)

    def validate(self, data):
        ingredients_data = self.initial_data.get("ingredients")
        cooking_time_data = self.initial_data.get("cooking_time")

        if not ingredients_data:
            raise ValidationError('Добавьте хотя бы один ингредиент!')

        if cooking_time_data < 1:
            raise ValidationError(
                'Время приготовления не может быть меньше 1!'
            )

        ingredients_list = []
        for ingredient in ingredients_data:
            ingredient_id = ingredient['id']
            try:
                int(ingredient['amount'])
            except ValueError:
                raise ValidationError(
                    'Количество ингредиентов может быть только целым числом!'
                )
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    'Количество ингредиентов не может быть меньше 0!'
                )
            if ingredient_id in ingredients_list:
                raise ValidationError('Ингредиент не может дублироваться!')
            ingredients_list.append(ingredient_id)

        return data

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredients.objects.bulk_create(
            [
                RecipeIngredients(
                    ingredient=Ingredient.objects.get(id=ingredient["id"]),
                    recipe=recipe,
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """
        Метод создания рецепта.
        """
        ingredients_data = self.initial_data.get("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )

        self.create_ingredients(ingredients_data, recipe)

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
        self.create_ingredients(ingredients_data, recipe)

        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance, context={"request": self.context.get("request")}
        ).data

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )


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
        return FavoriteRecipeSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data

    class Meta:
        model = ShoppingCart
        fields = ("recipe", "user")


class FavoriteSerializer(ModelSerializer):
    """
    Сериализатор избранных рецептов.
    """

    def validate(self, data):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        recipe = data["recipe"]
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise ValidationError({"errors": "Рецепт уже есть в Избранном!"})
        return data

    def to_representation(self, instance):
        return FavoriteRecipeSerializer(
            instance.recipe, context={"request": self.context.get("request")}
        ).data

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
