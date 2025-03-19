from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from .loadjson import LoadJson


class Command(LoadJson, BaseCommand):

    filename = 'ingredients.json'
    model = Ingredient
    message = 'продуктов'
