from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import Follow, User
from .serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    """
    ViewSet для работы с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
