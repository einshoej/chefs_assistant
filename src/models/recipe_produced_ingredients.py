"""
Recipe-produced ingredients for the Chef's Assistant ingredient library.

This module defines ingredients that are typically made from recipes rather than
bought directly - like pizza dough, sauces, stocks, etc.
"""

from ingredient import Ingredient, create_basic_ingredient, StorageType, Season, NutritionInfo, PriceInfo
from typing import Dict


def create_recipe_produced_ingredients() -> Dict[str, Ingredient]:
    """
    Create a library of ingredients that are typically produced by recipes.

    Returns:
        Dictionary mapping ingredient ID to Ingredient for recipe-produced items
    """
    ingredients = {}

    # === DOUGHS AND BASES ===

    # Pizza dough
    pizza_dough = Ingredient(
        ingredient_id="pizza_dough",
        name_no="Pizzadeig",
        name_en="Pizza Dough",
        category="grain",
        typical_weight_grams=300.0,  # Enough for one pizza
        density=1.2,  # Slightly denser than water
        edible_portion=1.0,
        common_units=['g', 'kg', 'ball', 'portion'],
        preparation_methods=[
            {'no': 'hel deigball', 'en': 'whole dough ball'},
            {'no': 'uttrukket', 'en': 'rolled out'},
            {'no': 'ferdig bunn', 'en': 'prepared base'}
        ],
        nutrition={
            'calories': 290,
            'protein': 9.5,
            'carbs': 58.0,
            'fat': 2.5,
            'fiber': 2.0,
            'sugar': 1.0
        },
        flavor_profile=['neutral', 'slightly yeasty'],
        texture='elastic',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=3,
        available_year_round=True
    )
    ingredients["pizza_dough"] = pizza_dough

    # Pasta dough
    pasta_dough = Ingredient(
        ingredient_id="pasta_dough",
        name_no="Pastadeig",
        name_en="Pasta Dough",
        category="grain",
        typical_weight_grams=400.0,  # Serves 4
        common_units=['g', 'kg', 'portion'],
        preparation_methods=[
            {'no': 'hel deigball', 'en': 'whole dough ball'},
            {'no': 'utvalset', 'en': 'rolled out'},
            {'no': 'skåret til pasta', 'en': 'cut into pasta'}
        ],
        nutrition={
            'calories': 310,
            'protein': 12.0,
            'carbs': 60.0,
            'fat': 3.0,
            'fiber': 2.5
        },
        flavor_profile=['neutral', 'eggy'],
        texture='smooth',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=2
    )
    ingredients["pasta_dough"] = pasta_dough

    # Pie crust
    pie_crust = Ingredient(
        ingredient_id="pie_crust",
        name_no="Paibunn",
        name_en="Pie Crust",
        category="grain",
        typical_weight_grams=250.0,  # One crust
        common_units=['g', 'crust', 'portion'],
        preparation_methods=[
            {'no': 'rå deig', 'en': 'raw dough'},
            {'no': 'utvalset', 'en': 'rolled out'},
            {'no': 'forbakt', 'en': 'pre-baked'}
        ],
        nutrition={
            'calories': 450,
            'protein': 6.0,
            'carbs': 45.0,
            'fat': 28.0,
            'fiber': 2.0
        },
        flavor_profile=['buttery', 'neutral'],
        texture='flaky',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=3
    )
    ingredients["pie_crust"] = pie_crust

    # === SAUCES ===

    # Tomato sauce
    tomato_sauce = Ingredient(
        ingredient_id="tomato_sauce",
        name_no="Tomatsaus",
        name_en="Tomato Sauce",
        category="sauce",
        typical_weight_grams=500.0,  # About 2 cups
        density=1.05,
        common_units=['ml', 'dl', 'l', 'cup'],
        preparation_methods=[
            {'no': 'glatt saus', 'en': 'smooth sauce'},
            {'no': 'chunky saus', 'en': 'chunky sauce'}
        ],
        nutrition={
            'calories': 35,
            'protein': 2.0,
            'carbs': 7.0,
            'fat': 0.5,
            'fiber': 1.5,
            'sugar': 5.0,
            'vitamins': {'C': 18.0, 'A': 900},
            'minerals': {'potassium': 250}
        },
        flavor_profile=['tangy', 'savory', 'umami'],
        texture='smooth',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=5,
        peak_season=[Season.SUMMER, Season.FALL],
        available_year_round=True
    )
    ingredients["tomato_sauce"] = tomato_sauce

    # Béchamel sauce
    bechamel_sauce = Ingredient(
        ingredient_id="bechamel_sauce",
        name_no="Béchamelsaus",
        name_en="Béchamel Sauce",
        category="sauce",
        typical_weight_grams=400.0,
        common_units=['ml', 'dl', 'cup'],
        preparation_methods=[
            {'no': 'tynn konsistens', 'en': 'thin consistency'},
            {'no': 'medium konsistens', 'en': 'medium consistency'},
            {'no': 'tykk konsistens', 'en': 'thick consistency'}
        ],
        nutrition={
            'calories': 150,
            'protein': 4.0,
            'carbs': 8.0,
            'fat': 12.0,
            'fiber': 0.2
        },
        flavor_profile=['creamy', 'mild', 'buttery'],
        texture='smooth',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=3
    )
    ingredients["bechamel_sauce"] = bechamel_sauce

    # Pesto
    pesto = Ingredient(
        ingredient_id="basil_pesto",
        name_no="Basilikumpesto",
        name_en="Basil Pesto",
        category="sauce",
        typical_weight_grams=200.0,  # About 3/4 cup
        common_units=['g', 'ml', 'tbsp', 'cup'],
        preparation_methods=[
            {'no': 'grov konsistens', 'en': 'coarse texture'},
            {'no': 'glatt konsistens', 'en': 'smooth texture'}
        ],
        nutrition={
            'calories': 260,
            'protein': 4.0,
            'carbs': 3.0,
            'fat': 26.0,
            'fiber': 1.0,
            'vitamins': {'A': 350, 'K': 25},
            'minerals': {'calcium': 60}
        },
        flavor_profile=['herbaceous', 'garlicky', 'nutty', 'rich'],
        texture='chunky',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=7,
        peak_season=[Season.SUMMER]
    )
    ingredients["basil_pesto"] = pesto

    # === STOCKS AND BROTHS ===

    # Vegetable stock
    vegetable_stock = Ingredient(
        ingredient_id="vegetable_stock",
        name_no="Grønnsaksbuljong",
        name_en="Vegetable Stock",
        category="liquid",
        typical_weight_grams=1000.0,  # 1 liter
        density=1.02,
        common_units=['ml', 'dl', 'l', 'cup'],
        nutrition={
            'calories': 12,
            'protein': 0.5,
            'carbs': 3.0,
            'fat': 0.1,
            'sodium': 600  # Can vary significantly
        },
        flavor_profile=['savory', 'vegetable', 'umami'],
        texture='liquid',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=5,
        available_year_round=True
    )
    ingredients["vegetable_stock"] = vegetable_stock

    # Chicken stock
    chicken_stock = Ingredient(
        ingredient_id="chicken_stock",
        name_no="Kyllingbuljong",
        name_en="Chicken Stock",
        category="liquid",
        typical_weight_grams=1000.0,  # 1 liter
        density=1.03,
        common_units=['ml', 'dl', 'l', 'cup'],
        nutrition={
            'calories': 38,
            'protein': 5.0,
            'carbs': 3.0,
            'fat': 1.0,
            'sodium': 850
        },
        flavor_profile=['rich', 'savory', 'chicken', 'umami'],
        texture='liquid',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=4,
        available_year_round=True
    )
    ingredients["chicken_stock"] = chicken_stock

    # === PASTA TYPES ===

    # Fresh pasta (generic)
    fresh_pasta = Ingredient(
        ingredient_id="fresh_pasta",
        name_no="Fersk pasta",
        name_en="Fresh Pasta",
        category="grain",
        typical_weight_grams=100.0,  # Per serving
        common_units=['g', 'portion', 'serving'],
        preparation_methods=[
            {'no': 'kokt', 'en': 'cooked'},
            {'no': 'rå', 'en': 'raw'}
        ],
        nutrition={
            'calories': 290,
            'protein': 11.0,
            'carbs': 55.0,
            'fat': 2.5,
            'fiber': 3.0
        },
        flavor_profile=['neutral', 'wheat'],
        texture='tender',
        cooking_methods=['boiled'],
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=2
    )
    ingredients["fresh_pasta"] = fresh_pasta

    # === DESSERT COMPONENTS ===

    # Pastry cream
    pastry_cream = Ingredient(
        ingredient_id="pastry_cream",
        name_no="Konditorkrem",
        name_en="Pastry Cream",
        category="dairy",
        typical_weight_grams=300.0,
        common_units=['ml', 'dl', 'g', 'cup'],
        preparation_methods=[
            {'no': 'kald', 'en': 'chilled'},
            {'no': 'varm', 'en': 'warm'}
        ],
        nutrition={
            'calories': 180,
            'protein': 4.5,
            'carbs': 20.0,
            'fat': 9.0,
            'sugar': 18.0
        },
        flavor_profile=['sweet', 'vanilla', 'creamy'],
        texture='smooth',
        storage_type=StorageType.REFRIGERATED,
        shelf_life_days=2
    )
    ingredients["pastry_cream"] = pastry_cream

    return ingredients


def get_recipe_ingredient_categories():
    """
    Get categories that typically contain recipe-produced ingredients.

    Returns:
        List of category names where recipes often produce ingredients
    """
    return [
        "Grunnoppskrifter",  # Base recipes
        "Dressing/dip/saus/vinaigrette",  # Sauces and dressings
        "Bakverk",  # Baking (for doughs and crusts)
    ]


def create_recipe_to_ingredient_mapping():
    """
    Create suggested mappings between recipe categories and ingredient production.

    Returns:
        Dictionary with suggested ingredient IDs for different recipe types
    """
    return {
        # Dough recipes
        "pizza": "pizza_dough",
        "pizzadeig": "pizza_dough",
        "pasta": "fresh_pasta",
        "pastadeig": "pasta_dough",
        "pai": "pie_crust",
        "terte": "pie_crust",

        # Sauce recipes
        "tomatsaus": "tomato_sauce",
        "pesto": "basil_pesto",
        "bechamel": "bechamel_sauce",
        "béchamel": "bechamel_sauce",

        # Stock/broth recipes
        "buljong": "vegetable_stock",
        "kraft": "chicken_stock",
        "stock": "vegetable_stock",

        # Dessert components
        "konditorkrem": "pastry_cream",
        "vaniljekrem": "pastry_cream"
    }


if __name__ == "__main__":
    print("=== Recipe-Produced Ingredients ===")

    ingredients = create_recipe_produced_ingredients()
    print(f"Created {len(ingredients)} recipe-produced ingredients:")

    for ingredient_id, ingredient in ingredients.items():
        print(f"\n{ingredient_id}:")
        print(f"  Name: {ingredient.get_name('no')} / {ingredient.get_name('en')}")
        print(f"  Category: {ingredient.category}")
        print(f"  Typical weight: {ingredient.typical_weight_grams}g")
        print(f"  Storage: {ingredient.storage_type.value}")
        print(f"  Shelf life: {ingredient.shelf_life_days} days")
        if ingredient.flavor_profile:
            print(f"  Flavor: {', '.join(ingredient.flavor_profile)}")

    print(f"\n=== Recipe Categories for Ingredient Production ===")
    categories = get_recipe_ingredient_categories()
    for category in categories:
        print(f"  - {category}")

    print(f"\n=== Recipe Name to Ingredient Mapping ===")
    mapping = create_recipe_to_ingredient_mapping()
    for recipe_keyword, ingredient_id in mapping.items():
        ingredient_name = ingredients[ingredient_id].get_name('no') if ingredient_id in ingredients else ingredient_id
        print(f"  {recipe_keyword} -> {ingredient_name}")