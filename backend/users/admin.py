from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    """ Админ панель управление пользователями """
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
    ordering = ('username', )
    empty_value_display = '—'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """ Админ панель управление подписками """
    list_display = ('user', 'author')
    list_display_links = ('user', )
    search_fields = ('user', )
    empty_value_display = '—'