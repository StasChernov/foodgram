from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def get_is_in_shopping_cart(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(shopping_carts__user=self.request.user)
        return recipes
