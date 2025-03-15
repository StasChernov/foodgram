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
from api.serializers import (AvatarSerializer, IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeViewSerializer, SubscribeCreateSerializer,
                             SubscribeViewSerializer, TagSerializer,
                             UserRecipeSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscribe, Tag, User)


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
        methods=['GET'],
        detail=False,
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
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=self.request.user)
        pages = self.paginate_queryset(queryset)
        return self.get_paginated_response(
            SubscribeViewSerializer(
                pages, many=True, context={'request': request},
            ).data
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = SubscribeCreateSerializer(
                data={'user': request.user.id, 'author': author.id},
                context={'request': request},
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        else:
            subscriptions_count, _ = request.user.subscriptions.filter(
                author=author
            ).delete()
            print(subscriptions_count)
            if subscriptions_count:
                return Response(status=status.HTTP_204_NO_CONTENT)    
            return Response(
                {'error': 'Нет подписки на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RecipeViewSet(ModelViewSet):

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeViewSerializer
        return RecipeCreateUpdateSerializer

    def add_or_delete_recipe(self, request, model, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                raise ValidationError(
                    {'detail': 'Рецепт уже добавлен.'}
                )
            model.objects.create(recipe=recipe, user=request.user)
        else:
            deleted_recipes, _ = model.objects.filter(
                recipe=pk, user=request.user
            ).delete()
            if deleted_recipes == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            UserRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.add_or_delete_recipe(
            request, ShoppingCart, pk=pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
    )
    def favorite(self, request, pk):
        return self.add_or_delete_recipe(
            request, Favorite, pk=pk
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
            .select_related('ingredient')
        )
        shopping_list = {}
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name in shopping_list:
                shopping_list[name]['amount'] += amount
            else:
                shopping_list[name] = {
                    'amount': amount,
                    'measurement_unit': measurement_unit
                }
        print(shopping_list)
        file_content = 'Список покупок:\n'
        for item, content in shopping_list.items():
            print(item, content)
            file_content += ( 
                f'\n{item} - {content["amount"]}/{content["measurement_unit"]}'
            )
        file_name = f'{user} shopping_cart.txt'
        response = HttpResponse(file_content, content_type="text/plain")
        response['Content-Disposition'] = f'attachment; filename={file_name}'
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
        print('')
        recipe = get_object_or_404(Recipe, link=short_link)
        return HttpResponseRedirect(f'/recipes/{recipe.id}')
