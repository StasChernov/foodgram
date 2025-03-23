from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Favorite, Ingredient,
    Recipe, ShoppingCart,
    Subscribe, Tag, User,
    RecipeIngredient
)


admin.site.unregister(Group)


@admin.register(Favorite, ShoppingCart)
class FavoriteCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


class RecipesCountMixin():

    list_display = ('recipes_count',)

    @admin.display(description='Рецептов')
    def recipes_count(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', *RecipesCountMixin.list_display)
    list_display_links = ('name',)
    search_fields = ('name', 'slug')


class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 0
    fields = (
        'ingredient',
        'amount',
        'unit',
    )
    readonly_fields = ('unit',)

    @admin.display(description='Мера')
    @mark_safe
    def unit(self, recipeingredient):
        url = reverse('admin:%s_%s_change' % (
            recipeingredient.ingredient._meta.app_label,
            recipeingredient.ingredient._meta.model_name
        ), args=(recipeingredient.ingredient.pk,))
        return '<a href="%s">%s</a>' % (
            url, recipeingredient.ingredient.measurement_unit
        )


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
    list_filter = ('author',)
    inlines = (IngredientInline,)

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
        ingredient = '{name} {amount}/{unit}'
        return '<br>'.join(
            ingredient.format(
                name=recipe_ingredient.ingredient.name,
                amount=recipe_ingredient.amount,
                unit=recipe_ingredient.ingredient.measurement_unit
            ) for recipe_ingredient in recipe.recipe_ingredients.all()
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
            return queryset.filter(**{self.parameter_name: False}).distinct()
        if self.value() == 'no':
            return queryset.filter(**{self.parameter_name: True}).distinct()


class RecipesFilter(UserFilter):

    title = 'Есть рецепты:'
    parameter_name = 'recipes__isnull'


class SubscriptionsFilter(UserFilter):

    title = 'Есть подписки:'
    parameter_name = 'subscribers__isnull'


class SubscribersFilter(UserFilter):

    title = 'Есть подписчики:'
    parameter_name = 'authors__isnull'


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
        *RecipesCountMixin.list_display)
    list_display_links = ('name',)
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', RecipesFilter)


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
        'get_subscribers_count',
    )
    list_display_links = ('username',)
    search_fields = ('username', 'email')
    list_filter = (RecipesFilter, SubscriptionsFilter, SubscribersFilter)
    fieldsets = UserAdmin.fieldsets + (
        ('Изменить аватар',
         {'fields': ('avatar',)}),
    )

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
