from djoser.views import UserViewSet
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.decorators import action
from .models import Follow, User
from .serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    """
    ViewSet для работы с пользователями.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """
        Отображение информации о текущем пользователе
        """
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        """
        Отображение списка пользователей,
        на которых подписан текущий пользователь.
        """
        pass

    @action(methods=['post, delete'], detail=False)
    def subscribe(self, request):
        """
        Подписаться/отписаться от пользователя.
        """
        pass
