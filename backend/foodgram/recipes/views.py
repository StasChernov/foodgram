from django.shortcuts import redirect
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe


def short_link(request, id):
    if Recipe.objects.filter(id=id).exists():
        return redirect(f'/recipes/{id}')
    raise ValidationError(f'Рецепта с id {id} не существует!')
