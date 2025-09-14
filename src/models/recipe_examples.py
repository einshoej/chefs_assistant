"""
Example usage of the Recipe class for the Chef's Assistant recipe management system.

This file demonstrates how to create and use recipes that integrate with the ingredient catalog,
showing various levels of complexity and functionality.
"""

from recipe import Recipe, RecipeIngredient, RecipeStep, RecipePhoto, DifficultyLevel, MealType
from ingredient import Ingredient, create_vegetable_ingredient, create_basic_ingredient, Season, StorageType
import json


def create_sample_ingredient_library():
    """Create a sample ingredient library for recipe examples"""
    
    library = {}
    
    # Vegetables
    carrot = create_vegetable_ingredient("carrot", "Gulrot", "Carrot", 100)
    carrot.set_nutrition(calories=41, protein=0.9, carbs=9.6, fat=0.2, fiber=2.8)
    carrot.nutrition.vitamins = {'A': 835, 'C': 5.9, 'K': 13.2}
    carrot.update_price_info(average_price_per_kg=15.00)
    library["carrot"] = carrot
    
    onion = create_vegetable_ingredient("onion", "Løk", "Onion", 150)
    onion.set_nutrition(calories=40, protein=1.1, carbs=9.3, fat=0.1)
    onion.update_price_info(average_price_per_kg=12.00)
    library["onion"] = onion
    
    potato = create_vegetable_ingredient("potato", "Potet", "Potato", 200)
    potato.set_nutrition(calories=77, protein=2.0, carbs=17.5, fat=0.1)
    potato.update_price_info(average_price_per_kg=8.00)
    library["potato"] = potato
    
    celery = create_vegetable_ingredient("celery", "Selleri", "Celery", 40)
    celery.set_nutrition(calories=16, protein=0.7, carbs=3.0, fat=0.2)
    celery.update_price_info(average_price_per_kg=25.00)
    library["celery"] = celery
    
    # Proteins
    chicken_breast = Ingredient(
        ingredient_id="chicken_breast",
        name_no="Kyllingbryst",
        name_en="Chicken Breast",
        category="meat",
        typical_weight_grams=200,
        storage_type=StorageType.REFRIGERATED,
        common_units=['stk', 'g', 'kg'],
        nutrition={
            'calories': 165,
            'protein': 31.0,
            'fat': 3.6,
            'carbs': 0.0
        },
        price_info={
            'average_price_per_kg': 159.00
        }
    )
    library["chicken_breast"] = chicken_breast
    
    # Pantry items
    olive_oil = create_basic_ingredient("olive_oil", "Olivenolje", "Olive Oil", "oil")
    olive_oil.typical_weight_grams = 15  # Per tablespoon
    olive_oil.storage_type = StorageType.PANTRY
    olive_oil.set_nutrition(calories=884, fat=100.0)
    olive_oil.update_price_info(average_price_per_kg=120.00)
    library["olive_oil"] = olive_oil
    
    salt = create_basic_ingredient("salt", "Salt", "Salt", "seasoning")
    salt.typical_weight_grams = 5  # Per teaspoon
    salt.storage_type = StorageType.PANTRY
    salt.update_price_info(average_price_per_kg=15.00)
    library["salt"] = salt
    
    black_pepper = create_basic_ingredient("black_pepper", "Sort pepper", "Black Pepper", "seasoning")
    black_pepper.typical_weight_grams = 2  # Per teaspoon
    black_pepper.storage_type = StorageType.PANTRY
    black_pepper.update_price_info(average_price_per_kg=200.00)
    library["black_pepper"] = black_pepper
    
    # Liquids
    chicken_stock = create_basic_ingredient("chicken_stock", "Kyllingbuljong", "Chicken Stock", "liquid")
    chicken_stock.typical_weight_grams = 1000  # Per liter
    chicken_stock.storage_type = StorageType.PANTRY
    chicken_stock.set_nutrition(calories=8, protein=1.0)
    chicken_stock.update_price_info(average_price_per_kg=25.00)
    library["chicken_stock"] = chicken_stock
    
    water = create_basic_ingredient("water", "Vann", "Water", "liquid")
    water.typical_weight_grams = 1000  # Per liter
    water.storage_type = StorageType.PANTRY
    library["water"] = water
    
    return library


def create_simple_recipe():
    """Create a simple recipe with minimal information"""
    
    recipe = Recipe(
        name_no="Enkel salat",
        name_en="Simple Salad",
        servings=2,
        difficulty=DifficultyLevel.EASY,
        meal_type=MealType.SIDE_DISH
    )
    
    # Add ingredients
    recipe.add_ingredient("carrot", quantity="1", unit="stk", preparation="revet")
    recipe.add_ingredient("onion", quantity="1/2", unit="stk", preparation="finhakket", optional=True)
    recipe.add_ingredient("olive_oil", quantity="2", unit="ss")
    recipe.add_ingredient("salt", note="etter smak")
    
    # Add preparation steps
    recipe.add_step("Riv gulroten grovt.", "Grate the carrot coarsely.")
    recipe.add_step("Hakk løken fint hvis du bruker den.", "Finely chop the onion if using.")
    recipe.add_step("Bland alt sammen og smak til med salt.", "Mix everything together and season with salt to taste.")
    
    return recipe


def create_detailed_recipe():
    """Create a more complex recipe with detailed information"""
    
    recipe = Recipe(
        name_no="Klassisk kyllingsuppe",
        name_en="Classic Chicken Soup",
        description_no="En varmende og næringsrik kyllingsuppe perfekt for kalde dager.",
        description_en="A warming and nutritious chicken soup perfect for cold days.",
        servings=4,
        prep_time_minutes=15,
        cook_time_minutes=45,
        difficulty=DifficultyLevel.MEDIUM,
        meal_type=MealType.DINNER,
        cuisine="Skandinavisk",
        categories=["Suppe", "Comfort Food", "Familie"],
        tags=["vinter", "sunn", "enkel"],
        seasons=[Season.FALL, Season.WINTER],
        rating=4.5,
        source="Bestemors oppskriftbok",
        author="Bestemor"
    )
    
    # Add ingredients with groups
    recipe.add_ingredient("chicken_breast", quantity="300", unit="g", preparation="terninger", group="Hovedingredienser")
    recipe.add_ingredient("carrot", quantity="2", unit="stk", preparation="skåret i skiver", group="Hovedingredienser")
    recipe.add_ingredient("celery", quantity="2", unit="stilker", preparation="skåret", group="Hovedingredienser")
    recipe.add_ingredient("onion", quantity="1", unit="stk", preparation="hakket", group="Hovedingredienser")
    recipe.add_ingredient("potato", quantity="2", unit="stk", preparation="terninger", group="Hovedingredienser")
    
    recipe.add_ingredient("chicken_stock", quantity="1", unit="liter", group="Væske")
    recipe.add_ingredient("water", quantity="0.5", unit="liter", group="Væske")
    
    recipe.add_ingredient("salt", note="etter smak", group="Krydder")
    recipe.add_ingredient("black_pepper", note="etter smak", group="Krydder")
    
    # Add detailed preparation steps with timing
    recipe.add_step(
        "Skjær kyllingbrystet i terninger på ca. 2 cm.",
        "Cut the chicken breast into 2cm cubes.",
        time_minutes=5
    )
    
    recipe.add_step(
        "Skjær gulrøttene i skiver, selleri i biter, og hakk løken.",
        "Slice the carrots, cut the celery into pieces, and chop the onion.",
        time_minutes=10
    )
    
    recipe.add_step(
        "Varm olje i en stor kasserolle på middels varme.",
        "Heat oil in a large pot over medium heat.",
        time_minutes=2
    )
    
    recipe.add_step(
        "Stek kyllingterningene til de er gyllne på alle sider.",
        "Brown the chicken cubes on all sides.",
        time_minutes=5
    )
    
    recipe.add_step(
        "Tilsett løk, gulrot og selleri. Stek i 5 minutter.",
        "Add onion, carrot and celery. Cook for 5 minutes.",
        time_minutes=5
    )
    
    recipe.add_step(
        "Hell på kyllingbuljong og vann. Bring til koking.",
        "Pour in chicken stock and water. Bring to a boil.",
        time_minutes=5
    )
    
    recipe.add_step(
        "Tilsett poteterningene og la suppen småkoke i 20 minutter.",
        "Add the potato cubes and simmer for 20 minutes.",
        time_minutes=20
    )
    
    recipe.add_step(
        "Smak til med salt og pepper før servering.",
        "Season with salt and pepper before serving."
    )
    
    # Add a photo
    photo = RecipePhoto(
        url="https://example.com/chicken-soup.jpg",
        caption_no="Deilig varm kyllingsuppe",
        caption_en="Delicious warm chicken soup",
        is_primary=True
    )
    recipe.photos.append(photo)
    
    return recipe


def create_vegetarian_recipe():
    """Create a vegetarian recipe demonstrating dietary categories"""
    
    recipe = Recipe(
        name_no="Røsti med grønnsaker",
        name_en="Vegetable Rösti",
        description_no="Sprø potatkake med friske grønnsaker - perfekt vegetarisk måltid.",
        description_en="Crispy potato cake with fresh vegetables - perfect vegetarian meal.",
        servings=3,
        prep_time_minutes=20,
        cook_time_minutes=25,
        difficulty=DifficultyLevel.MEDIUM,
        meal_type=MealType.DINNER,
        cuisine="Sveitsisk",
        categories=["Vegetarisk", "Hovedrett"],
        tags=["sprø", "grønnsaker", "poteter"],
        rating=4.2,
        seasons=[Season.FALL, Season.WINTER]
    )
    
    # Add ingredients
    recipe.add_ingredient("potato", quantity="800", unit="g", preparation="revet grovt")
    recipe.add_ingredient("carrot", quantity="1", unit="stk", preparation="revet")
    recipe.add_ingredient("onion", quantity="1", unit="stk", preparation="finhakket")
    recipe.add_ingredient("olive_oil", quantity="3", unit="ss")
    recipe.add_ingredient("salt", quantity="1", unit="ts")
    recipe.add_ingredient("black_pepper", note="etter smak")
    
    # Add steps
    recipe.add_step(
        "Riv potetene grovt og press ut så mye væske som mulig.",
        "Coarsely grate the potatoes and squeeze out as much liquid as possible.",
        time_minutes=10
    )
    
    recipe.add_step(
        "Riv gulroten og hakk løken fint.",
        "Grate the carrot and finely chop the onion.",
        time_minutes=5
    )
    
    recipe.add_step(
        "Bland poteter, gulrot, løk, salt og pepper i en stor skål.",
        "Mix potatoes, carrot, onion, salt and pepper in a large bowl.",
        time_minutes=3
    )
    
    recipe.add_step(
        "Varm olivenolje i en stor stekepanne på middels-høy varme.",
        "Heat olive oil in a large frying pan over medium-high heat.",
        time_minutes=2
    )
    
    recipe.add_step(
        "Press potetblandingen ned i pannen til en jevn kake.",
        "Press the potato mixture down in the pan to form an even cake.",
        time_minutes=2,
        temperature_celsius=180
    )
    
    recipe.add_step(
        "Stek i 12-15 minutter til bunnen er gyllen og sprø.",
        "Cook for 12-15 minutes until the bottom is golden and crispy.",
        time_minutes=15
    )
    
    recipe.add_step(
        "Snu røstien forsiktig og stek den andre siden i 8-10 minutter.",
        "Carefully flip the rösti and cook the other side for 8-10 minutes.",
        time_minutes=10
    )
    
    return recipe


def demonstrate_recipe_usage():
    """Demonstrate various ways to use the Recipe class"""
    
    print("=== Creating Sample Ingredient Library ===")
    ingredient_library = create_sample_ingredient_library()
    print(f"Created ingredient library with {len(ingredient_library)} ingredients")
    
    print("\\n=== Creating Sample Recipes ===")
    
    # Create different types of recipes
    simple_salad = create_simple_recipe()
    chicken_soup = create_detailed_recipe()
    vegetable_rosti = create_vegetarian_recipe()
    
    recipes = [simple_salad, chicken_soup, vegetable_rosti]
    
    print("\\nCreated recipes:")
    for recipe in recipes:
        print(f"- {recipe}")
        print(f"  Servings: {recipe.servings}")
        print(f"  Total time: {recipe.get_total_time_minutes()} minutes")
        print(f"  Ingredients: {len(recipe.recipe_ingredients)}")
        print(f"  Steps: {len(recipe.preparation_steps)}")
        print()
    
    print("=== Loading Ingredients for Recipes ===")
    for recipe in recipes:
        recipe.load_ingredients(ingredient_library)
        print(f"Loaded ingredients for: {recipe.get_name()}")
    
    print("\\n=== Chicken Soup Details ===")
    print(f"Recipe: {chicken_soup.get_name('en')}")
    print(f"Description: {chicken_soup.get_description('en')}")
    print(f"Difficulty: {chicken_soup.difficulty.value}")
    print(f"Total time: {chicken_soup.get_total_time_minutes()} minutes")
    print(f"Estimated cost: {chicken_soup.estimate_cost():.2f} NOK")
    print(f"Cost per serving: {chicken_soup.get_cost_per_serving():.2f} NOK")
    
    print("\\nIngredients by group:")
    ingredients_by_group = {}
    for ing in chicken_soup.recipe_ingredients:
        group = ing.group or "Other"
        if group not in ingredients_by_group:
            ingredients_by_group[group] = []
        ingredients_by_group[group].append(ing)
    
    for group, ingredients in ingredients_by_group.items():
        print(f"\\n{group}:")
        for ing in ingredients:
            print(f"  - {ing.get_display_text('en')}")
    
    print("\\nPreparation steps:")
    for i, step in enumerate(chicken_soup.preparation_steps, 1):
        time_info = f" ({step.time_minutes} min)" if step.time_minutes else ""
        print(f"{i}. {step.get_instruction('en')}{time_info}")
    
    print("\\n=== Nutrition Calculation ===")
    nutrition = chicken_soup.calculate_nutrition_per_serving()
    if nutrition:
        print(f"Nutrition per serving:")
        print(f"  Calories: {nutrition.calories:.1f}")
        print(f"  Protein: {nutrition.protein:.1f}g")
        print(f"  Carbs: {nutrition.carbs:.1f}g")
        print(f"  Fat: {nutrition.fat:.1f}g")
    
    print("\\n=== Recipe Scaling ===")
    scaled_soup = chicken_soup.scale_recipe(2.0)  # Double the recipe
    print(f"Scaled recipe: {scaled_soup.get_name()}")
    print(f"Original servings: {chicken_soup.servings}")
    print(f"Scaled servings: {scaled_soup.servings}")
    
    print("\\n=== Shopping List Generation ===")
    shopping_list = chicken_soup.get_shopping_list('en')
    print("Shopping list:")
    for item in shopping_list:
        print(f"- {item['quantity']} {item['unit']} {item['name']}")
        if item['note']:
            print(f"  Note: {item['note']}")
    
    print("\\n=== JSON Serialization ===")
    soup_dict = chicken_soup.to_dict()
    soup_json = json.dumps(soup_dict, indent=2, ensure_ascii=False)
    print("Chicken soup as JSON (first 800 characters):")
    print(soup_json[:800] + "..." if len(soup_json) > 800 else soup_json)
    
    print("\\n=== Creating from Dictionary ===")
    restored_soup = Recipe.from_dict(soup_dict)
    print(f"Restored recipe: {restored_soup}")
    print(f"Same servings: {restored_soup.servings}")
    print(f"Same total time: {restored_soup.get_total_time_minutes()} minutes")
    
    print("\\n=== Season Suitability ===")
    print(f"Chicken soup suitable for winter: {chicken_soup.is_suitable_for_season(Season.WINTER)}")
    print(f"Chicken soup suitable for summer: {chicken_soup.is_suitable_for_season(Season.SUMMER)}")
    print(f"Simple salad suitable for spring: {simple_salad.is_suitable_for_season(Season.SPRING)}")


def create_recipe_library():
    """Create a sample recipe library with various types of recipes"""
    
    ingredient_library = create_sample_ingredient_library()
    
    recipes = {
        'simple_salad': create_simple_recipe(),
        'chicken_soup': create_detailed_recipe(),
        'vegetable_rosti': create_vegetarian_recipe()
    }
    
    # Load ingredients for all recipes
    for recipe in recipes.values():
        recipe.load_ingredients(ingredient_library)
    
    return recipes, ingredient_library


if __name__ == "__main__":
    print("=== Recipe Class Examples ===")
    demonstrate_recipe_usage()
    
    print("\\n\\n=== Sample Recipe Library ===")
    recipe_library, ingredient_library = create_recipe_library()
    print(f"Created recipe library with {len(recipe_library)} recipes:")
    print(f"Created ingredient library with {len(ingredient_library)} ingredients:")
    
    for recipe_id, recipe in recipe_library.items():
        print(f"  {recipe_id}: {recipe}")
        print(f"    - {len(recipe.recipe_ingredients)} ingredients")
        print(f"    - {len(recipe.preparation_steps)} steps")
        print(f"    - {recipe.get_total_time_minutes()} minutes total")
        if recipe.rating > 0:
            print(f"    - Rating: {recipe.rating}/5")