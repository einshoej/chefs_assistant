"""
Examples demonstrating the Recipe-as-Ingredient functionality.

This module shows how to create recipes that produce ingredients for other recipes,
and how to use those ingredient-producing recipes in complex dishes.
"""

from recipe import Recipe, create_basic_recipe, DifficultyLevel, MealType
from recipe_produced_ingredients import create_recipe_produced_ingredients
from ingredient import Ingredient
from typing import Dict


def create_pizza_dough_recipe() -> Recipe:
    """
    Create a recipe for pizza dough that produces the 'pizza_dough' ingredient.

    Returns:
        Recipe instance configured to produce pizza dough
    """
    recipe = Recipe(
        name_no="Pizzadeig",
        name_en="Pizza Dough",
        description_no="Enkel og deilig pizzadeig som kan brukes til alle typer pizza",
        description_en="Simple and delicious pizza dough that can be used for all types of pizza",
        prep_time_minutes=15,
        rest_time_minutes=60,  # Rising time
        servings=4,  # Makes 4 individual pizzas
        yield_amount=1200.0,  # Total dough weight in grams
        yield_unit="g",
        difficulty=DifficultyLevel.EASY,
        categories=["Grunnoppskrifter", "Italiensk"],
        tags=["vegetar", "grunnoppskrift", "pizza"]
    )

    # Add ingredients for the dough
    recipe.add_ingredient("flour", "500", "g", "", "type 00 eller vanlig hvetemel")
    recipe.add_ingredient("water", "320", "ml", "lunken", "")
    recipe.add_ingredient("olive_oil", "2", "ss", "", "")
    recipe.add_ingredient("salt", "1", "ts", "", "")
    recipe.add_ingredient("dry_yeast", "7", "g", "", "1 pakke tørrgjær")

    # Add preparation steps
    recipe.add_step(
        "Bland mel og salt i en stor bolle.",
        "Mix flour and salt in a large bowl."
    )
    recipe.add_step(
        "Løs opp gjæren i det lunkne vannet og la stå i 5 minutter.",
        "Dissolve yeast in lukewarm water and let stand for 5 minutes."
    )
    recipe.add_step(
        "Hell gjærvann og olivenolje i melblandingen. Bland til en jevn deig.",
        "Pour yeast water and olive oil into flour mixture. Mix until smooth dough forms."
    )
    recipe.add_step(
        "Kna deigen på melstrødd bord i 8-10 minutter til den er smidig.",
        "Knead dough on floured surface for 8-10 minutes until smooth."
    )
    recipe.add_step(
        "Legg deigen i en oljesmurt bolle, dekk til og la heve i 1 time.",
        "Place dough in oiled bowl, cover and let rise for 1 hour."
    )

    # Configure as ingredient producer
    recipe.set_as_ingredient_producer(
        ingredient_id="pizza_dough",
        yield_amount=1200.0,
        yield_unit="g"
    )

    return recipe


def create_tomato_sauce_recipe() -> Recipe:
    """
    Create a recipe for tomato sauce that produces the 'tomato_sauce' ingredient.

    Returns:
        Recipe instance configured to produce tomato sauce
    """
    recipe = Recipe(
        name_no="Enkel tomatsaus",
        name_en="Simple Tomato Sauce",
        description_no="Grunnleggende tomatsaus perfekt til pizza og pasta",
        description_en="Basic tomato sauce perfect for pizza and pasta",
        prep_time_minutes=10,
        cook_time_minutes=20,
        servings=0,  # This is a component, not a dish
        yield_amount=500.0,  # Makes about 500ml sauce
        yield_unit="ml",
        difficulty=DifficultyLevel.EASY,
        categories=["Grunnoppskrifter", "Dressing/dip/saus/vinaigrette"],
        tags=["vegetar", "grunnoppskrift", "saus"]
    )

    # Add ingredients for the sauce
    recipe.add_ingredient("canned_tomatoes", "400", "g", "knuste", "1 boks")
    recipe.add_ingredient("garlic", "2", "fedd", "hakket", "")
    recipe.add_ingredient("olive_oil", "2", "ss", "", "")
    recipe.add_ingredient("onion", "0.5", "stk", "finhakket", "liten løk")
    recipe.add_ingredient("salt", "", "etter smak", "", "")
    recipe.add_ingredient("black_pepper", "", "etter smak", "", "")
    recipe.add_ingredient("dried_oregano", "1", "ts", "", "", optional=True)
    recipe.add_ingredient("sugar", "1", "ts", "", "for å balansere syre", optional=True)

    # Add preparation steps
    recipe.add_step(
        "Varm olivenolje i en kasserolle på middels varme.",
        "Heat olive oil in a saucepan over medium heat."
    )
    recipe.add_step(
        "Stek løk og hvitløk til de er myke, ca 3-4 minutter.",
        "Sauté onion and garlic until soft, about 3-4 minutes."
    )
    recipe.add_step(
        "Tilsett knuste tomater og krydder. Kok opp.",
        "Add crushed tomatoes and seasonings. Bring to boil."
    )
    recipe.add_step(
        "La sausen småkoke i 15-20 minutter til den tykner.",
        "Simmer for 15-20 minutes until sauce thickens."
    )
    recipe.add_step(
        "Smak til med salt, pepper og sukker etter behov.",
        "Season with salt, pepper and sugar to taste."
    )

    # Configure as ingredient producer
    recipe.set_as_ingredient_producer(
        ingredient_id="tomato_sauce",
        yield_amount=500.0,
        yield_unit="ml"
    )

    return recipe


def create_margherita_pizza_recipe(ingredient_library: Dict[str, Ingredient]) -> Recipe:
    """
    Create a Margherita pizza recipe that uses recipe-produced ingredients.

    Args:
        ingredient_library: Library containing all ingredients including recipe-produced ones

    Returns:
        Recipe that uses pizza_dough and tomato_sauce as ingredients
    """
    recipe = Recipe(
        name_no="Pizza Margherita",
        name_en="Margherita Pizza",
        description_no="Klassisk italiensk pizza med tomatsaus, mozzarella og basilikum",
        description_en="Classic Italian pizza with tomato sauce, mozzarella and basil",
        prep_time_minutes=15,
        cook_time_minutes=12,
        servings=4,
        difficulty=DifficultyLevel.MEDIUM,
        meal_type=MealType.DINNER,
        categories=["Pizza", "Italiensk", "Middag"],
        tags=["vegetar", "klassisk"]
    )

    # Use recipe-produced ingredients
    recipe.add_ingredient(
        ingredient_id="pizza_dough",
        quantity="1200",
        unit="g",
        note="fra pizzadeig-oppskrift"
    )
    recipe.add_ingredient(
        ingredient_id="tomato_sauce",
        quantity="400",
        unit="ml",
        note="fra tomatsaus-oppskrift"
    )

    # Add regular ingredients
    recipe.add_ingredient("mozzarella_cheese", "300", "g", "revet", "fersk mozzarella")
    recipe.add_ingredient("fresh_basil", "20", "g", "friske blader", "")
    recipe.add_ingredient("parmesan_cheese", "50", "g", "revet", "", optional=True)
    recipe.add_ingredient("olive_oil", "2", "ss", "ekstra virgin", "for drypping")

    # Add preparation steps
    recipe.add_step(
        "Varm ovnen til 250°C (eller høyeste innstilling).",
        "Preheat oven to 250°C (or highest setting).",
        temperature_celsius=250
    )
    recipe.add_step(
        "Del pizzadeigen i 4 deler. Rull ut hver del til tynn bunn.",
        "Divide pizza dough into 4 parts. Roll each part into thin base."
    )
    recipe.add_step(
        "Smør tomatsaus utover pizzabunnene, la 2 cm kant rundt.",
        "Spread tomato sauce over pizza bases, leaving 2cm border."
    )
    recipe.add_step(
        "Fordel mozzarella jevnt over sausen.",
        "Distribute mozzarella evenly over sauce."
    )
    recipe.add_step(
        "Stek pizzaene i ovnen 10-12 minutter til bunnen er gylden.",
        "Bake pizzas for 10-12 minutes until base is golden.",
        time_minutes=11
    )
    recipe.add_step(
        "Pynt med fersk basilikum og drypp med olivenolje før servering.",
        "Garnish with fresh basil and drizzle with olive oil before serving."
    )

    # Load ingredient information from library
    recipe.load_ingredients(ingredient_library)

    return recipe


def demonstrate_recipe_ingredient_workflow():
    """
    Demonstrate the complete workflow of recipe-as-ingredient functionality.
    """
    print("=== Recipe-as-Ingredient Workflow Demo ===\n")

    # Step 1: Create ingredient library including recipe-produced ingredients
    print("1. Creating ingredient library...")
    recipe_ingredients = create_recipe_produced_ingredients()
    print(f"   Created {len(recipe_ingredients)} recipe-produced ingredients\n")

    # Step 2: Create component recipes
    print("2. Creating component recipes...")
    pizza_dough_recipe = create_pizza_dough_recipe()
    tomato_sauce_recipe = create_tomato_sauce_recipe()

    print(f"   Pizza Dough Recipe: {pizza_dough_recipe.get_name()}")
    print(f"     - Produces ingredient: {pizza_dough_recipe.produced_ingredient_id}")
    print(f"     - Yield: {pizza_dough_recipe.yield_amount} {pizza_dough_recipe.yield_unit}")
    print(f"     - Is ingredient producer: {pizza_dough_recipe.is_ingredient_producer()}")

    print(f"   Tomato Sauce Recipe: {tomato_sauce_recipe.get_name()}")
    print(f"     - Produces ingredient: {tomato_sauce_recipe.produced_ingredient_id}")
    print(f"     - Yield: {tomato_sauce_recipe.yield_amount} {tomato_sauce_recipe.yield_unit}")
    print(f"     - Is ingredient producer: {tomato_sauce_recipe.is_ingredient_producer()}")
    print()

    # Step 3: Create final recipe that uses recipe-produced ingredients
    print("3. Creating final recipe using component ingredients...")
    margherita_recipe = create_margherita_pizza_recipe(recipe_ingredients)

    print(f"   Margherita Pizza Recipe: {margherita_recipe.get_name()}")
    print("   Ingredients:")
    for recipe_ingredient in margherita_recipe.recipe_ingredients:
        ingredient_type = "recipe-produced" if recipe_ingredient.ingredient_id in recipe_ingredients else "regular"
        print(f"     - {recipe_ingredient.get_display_text()} ({ingredient_type})")
    print()

    # Step 4: Show ingredient production info
    print("4. Ingredient production information:")
    for recipe in [pizza_dough_recipe, tomato_sauce_recipe]:
        info = recipe.get_produced_ingredient_info()
        if info:
            print(f"   {info['recipe_name']} produces:")
            print(f"     - Ingredient: {info['ingredient_id']}")
            print(f"     - Amount: {info['yield_amount']} {info['yield_unit']}")
    print()

    # Step 5: Show recipe relationships
    print("5. Recipe dependency relationships:")
    print("   Margherita Pizza depends on:")
    for recipe_ingredient in margherita_recipe.recipe_ingredients:
        if recipe_ingredient.ingredient_id in recipe_ingredients:
            print(f"     - {recipe_ingredient.ingredient_id} (from recipe)")
    print()

    print("   Component recipes:")
    for recipe in [pizza_dough_recipe, tomato_sauce_recipe]:
        if recipe.is_ingredient_producer():
            print(f"     - {recipe.get_name()} → {recipe.produced_ingredient_id}")


if __name__ == "__main__":
    demonstrate_recipe_ingredient_workflow()