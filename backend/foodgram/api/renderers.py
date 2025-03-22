from datetime import datetime

PRODUCT = '{count} {name} - {amount}/{unit}'
RECIPE = '{count} {name} от {username}'


def cart_render(ingredients, recipe_ingredient):
    date = datetime.now().strftime('%Y-%m-%d')
    list_header = f'Список покупок от: {date}'
    ingredient_header = 'Список продуктов:'
    recipe_header = 'Для рецептов:'
    products_list = [(
        PRODUCT.format(
            count=i,
            name=ingredient['ingredient__name'].capitalize(),
            amount=ingredient['amount'],
            unit=ingredient['ingredient__measurement_unit']
        )
    )
        for i, ingredient in enumerate(ingredients, start=1)
    ]
    recipes_list = [(
        RECIPE.format(
            count=i,
            name=recipe_ingredient['recipe__name'],
            username=recipe_ingredient['recipe__author__username']
        )
    )
        for i, recipe_ingredient in enumerate(
            recipe_ingredient.values(
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
