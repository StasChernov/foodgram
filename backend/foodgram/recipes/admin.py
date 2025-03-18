from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, Recipe, ShoppingCart, Subscribe,
                     Tag)


admin.site.unregister(Group)
User = get_user_model()


@admin.register(Favorite, ShoppingCart)
class FavoriteCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


class RecipesCountMixin():

    @admin.display(description='Количество рецептов')
    def recipes_count(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    list_display_links = ('name',)
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipes_count')
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
    def get_tags(self, recipe):
        return ", ".join([str(tag) for tag in recipe.tags.all()])

    @admin.display(description='Продукты')
    def get_ingredients(self, recipe):
        return ", ".join(
            [str(ingredient) for ingredient in recipe.ingredients.all()]
        )


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')


class Filter(admin.SimpleListFilter):

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        print(self.value)
        if self.value() == 'yes':
            return queryset.filter(**{self.parameter_name: False})
        if self.value() == 'no':
            return queryset.filter(**{self.parameter_name: True})


class RecipesFilter(Filter):

    title = 'Есть рецепты:'
    parameter_name = 'recipes__isnull'


class SubscriptionsFilter(Filter):

    title = 'Есть подписки:'
    parameter_name = 'subscriber__isnull'


class SubscribersFilter(Filter):

    title = 'Есть подписчики:'
    parameter_name = 'following__isnull'


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'get_full_name',
        'email',
        'get_avatar',
        'get_recipes_count',
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
        else:
            return 'Нет аватара'

    @admin.display(description='Рецептов')
    @mark_safe
    def get_recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписки')
    @mark_safe
    def get_subscriptions_count(self, user):
        return user.subscriber.count()

    @admin.display(description='Подписчики')
    @mark_safe
    def get_subscribers_count(self, user):
        return user.following.count()
