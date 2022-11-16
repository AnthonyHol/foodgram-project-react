from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UsersViewSet

router = DefaultRouter()

# router.register('users', UsersViewSet)
# router.register('recipes', RecipeViewSet)
# router.register('ingredients', IngredientViewSet)
# router.register('tags', TagViewSet)


urlpatterns = [
    # path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]