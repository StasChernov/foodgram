from datetime import datetime

PRODUCT = '{} {} - {}/{}'
RECIPE = '{} {} от {}'


def cart_render(ingredients, recipes):
    date = datetime.now().strftime('%Y-%m-%d')
    list_header = f'Список покупок от: {date}'
    ingredient_header = 'Список продуктов:'
    recipe_header = 'Для рецептов:'
    products_list = [(
        PRODUCT.format(
            i,
            ingredient['ingredient__name'],
            ingredient['amount'],
            ingredient['ingredient__measurement_unit']
        )
    )
        for i, ingredient in enumerate(ingredients, start=1)
    ]
    recipes_list = [(
        RECIPE.format(
            i,
            recipe['recipe__name'],
            recipe['recipe__author__username']
        )
    )
        for i, recipe in enumerate(
            recipes.values(
                'recipe__name', 'recipe__author__username'
            )
            .distinct()
            .order_by('recipe__name'),
            start=1)
    ]
    return '\n'.join([
        list_header,
        ingredient_header,
        *products_list,
        recipe_header,
        *recipes_list
    ])
