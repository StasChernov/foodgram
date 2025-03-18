import csv
import logging

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        filename = 'ingredients.csv'
        try:
            with open(f'data/{filename}', 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',')
                ingredients = [Ingredient(
                    name=name, measurement_unit=unit
                ) for name, unit in reader]
                amount = len(Ingredient.objects.bulk_create(
                    ingredients, ignore_conflicts=True
                ))
                print(f'Добавлено {amount} продукта из фала {filename}.')
        except FileNotFoundError:
            print(f'Запрашиваемый файл {filename} не найден')
