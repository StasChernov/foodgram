from datetime import datetime


def cart_render(ingredients, recipes):
    date = datetime.now().strftime('%Y-%m-%d')
    list_header = f'Список покупок от: {date}'
    ingredient_header = 'Список продуктов:'
    recipe_header = 'Для рецептов:'
    products_list = [(
        f'{i} {ingredient["ingredient__name"]} - '
        f'{ingredient["amount"]}/'
        f'{ingredient["ingredient__measurement_unit"]}'
    )
        for i, ingredient in enumerate(ingredients, start=1)
    ]
    recipes_list = [(
        f'{i} {recipe["recipe__name"]} '
        f'от {recipe["recipe__author__first_name"]} '
        f'{recipe["recipe__author__last_name"]}'
    )
        for i, recipe in enumerate(recipes, start=1)
    ]
    return '\n'.join([
        list_header,
        ingredient_header,
        *products_list,
        recipe_header,
        *recipes_list
    ])
