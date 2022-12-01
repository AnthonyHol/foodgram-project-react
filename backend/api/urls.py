from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()

router.register("ingredients", IngredientViewSet)
router.register("tags", TagViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path(
        "recipes/<int:pk>/shopping_cart/",
        RecipeViewSet.as_view({"post": "shopping_cart"}),
        name="shopping_cart",
    ),
    path(
        "recipes/<int:pk>/favorite/",
        RecipeViewSet.as_view({"post": "favorite"}),
        name="favorite_recipe",
    ),
    path("", include(router.urls)),
]
