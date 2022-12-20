from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from recipes.models import Recipe
from recipes.serializers import FavoriteRecipeSerializer

from .models import Follow, User


class UserRegistrationSerializer(UserCreateSerializer):
    """
    Сериализатор для создания новых пользователей.
    """

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для работы с данными о пользователе.
    """

    is_subscribed = serializers.SerializerMethodField(
        read_only=True, method_name="get_is_subscribed"
    )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )


class FollowSerializer(ModelSerializer):
    """
    Сериализатор для подписки/отписки от пользователя.
    """

    def validate(self, data):
        get_object_or_404(User, username=data["author"])

        if self.context["request"].user == data["author"]:
            raise ValidationError(
                {"errors": "Нельзя подписаться на самого себя!"}
            )

        if Follow.objects.filter(
            user=self.context["request"].user, author=data["author"]
        ):
            raise ValidationError(
                {"errors": "Вы уже подписаны на данного пользователя!"}
            )

        return data

    def to_representation(self, instance):
        return FollowListSerializer(
            instance.author, context={"request": self.context.get("request")}
        ).data

    class Meta:
        model = Follow
        fields = ("user", "author")


class FollowListSerializer(CustomUserSerializer):
    """
    Сериализатор для работы со списком подписок.
    """

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField(read_only=True)

    def get_recipes(self, author):
        queryset = self.context.get("request")
        recipes_limit = queryset.query_params.get("recipes_limit")
        if not recipes_limit:
            return FavoriteRecipeSerializer(
                Recipe.objects.filter(author=author),
                many=True,
                context={"request": queryset},
            ).data
        return FavoriteRecipeSerializer(
            Recipe.objects.filter(author=author)[: int(recipes_limit)],
            many=True,
            context={"request": queryset},
        ).data

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_is_subscribed(self, author):
        return Follow.objects.filter(
            user=self.context.get("request").user, author=author
        ).exists()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
