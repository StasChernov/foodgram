from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, ShoppingCart, Subscribe,
                     Tag, User)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'text', 'favorites_count', 'image')
    list_display_links = ('name',)
    filter_horizontal = ('tags', 'ingredients')

    def favorites_count(self, recipe):
        return recipe.favorites.count()


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name', 'slug')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_display_links = ('username',)
    search_fields = ('username', 'email')
