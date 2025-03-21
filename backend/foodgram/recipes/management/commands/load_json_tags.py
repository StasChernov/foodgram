from recipes.models import Tag
from .loadjson import LoadJson


class Command(LoadJson):

    filename = 'tags.json'
    model = Tag
