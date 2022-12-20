from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from api.paginations import SixPagePagination
from users.serializers import FollowListSerializer, FollowSerializer

from .models import Follow, User
from .serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    """
    ViewSet для работы с пользователями.
    """

    pagination_class = SixPagePagination
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(["GET"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """
        Отображение информации о текущем пользователе
        """

        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def subscriptions(self, request):
        """
        Метод отображение списка пользователей,
        на которых подписан текущий пользователь.
        """

        subscriptions_list = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowListSerializer(
            subscriptions_list, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def subscribe(self, request, id=None):
        """
        Метод для подписки/отписки от пользователя.
        """

        user = get_object_or_404(User, id=id)
        follow = Follow.objects.filter(user=request.user, author=user)

        if request.method == "POST":
            if user == request.user:
                error = {"errors": "Нельзя подписаться на самого себя!"}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            obj, created = Follow.objects.get_or_create(
                user=request.user, author=user
            )

            if not created:
                error = {"errors": "Вы уже подписаны на этого пользователя!"}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(obj, context={"request": request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not follow.exists():
            error = {"errors": "Вы не подписаны на этого пользователя!"}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
