import json
import logging

from django.core.management.base import BaseCommand

from recipes.models import Tag

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        filename = 'tags.json'
        try:
            with open(f'data/{filename}', 'r', encoding='utf-8') as file:
                reader = json.load(file)
                tags = [
                    Tag(**tag) for tag in reader
                ]
                amount = len(Tag.objects.bulk_create(
                    tags, ignore_conflicts=True
                ))
                print(f'Добавлено {amount} тэгов из фала {filename}.')
        except FileNotFoundError:
            print(f'Запрашиваемый файл {filename} не найден')
