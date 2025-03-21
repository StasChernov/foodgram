from recipes.models import Ingredient
from .loadjson import LoadJson


class Command(LoadJson):

    filename = 'ingredients.json'
    model = Ingredient
