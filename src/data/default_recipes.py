"""
Default recipes module - loads default recipes for the app
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from src.models.recipe import Recipe
from src.models.ingredient import Ingredient

logger = logging.getLogger(__name__)


def get_default_recipes_file() -> Path:
    """Get the path to the default recipes JSON file"""
    return Path(__file__).parent / "default_recipes.json"


def get_migrated_recipes_file() -> Path:
    """Get the path to the migrated recipes JSON file"""
    return Path(__file__).parent / "migrated_recipes.json"


def get_ingredient_library_file() -> Path:
    """Get the path to the ingredient library JSON file"""
    return Path(__file__).parent / "ingredient_library.json"


def load_ingredient_library() -> Dict[str, Ingredient]:
    """Load the ingredient library"""
    ingredient_file = get_ingredient_library_file()

    if not ingredient_file.exists():
        logger.info("No ingredient library file found")
        return {}

    try:
        with open(ingredient_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ingredients_data = data.get('ingredients', {})
        ingredient_library = {}

        for ingredient_id, ingredient_dict in ingredients_data.items():
            try:
                ingredient = Ingredient.from_dict(ingredient_dict)
                ingredient_library[ingredient_id] = ingredient
            except Exception as e:
                logger.error(f"Failed to load ingredient {ingredient_id}: {e}")
                continue

        logger.info(f"Loaded {len(ingredient_library)} ingredients into library")
        return ingredient_library

    except Exception as e:
        logger.error(f"Error loading ingredient library: {e}")
        return {}


def load_default_recipes() -> List[Recipe]:
    """Load default recipes from the migrated Recipe objects file"""
    # First try to load migrated recipes
    migrated_file = get_migrated_recipes_file()

    if migrated_file.exists():
        return load_migrated_recipes()

    # Fall back to old dictionary format if migrated file doesn't exist
    logger.warning("Migrated recipes file not found, falling back to dictionary format")
    return load_legacy_recipes()


def load_migrated_recipes() -> List[Recipe]:
    """Load recipes from the migrated Recipe class format"""
    migrated_file = get_migrated_recipes_file()

    if not migrated_file.exists():
        logger.info("No migrated recipes file found")
        return []

    try:
        with open(migrated_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        recipes_data = data.get('recipes', [])
        export_info = data.get('export_info', {})

        # Load ingredient library
        ingredient_library = load_ingredient_library()

        # Convert dictionaries back to Recipe objects
        recipes = []
        for recipe_dict in recipes_data:
            try:
                recipe = Recipe.from_dict(recipe_dict)
                # Link ingredients to library
                recipe.load_ingredients(ingredient_library)
                recipes.append(recipe)
            except Exception as e:
                logger.error(f"Failed to load recipe {recipe_dict.get('names', {}).get('no', 'unknown')}: {e}")
                continue

        # Log information about loaded recipes
        if export_info:
            exported_at = export_info.get('exported_at', 'Unknown')
            migration_method = export_info.get('migration_method', 'Unknown')
            total_recipes = export_info.get('total_recipes', len(recipes))

            logger.info(f"Loaded {len(recipes)} migrated Recipe objects (originally {total_recipes}) using {migration_method}")
        else:
            logger.info(f"Loaded {len(recipes)} migrated Recipe objects")

        return recipes

    except Exception as e:
        logger.error(f"Error loading migrated recipes: {e}")
        return []


def load_legacy_recipes() -> List[Dict]:
    """Load recipes from the legacy dictionary format (for backward compatibility)"""
    recipes_file = get_default_recipes_file()

    if not recipes_file.exists():
        logger.info("No default recipes file found")
        return []

    try:
        with open(recipes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        recipes = data.get('recipes', [])
        export_info = data.get('export_info', {})

        # Log information about loaded recipes
        if export_info:
            exported_at = export_info.get('exported_at', 'Unknown')
            exported_from = export_info.get('exported_from', 'Unknown')
            total_recipes = export_info.get('total_recipes', len(recipes))

            logger.info(f"Loaded {total_recipes} default recipes (legacy format) exported from {exported_from} at {exported_at}")
        else:
            logger.info(f"Loaded {len(recipes)} default recipes (legacy format)")

        # Add metadata to each recipe to indicate it's a default recipe
        for recipe in recipes:
            recipe['is_default_recipe'] = True
            recipe['recipe_type'] = 'default_export'

        return recipes

    except Exception as e:
        logger.error(f"Error loading default recipes: {e}")
        return []


def get_default_recipes_info() -> Optional[Dict]:
    """Get information about the default recipes export"""
    recipes_file = get_default_recipes_file()
    
    if not recipes_file.exists():
        return None
    
    try:
        with open(recipes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        export_info = data.get('export_info', {})
        
        # Add file information
        file_stats = recipes_file.stat()
        export_info['file_size_mb'] = round(file_stats.st_size / 1024 / 1024, 2)
        export_info['file_modified'] = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        
        return export_info
        
    except Exception as e:
        logger.error(f"Error getting default recipes info: {e}")
        return None


def has_default_recipes() -> bool:
    """Check if default recipes are available"""
    recipes_file = get_default_recipes_file()
    return recipes_file.exists() and recipes_file.stat().st_size > 0


def get_default_recipes_count() -> int:
    """Get the number of default recipes available"""
    if not has_default_recipes():
        return 0
    
    try:
        with open(get_default_recipes_file(), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return len(data.get('recipes', []))
        
    except Exception as e:
        logger.error(f"Error counting default recipes: {e}")
        return 0


def search_default_recipes(query: str, recipes: Optional[List[Dict]] = None) -> List[Dict]:
    """Search through default recipes by name, ingredients, or tags"""
    if recipes is None:
        recipes = load_default_recipes()
    
    if not query:
        return recipes
    
    query_lower = query.lower()
    matching_recipes = []
    
    for recipe in recipes:
        # Search in recipe name
        name = recipe.get('name', '').lower()
        if query_lower in name:
            matching_recipes.append(recipe)
            continue
        
        # Search in ingredients
        ingredients = recipe.get('ingredients', [])
        if isinstance(ingredients, list):
            ingredient_text = ' '.join(str(ing).lower() for ing in ingredients)
        elif isinstance(ingredients, dict):
            ingredient_text = ' '.join(f"{ing} {qty}".lower() for ing, qty in ingredients.items())
        else:
            ingredient_text = str(ingredients).lower()
        
        if query_lower in ingredient_text:
            matching_recipes.append(recipe)
            continue
        
        # Search in collections/tags
        collections = recipe.get('collections', [])
        if isinstance(collections, list):
            collections_text = ' '.join(str(col).lower() for col in collections)
            if query_lower in collections_text:
                matching_recipes.append(recipe)
                continue
    
    return matching_recipes


def get_recipes_by_rating(min_rating: int = 1, recipes: Optional[List[Dict]] = None) -> List[Dict]:
    """Get recipes filtered by minimum rating"""
    if recipes is None:
        recipes = load_default_recipes()
    
    return [recipe for recipe in recipes if recipe.get('rating', 0) >= min_rating]


def get_recipes_with_photos(recipes: Optional[List[Dict]] = None) -> List[Dict]:
    """Get recipes that have photos"""
    if recipes is None:
        recipes = load_default_recipes()
    
    return [recipe for recipe in recipes if recipe.get('photo', {}).get('hasPhoto', False)]


def get_recipes_by_prep_time(max_prep_minutes: int, recipes: Optional[List[Dict]] = None) -> List[Dict]:
    """Get recipes filtered by maximum prep time"""
    if recipes is None:
        recipes = load_default_recipes()
    
    return [recipe for recipe in recipes 
            if recipe.get('prepTime', 0) <= max_prep_minutes and recipe.get('prepTime', 0) > 0]


def get_recipes_by_cook_time(max_cook_minutes: int, recipes: Optional[List[Dict]] = None) -> List[Dict]:
    """Get recipes filtered by maximum cook time"""
    if recipes is None:
        recipes = load_default_recipes()
    
    return [recipe for recipe in recipes 
            if recipe.get('cookTime', 0) <= max_cook_minutes and recipe.get('cookTime', 0) > 0]


if __name__ == "__main__":
    # Test the default recipes loading
    print("Testing default recipes loading...")
    
    recipes = load_default_recipes()
    print(f"Loaded {len(recipes)} default recipes")
    
    info = get_default_recipes_info()
    if info:
        print(f"Export info: {info}")
    
    if recipes:
        print(f"\nFirst recipe: {recipes[0].get('name', 'Unnamed')}")
        
        # Test search
        search_results = search_default_recipes("chicken")
        print(f"Found {len(search_results)} recipes containing 'chicken'")
        
        # Test rating filter
        high_rated = get_recipes_by_rating(4)
        print(f"Found {len(high_rated)} recipes with 4+ star rating")
        
        # Test photos filter
        with_photos = get_recipes_with_photos()
        print(f"Found {len(with_photos)} recipes with photos")