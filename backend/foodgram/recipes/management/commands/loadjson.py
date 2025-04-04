import json

from django.core.management.base import BaseCommand


class LoadJson(BaseCommand):

    def handle(self, *args, **options):
        try:
            with open(f'data/{self.filename}', 'r', encoding='utf-8') as file:
                reader = json.load(file)
                items = [
                    self.model(**item) for item in reader
                ]
                amount = len(self.model.objects.bulk_create(
                    items, ignore_conflicts=True
                ))
                print(
                    f'Добавлено {amount} '
                    f'{self.model._meta.verbose_name} '
                    f'из файла {self.filename}.'
                )
        except Exception as e:
            print(f'Ошибка при работе с файлом {self.filename}: {e}')
