from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import Tag, Ingredient, Recipe
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer,
)
from rest_framework.filters import SearchFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .paginations import SixPagePagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework import status
from rest_framework.response import Response
from recipes.models import Favorite, ShoppingCart
from rest_framework.decorators import action
from django.http import HttpResponse


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
    filter_backends = [SearchFilter]
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептами.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = SixPagePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(methods=["post, delete"], detail=True)
    def shopping_cart(self, request, pk=None):
        """
        Метод добавления/удаления рецепта в список покупок.
        """
        if request.method == "POST":
            data = {'user': request.user.id, 'recipe': pk}
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = ShoppingCart.objects.filter(user=request.user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Рецепт уже удален!'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """
        Метод добавления/удаления рецепта в Избранное.
        """

        if request.method == "POST":
            data = {'user': request.user.id, 'recipe': pk}
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        obj = Favorite.objects.filter(user=request.user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'Рецепт уже удален!'},
            status=status.HTTP_400_BAD_REQUEST,
        )
