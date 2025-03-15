import csv
import logging

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/ingredients.csv', 'r', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")
            ingredients = []
            for row in reader:
                name, unit = row
                if name:
                    ingredient = Ingredient(name=name, measurement_unit=unit)
                    ingredients.append(ingredient)
            Ingredient.objects.bulk_create(ingredients)
            print('All data downloaded.')
