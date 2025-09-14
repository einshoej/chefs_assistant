"""
Script to run the full migration from dictionary recipes to Recipe/Ingredient classes
"""

import sys
import logging
from pathlib import Path

# Add project root to path so we can import our modules
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))

from src.data.default_recipes import load_default_recipes
from src.utils.ingredient_extractor import IngredientExtractor
from src.utils.recipe_migrator import RecipeMigrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the full migration process"""
    logger.info("Starting migration process...")

    # Step 1: Load existing recipes
    logger.info("Loading default recipes...")
    recipes = load_default_recipes()
    logger.info(f"Loaded {len(recipes)} recipes")

    if not recipes:
        logger.error("No recipes loaded. Cannot proceed with migration.")
        return

    # Step 2: Build ingredient library
    logger.info("Building ingredient library...")
    ingredient_library = IngredientExtractor.build_ingredient_library(recipes)
    logger.info(f"Built ingredient library with {len(ingredient_library)} ingredients")

    # Step 3: Save ingredient library
    ingredient_library_path = project_root / "src" / "data" / "ingredient_library.json"
    logger.info(f"Saving ingredient library to {ingredient_library_path}")
    IngredientExtractor.save_ingredient_library(ingredient_library, str(ingredient_library_path))

    # Step 4: Migrate recipes
    logger.info("Migrating recipes to Recipe class objects...")
    migrated_recipes = RecipeMigrator.migrate_all_recipes(recipes, ingredient_library)
    logger.info(f"Successfully migrated {len(migrated_recipes)} recipes")

    # Step 5: Save migrated recipes
    migrated_recipes_path = project_root / "src" / "data" / "migrated_recipes.json"
    logger.info(f"Saving migrated recipes to {migrated_recipes_path}")
    RecipeMigrator.save_migrated_recipes(migrated_recipes, str(migrated_recipes_path))

    # Step 6: Print summary statistics
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Original recipes: {len(recipes)}")
    print(f"Migrated recipes: {len(migrated_recipes)}")
    print(f"Unique ingredients: {len(ingredient_library)}")
    print(f"Ingredient library: {ingredient_library_path}")
    print(f"Migrated recipes: {migrated_recipes_path}")

    # Show ingredient categories
    categories = {}
    for ingredient in ingredient_library.values():
        cat = ingredient.category
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nIngredient categories:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} ingredients")

    # Show recipe categories
    meal_types = {}
    difficulties = {}
    for recipe in migrated_recipes:
        if recipe.meal_type:
            meal_types[recipe.meal_type.value] = meal_types.get(recipe.meal_type.value, 0) + 1
        diff = recipe.difficulty.value
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print(f"\nRecipe meal types:")
    for meal_type, count in sorted(meal_types.items()):
        print(f"  {meal_type}: {count} recipes")

    print(f"\nRecipe difficulties:")
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count} recipes")

    print("\n" + "="*60)
    print("Migration completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()