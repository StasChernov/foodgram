from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import (
    Favorite, Ingredient,
    Recipe, ShoppingCart,
    Subscribe, Tag, User
)


admin.site.unregister(Group)


@admin.register(Favorite, ShoppingCart)
class FavoriteCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


class RecipesCountMixin():

    list_display = ('recipes_count',)

    @admin.display(description='Количество рецептов')
    def recipes_count(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
        *RecipesCountMixin.list_display)
    list_display_links = ('name',)
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', *RecipesCountMixin.list_display)
    list_display_links = ('name',)
    search_fields = ('name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'get_tags',
        'favorites_count',
        'get_ingredients',
        'get_image'
    )
    list_display_links = ('name',)

    @admin.display(description='В избранном')
    def favorites_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Изображение')
    @mark_safe
    def get_image(self, recipe):
        return mark_safe(f'<img src="{recipe.image.url}" width=50 />')

    @admin.display(description='Тэги')
    @mark_safe
    def get_tags(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Продукты')
    @mark_safe
    def get_ingredients(self, recipe):
        return '<br>'.join(
            ingredient.name for ingredient in recipe.ingredients.all()
        )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')


class UserFilter(admin.SimpleListFilter):

    VALUES = (
        ('yes', 'Да'),
        ('no', 'Нет'),
    )

    def lookups(self, request, model_admin):
        return self.VALUES

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(**{self.parameter_name: False})
        if self.value() == 'no':
            return queryset.filter(**{self.parameter_name: True})


class RecipesFilter(UserFilter):

    title = 'Есть рецепты:'
    parameter_name = 'recipes__isnull'


class SubscriptionsFilter(UserFilter):

    title = 'Есть подписки:'
    parameter_name = 'subscribers__isnull'


class SubscribersFilter(UserFilter):

    title = 'Есть подписчики:'
    parameter_name = 'authors__isnull'


@admin.register(User)
class UserAdmin(RecipesCountMixin, UserAdmin):
    list_display = (
        'id',
        'username',
        'get_full_name',
        'email',
        'get_avatar',
        *RecipesCountMixin.list_display,
        'get_subscriptions_count',
        'get_subscribers_count'
    )
    list_display_links = ('username',)
    search_fields = ('username', 'email')
    list_filter = (RecipesFilter, SubscriptionsFilter, SubscribersFilter)

    @admin.display(description='ФИО')
    def get_full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def get_avatar(self, user):
        if user.avatar:
            return f'<img src="{user.avatar.url}" width=50 />'
        return ''

    @admin.display(description='Подписки')
    def get_subscriptions_count(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписчики')
    def get_subscribers_count(self, user):
        return user.authors.count()
