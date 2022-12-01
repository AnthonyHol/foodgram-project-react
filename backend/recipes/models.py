from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название ингридиента", db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Единицы измерения"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Тег", db_index=True, unique=True
    )
    color = ColorField(format="hex", verbose_name="HEX-код тега")
    slug = models.SlugField(max_length=200, verbose_name="Slug", unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    image = models.ImageField(
        blank=True,
        upload_to="recipes/",
        verbose_name="Картинка",
        null=True,
    )
    text = models.TextField(verbose_name="Описание")
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True
    )

    ingredients = models.ManyToManyField(
        Ingredient, verbose_name="Ингридиенты", through="RecipeIngredients"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Теги")
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(
                1, message="Время приготовления не может быть <1 минуты!"
            )
        ],
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты",
        related_name="recipe_ingredients",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipe_ingredients",
    )
    amount = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Требуется хотя бы один ингредиент!")
        ],
        verbose_name="Количество ингредиента",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="recipe_ingredients_unique",
            )
        ]
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="shopping_list",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="shopping_list",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("user", "recipe"), name="user_shopping_list_unique"
            )
        ]
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="favorites",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorites",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("user", "recipe"), name="user_favorite_unique"
            )
        ]
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
