from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


<<<<<<< HEAD
class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
=======
class RecipeFilter(FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
>>>>>>> 590e18ab030827a6c9b54624b03d87cf9d226724
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
<<<<<<< HEAD
        if value and self.request.user.is_authenticated:
=======
        if self.request.user.is_authenticated and value:
>>>>>>> 590e18ab030827a6c9b54624b03d87cf9d226724
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
<<<<<<< HEAD
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset
=======
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
>>>>>>> 590e18ab030827a6c9b54624b03d87cf9d226724
