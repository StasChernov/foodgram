import io

from django.db.models import Sum
from django.http import FileResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.renderers import cart_render
from api.serializers import (
    AvatarSerializer, IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeViewSerializer,
    SubscribersViewSerializer, TagSerializer,
    UserRecipeSerializer
)
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag, User, Subscribe
)


class TagViewSet(ReadOnlyModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class FoodgramUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action in ['me']:
            return [IsAuthenticated(), ]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
    )
    def subscriptions(self, request):
        subscriptions = User.objects.filter(authors__user=self.request.user)
        pages = self.paginate_queryset(subscriptions)
        return self.get_paginated_response(
            SubscribersViewSerializer(
                pages, many=True, context={'request': request},
            ).data
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if user == author:
            raise ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        _, created = Subscribe.objects.get_or_create(
            user=user,
            author=author
        )
        if not created:
            raise ValidationError(
                'Вы уже подписаны на пользователя {author}.'
            )
        return Response(
            SubscribersViewSerializer(author, context={'request': request})
            .data,
            status=status.HTTP_201_CREATED
        )


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeViewSerializer
        return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def cart_and_favorite_manage(self, request, model, pk, message):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise ValidationError(
                {'detail': f'Рецепт {recipe} уже добавлен в {message}.'}
            )
        return Response(
            UserRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.cart_and_favorite_manage(
            request, ShoppingCart, pk, 'корзину'
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
    )
    def favorite(self, request, pk):
        return self.cart_and_favorite_manage(
            request, Favorite, pk, 'избранное'
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts__user=request.user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        recipes = (user.shopping_carts.all())
        buffer = io.BytesIO()
        buffer.write(
            bytes(cart_render(ingredients, recipes), encoding='utf-8')
        )
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="list.txt")

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            raise ValidationError(f'Рецепта c id {pk} не существует!')
        short_link = self.request.build_absolute_uri(
            reverse(
                'recipes:short_link',
                args=[pk]
            )
        )
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)
