from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import Tag, Ingredient, Recipe
from .serializers import TagSerializer, IngredientSerializer, RecipeSerializer
from rest_framework.filters import SearchFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .paginations import SixPagePagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework import status
from rest_framework.response import Response
from users.models import Favorite
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
    ViewSet.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = SixPagePagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer

        # return CreateRecipeSerializer
