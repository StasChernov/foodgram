import re

from rest_framework.exceptions import ValidationError


def username_validator(username):
    if re.search(r'^[\w.@+-]+\Z', username) is None:
        raise ValidationError(
            'Недопустимое имя пользователя.'
        )


def amount_validator(amount):
    if amount <= 0:
        raise ValidationError(
            'Неверное количество продукта.'
        )


def cooking_time_validator(cooking_time):
    print(cooking_time)
    if int(cooking_time) <= 0:
        raise ValidationError('Время готовки должно быть больше 0.')
