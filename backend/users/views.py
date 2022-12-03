from api.paginations import SixPagePagination
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
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

    @action(methods=["get"], detail=False)
    def subscriptions(self, request):
        """
        Отображение списка пользователей,
        на которых подписан текущий пользователь.
        """
        subscriptions_list = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )
        serializer = FollowListSerializer(
            subscriptions_list, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=["post, delete"], detail=False)
    def subscribe(self, request):
        """
        Подписаться/отписаться от пользователя.
        """
        if request.method == "POST":
            serializer = FollowSerializer(
                data={
                    "user": request.user.id,
                    "author": get_object_or_404(User, id=id).id,
                },
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Follow, author=get_object_or_404(User, id=id), user=request.user
        )
        self.perform_destroy(subscription)
        return Response(status=status.HTTP_204_NO_CONTENT)
