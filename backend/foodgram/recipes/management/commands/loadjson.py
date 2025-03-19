import json


class LoadJson:

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
                    f'{self.message} из фала {self.filename}.'
                )
        except Exception as e:
            print(f'Ошибка: {e}')
