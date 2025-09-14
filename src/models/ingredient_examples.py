"""
Example usage of the Ingredient class for the Chef's Assistant ingredient library.

This file demonstrates how to create and use ingredients with various properties.
"""

from ingredient import Ingredient, create_basic_ingredient, create_vegetable_ingredient, StorageType, Season, NutritionInfo, PriceInfo
import json


def create_sample_ingredients():
    """Create sample ingredients demonstrating different features"""
    
    # Basic ingredient with minimal information
    salt = create_basic_ingredient(
        ingredient_id="salt",
        name_no="Salt",
        name_en="Salt",
        category="seasoning"
    )
    
    # Vegetable with typical properties
    carrot = create_vegetable_ingredient(
        ingredient_id="carrot",
        name_no="Gulrot",
        name_en="Carrot",
        typical_weight=100.0
    )
    
    # Add nutritional information to carrot
    carrot.set_nutrition(
        calories=41,
        protein=0.9,
        carbs=9.6,
        fat=0.2,
        fiber=2.8,
        sugar=4.7
    )
    carrot.nutrition.vitamins = {'A': 835, 'C': 5.9, 'K': 13.2}
    carrot.nutrition.minerals = {'potassium': 320, 'calcium': 33}
    
    # Add price information
    carrot.update_price_info(
        average_price_per_kg=15.00,
        seasonal_price_variation=True
    )
    
    # Set additional properties
    carrot.flavor_profile = ['sweet', 'earthy']
    carrot.texture = 'crisp'
    carrot.shelf_life_days = 14
    carrot.peak_season = [Season.SUMMER, Season.FALL]
    carrot.common_pairings = ['onion', 'celery', 'ginger', 'cumin']
    
    # Complex ingredient with full information
    salmon = Ingredient(
        ingredient_id="salmon",
        name_no="Laks",
        name_en="Salmon",
        plural_no="Laksefileter",
        plural_en="Salmon fillets",
        category="fish",
        typical_weight_grams=150.0,  # Per fillet
        edible_portion=0.95,  # 95% edible
        common_units=['stk', 'g', 'kg', 'fillet'],
        preparation_methods=[
            {'no': 'hel filet', 'en': 'whole fillet'},
            {'no': 'i biter', 'en': 'chunks'},
            {'no': 'tynne skiver', 'en': 'thin slices'},
            {'no': 'terninger', 'en': 'cubed'}
        ],
        nutrition={
            'calories': 208,
            'protein': 25.4,
            'fat': 12.4,
            'carbs': 0.0,
            'vitamins': {'D': 526, 'B12': 4.9, 'B6': 0.8},
            'minerals': {'selenium': 24.9, 'phosphorus': 252}
        },
        price_info={
            'average_price_per_kg': 299.00,
            'seasonal_price_variation': False,
            'typical_package_size': 0.4,  # 400g package
            'typical_package_unit': 'kg'
        },
        flavor_profile=['rich', 'buttery', 'oceanic'],
        texture='flaky',
        cooking_methods=['grilled', 'baked', 'pan-fried', 'poached', 'smoked'],
        common_pairings=['lemon', 'dill', 'capers', 'asparagus', 'avocado'],
        shelf_life_days=3,
        storage_type=StorageType.REFRIGERATED,
        available_year_round=True
    )
    
    # Bread ingredient with specific properties
    bread = Ingredient(
        ingredient_id="white_bread",
        name_no="Hvitbrød",
        name_en="White Bread",
        category="grain",
        typical_weight_grams=30.0,  # Per slice
        common_units=['skive', 'slice', 'g'],
        aliases=['toast', 'brødskive'],
        preparation_methods=[
            {'no': 'hel skive', 'en': 'whole slice'},
            {'no': 'ristede', 'en': 'toasted'},
            {'no': 'smuler', 'en': 'breadcrumbs'},
            {'no': 'terninger', 'en': 'cubed'}
        ],
        nutrition={
            'calories': 265,
            'protein': 9.0,
            'carbs': 49.0,
            'fat': 3.2,
            'fiber': 2.7,
            'sugar': 5.0
        },
        flavor_profile=['neutral', 'slightly sweet'],
        texture='soft',
        cooking_methods=['toasted', 'baked', 'fried'],
        shelf_life_days=5,
        storage_type=StorageType.ROOM_TEMPERATURE
    )
    
    return [salt, carrot, salmon, bread]


def demonstrate_ingredient_usage():
    """Demonstrate various ways to use the Ingredient class"""
    
    print("=== Creating Sample Ingredients ===")
    ingredients = create_sample_ingredients()
    
    print("\n=== Basic Information ===")
    for ingredient in ingredients:
        print(f"ID: {ingredient.id}")
        print(f"Name (Norwegian): {ingredient.get_name('no')}")
        print(f"Name (English): {ingredient.get_name('en')}")
        print(f"Category: {ingredient.category}")
        print(f"String representation: {ingredient}")
        print("-" * 40)
    
    # Focus on carrot for detailed examples
    carrot = ingredients[1]  # The carrot we created
    
    print("\n=== Carrot Details ===")
    print(f"Typical weight: {carrot.typical_weight_grams}g")
    print(f"Preparation methods (Norwegian): {carrot.get_preparation_methods('no')}")
    print(f"Preparation methods (English): {carrot.get_preparation_methods('en')}")
    print(f"Flavor profile: {carrot.flavor_profile}")
    print(f"Common pairings: {carrot.common_pairings}")
    print(f"In season during summer: {carrot.is_in_season(Season.SUMMER)}")
    print(f"In season during winter: {carrot.is_in_season(Season.WINTER)}")
    
    print(f"\nNutrition per 100g:")
    print(f"  Calories: {carrot.nutrition.calories}")
    print(f"  Protein: {carrot.nutrition.protein}g")
    print(f"  Carbs: {carrot.nutrition.carbs}g")
    print(f"  Fiber: {carrot.nutrition.fiber}g")
    print(f"  Vitamin A: {carrot.nutrition.vitamins.get('A', 0)} IU")
    
    print(f"\nPrice information:")
    print(f"  Average price per kg: {carrot.price_info.average_price_per_kg} NOK")
    print(f"  Price updated: {carrot.price_info.price_updated}")
    
    print(f"\nCommon conversions: {carrot.get_common_conversions()}")
    
    print("\n=== JSON Serialization ===")
    carrot_dict = carrot.to_dict()
    carrot_json = json.dumps(carrot_dict, indent=2)
    print("Carrot as JSON:")
    print(carrot_json[:500] + "..." if len(carrot_json) > 500 else carrot_json)
    
    # Demonstrate creating from dictionary
    print("\n=== Creating from Dictionary ===")
    restored_carrot = Ingredient.from_dict(carrot_dict)
    print(f"Restored carrot: {restored_carrot}")
    print(f"Same nutrition calories: {restored_carrot.nutrition.calories}")
    
    print("\n=== Adding Preparation Methods ===")
    carrot.add_preparation_method("raspet", "shredded")
    print(f"Updated preparation methods: {carrot.get_preparation_methods('no')}")


def create_ingredient_library():
    """Create a sample ingredient library with common ingredients"""
    
    library = {}
    
    # Vegetables
    vegetables = [
        ("onion", "Løk", "Onion", 150),
        ("potato", "Potet", "Potato", 200),
        ("tomato", "Tomat", "Tomato", 120),
        ("bell_pepper", "Paprika", "Bell Pepper", 160),
        ("broccoli", "Brokkoli", "Broccoli", 300),
        ("cucumber", "Agurk", "Cucumber", 400)
    ]
    
    for ing_id, name_no, name_en, weight in vegetables:
        ingredient = create_vegetable_ingredient(ing_id, name_no, name_en, weight)
        library[ing_id] = ingredient
    
    # Proteins
    proteins = [
        ("chicken_breast", "Kyllingbryst", "Chicken Breast", "meat", 200),
        ("ground_beef", "Kjøttdeig", "Ground Beef", "meat", 500),
        ("eggs", "Egg", "Eggs", "protein", 60),
    ]
    
    for ing_id, name_no, name_en, category, weight in proteins:
        ingredient = Ingredient(
            ingredient_id=ing_id,
            name_no=name_no,
            name_en=name_en,
            category=category,
            typical_weight_grams=weight,
            storage_type=StorageType.REFRIGERATED
        )
        library[ing_id] = ingredient
    
    # Pantry staples
    pantry_items = [
        ("olive_oil", "Olivenolje", "Olive Oil", "oil", 15),  # Per tablespoon
        ("flour", "Mel", "Flour", "grain", 125),  # Per cup
        ("sugar", "Sukker", "Sugar", "sweetener", 200),  # Per cup
        ("rice", "Ris", "Rice", "grain", 185)  # Per cup uncooked
    ]
    
    for ing_id, name_no, name_en, category, weight in pantry_items:
        ingredient = Ingredient(
            ingredient_id=ing_id,
            name_no=name_no,
            name_en=name_en,
            category=category,
            typical_weight_grams=weight,
            storage_type=StorageType.PANTRY,
            shelf_life_days=365,
            available_year_round=True
        )
        library[ing_id] = ingredient
    
    return library


if __name__ == "__main__":
    print("=== Ingredient Class Examples ===")
    demonstrate_ingredient_usage()
    
    print("\n\n=== Sample Ingredient Library ===")
    library = create_ingredient_library()
    print(f"Created library with {len(library)} ingredients:")
    for ingredient_id, ingredient in library.items():
        print(f"  {ingredient_id}: {ingredient}")