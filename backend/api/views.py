from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from recipes.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer
from rest_framework.filters import SearchFilter


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
