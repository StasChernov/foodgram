import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField, IntegerField

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscribe, Tag, User)


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class FoodgramUserSerializer(UserSerializer):

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields, 'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscribe.objects.filter(user=user, author=author).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientViewSerializer(serializers. ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True,
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class RecipeViewSerializer(serializers.ModelSerializer):

    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = FoodgramUserSerializer(read_only=True,)
    ingredients = RecipeIngredientViewSerializer(
        many=True,
        read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        read_only=True,
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def calculation_fields(self, recipe, model):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and model.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_favorited(self, recipe):
        return self.calculation_fields(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self.calculation_fields(recipe, ShoppingCart)


class IngredientCreateSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):

    ingredients = IngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        if not data.get('ingredients'):
            raise ValidationError('Рецепт должен содержать продукты.')
        if not data.get('tags'):
            raise ValidationError('Рецепт должен содержать теги.')
        return data

    @staticmethod
    def field_validate(field_data, message):
        data_list = []
        duplicates = []
        for item in field_data:
            if item in data_list:
                duplicates.append(item.name)
            data_list.append(item)
        if duplicates:
            raise ValidationError(
                f'{message} {set(duplicates)} повторяется.'
            )
        return data_list

    def validate_ingredients(self, ingredients):
        ingredients_list = [
            ingredient['id'] for ingredient in ingredients
        ]
        self.field_validate(ingredients_list, 'Продукт')
        return ingredients

    def validate_tags(self, tags):
        return self.field_validate(tags, 'Тэг')

    def create_ingredients(self, recipe, ingredients):
        recipe_ingredients = [RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
        ) for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance,
            context=self.context
        ).data


class UserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class SubscribersViewSerializer(FoodgramUserSerializer):

    recipes = SerializerMethodField()
    recipes_count = IntegerField(source='recipes.count', read_only=True)

    class Meta(FoodgramUserSerializer.Meta):
        fields = (
            *FoodgramUserSerializer.Meta.fields,
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes(self, user):
        recipes_limit = int(
            self.context['request'].query_params.get('recipes_limit', 10**10)
        )
        serializer = UserRecipeSerializer(
            user.recipes.all()[: recipes_limit],
            many=True, context=self.context
        )
        return serializer.data
