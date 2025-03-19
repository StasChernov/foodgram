from django.core.management.base import BaseCommand

from recipes.models import Tag
from .loadjson import LoadJson


class Command(LoadJson, BaseCommand):

    filename = 'tags.json'
    model = Tag
    message = 'тегов'
