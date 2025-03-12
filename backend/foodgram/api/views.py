import random
import string

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer, 
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeViewSerializer,
    SubscribeCreateSerializer,
    SubscribeViewSerializer,
    TagSerializer,
    UserRecipeSerializer
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    User
)


class TagViewSet(ModelViewSet):

    http_method_names = ['get']
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):

    http_method_names = ['get']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class CustomUserViewSet(UserViewSet):

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'DELETE':
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=self.request.user)
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(
            SubscribeViewSerializer(
                page, many=True, context={'request': request},
            ).data
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'DELETE':
            subscriptions = request.user.subscriptions.filter(author=author)
            if not subscriptions:
                return Response(
                    {"error": "Нет подписки на этого пользователя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscriptions.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = SubscribeCreateSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        print(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeViewSerializer
        return RecipeCreateUpdateSerializer

    def add_recipe(
            self, request, model, pk
    ):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            deleted_count, _ = model.objects.filter(
                recipe=pk, user=request.user
            ).delete()
            if deleted_count == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise ValidationError(
                {'detail': 'Рецепт уже добавлен.'}
            )
        return Response(
            UserRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.add_recipe(
            request, ShoppingCart, pk=pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='favorite',
    )
    def favorite(self, request, pk):
        print('111111')
        return self.add_recipe(
            request, Favorite, pk=pk
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts__user=request.user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(ingredient_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        shopping_list = 'Список покупок:\n'

        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list += f'\n{name} - {amount}/{unit}'

        file_name = f"{user}_shopping_cart.txt"
        response = HttpResponse(shopping_list, content_type="text/plain")
        response["Content-Disposition"] = f"attachment; filename={file_name}"
        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link'
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not recipe.link:
            recipe.link = ''.join(
                random.choice(string.ascii_letters) for _ in range(3)
            )
            recipe.save()
        short_link = self.request.build_absolute_uri(
            reverse(
                'short_link',
                kwargs={'short_link': recipe.link}
            )
        )
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class ShortView(APIView):

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, link=short_link)
        return HttpResponseRedirect(f'/recipes/{recipe.id}')
