from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, TagViewSet, RecipeViewSet

router = DefaultRouter()

router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]