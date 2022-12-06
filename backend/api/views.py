from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)

from .filters import IngredientFilter, RecipeFilter
from .paginations import SixPagePagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с тегами.
    """

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с ингредиентами.
    """

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ("^name",)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептами.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = SixPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        methods=("POST", "DELETE"),
        detail=True,
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def shopping_cart(self, request, pk=None):
        """
        Метод добавления/удаления рецепта в список покупок.
        """
        if request.method == "POST":
            data = {"user": request.user.id, "recipe": pk}
            serializer = ShoppingCartSerializer(
                data=data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = ShoppingCart.objects.filter(user=request.user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": "Рецепт уже удален!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=True,
        methods=("POST"),
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def favorite(self, request, pk=None):
        """
        Метод добавления/удаления рецепта в Избранное.
        """

        if request.method == "POST":
            data = {"user": request.user.id, "recipe": pk}
            serializer = FavoriteSerializer(
                data=data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = Favorite.objects.filter(user=request.user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": "Рецепт уже удален!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        detail=False, methods=("GET"), permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Метод для скачивания корзины покупок.
        """
        user = request.user
        if not user.shopping_list.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = (
            RecipeIngredients.objects.filter(
                recipe__shopping_list__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )

        today = datetime.today()
        shopping_list = (
            f"Список покупок для: {user.get_full_name()}\n\n"
            f"Дата: {today:%Y-%m-%d}\n\n"
        )
        shopping_list += "\n".join(
            [
                f'- {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' - {ingredient["amount"]}'
                for ingredient in ingredients
            ]
        )
        shopping_list += f"\n\nFoodgram ({today:%Y})"

        filename = f"{user.username}_shopping_list.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
