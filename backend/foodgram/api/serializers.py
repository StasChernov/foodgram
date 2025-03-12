import base64
import re

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscribe, Tag, User)

MIN_TIME = 1
MAX_TIME = 100


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
        fields = ('id', 'name', 'slug')


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        if re.search(r'^[\w.@+-]+\Z', value) is None:
            raise serializers.ValidationError(
                'Недопустимое имя пользователя.'
            )
        return value


class CustomUserSerializer(UserSerializer):

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers. ModelSerializer):

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


class RecipeViewSerializer(serializers.ModelSerializer):

    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = CustomUserSerializer(read_only=True,)
    ingredients = RecipeIngredientSerializer(
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

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


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
        if not self.initial_data.get('ingredients'):
            raise ValidationError('Рецепт должен содержать ингредиенты.')
        if not self.initial_data.get('tags'):
            raise ValidationError('Рецепт должен содержать теги.')
        return data

    def validate_ingredients(self, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient in ingredients_list:
                raise ValidationError('Ингредиенты не должны повторяться.')
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    ('Количество ингредиента должно быть > 0.')
                )
            ingredients_list.append(ingredient)
        return ingredients

    def validate_tags(self, tags):
        if len(set(tags)) != len(tags):
            raise ValidationError('Теги не должны повторяться.')
        return tags

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise ValidationError('Время приготовления должно быть > 0.')
        return cooking_time

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient['amount']
            RecipeIngredient.objects.create(recipe=recipe,
                                            ingredient=ingredient['id'],
                                            amount=amount)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        for ingredient in ingredients:
            amount = ingredient['amount']
            RecipeIngredient.objects.create(recipe=instance,
                                            ingredient=ingredient['id'],
                                            amount=amount)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeViewSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже находится в избранном',
            )
        ]


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже находится в корзине',
            )
        ]


class UserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AvatarSerializer(serializers.ModelSerializer):

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if 'avatar' not in data:
            raise serializers.ValidationError(
                {'avatar': 'avatar обязательное поле.'}
            )
        return data


class SubscribeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate_author(self, value):
        user = self.context['request'].user
        if Subscribe.objects.filter(user=user, author=value).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        if user == value:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        return value

    def to_representation(self, instance):
        request = self.context['request']
        return SubscribeViewSerializer(
            instance.author, context={'request': request}
        ).data


class SubscribeViewSerializer(serializers.ModelSerializer):

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):

        recipes_limit = int(
            self.context['request'].query_params.get('recipes_limit', 0)
        )
        recipes = obj.recipes.all()
        if recipes_limit > 0:
            recipes = obj.recipes.all()[: recipes_limit]
        serializer = ShortRecipeSerializer(
            recipes, many=True, context=self.context
        )
        return serializer.data
