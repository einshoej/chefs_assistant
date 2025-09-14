"""
Recipe migrator utility - converts dictionary-based recipes to Recipe class objects
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from src.models.recipe import Recipe, RecipeIngredient, RecipeStep, RecipePhoto, DifficultyLevel, MealType
from src.models.ingredient import Ingredient, Season
from src.utils.ingredient_extractor import IngredientExtractor, ParsedIngredient

logger = logging.getLogger(__name__)


class RecipeMigrator:
    """Converts dictionary-based recipes to Recipe class objects"""

    @classmethod
    def migrate_recipe(cls, recipe_dict: Dict, ingredient_library: Dict[str, Ingredient]) -> Recipe:
        """
        Convert a dictionary recipe to a Recipe object

        Args:
            recipe_dict: Dictionary containing recipe data
            ingredient_library: Library of Ingredient objects for linking

        Returns:
            Recipe object
        """
        # Extract basic information
        recipe_id = recipe_dict.get('id', '')
        name = recipe_dict.get('name', '')

        if not name:
            raise ValueError(f"Recipe must have a name: {recipe_dict}")

        # Create Recipe object with basic info
        recipe = Recipe(
            recipe_id=recipe_id,
            name_no=name,  # Assume Norwegian name as primary
            description_no=recipe_dict.get('description', ''),
            prep_time_minutes=cls._parse_time(recipe_dict.get('prep_time', 0)),
            cook_time_minutes=cls._parse_time(recipe_dict.get('cook_time', 0)),
            servings=cls._parse_servings(recipe_dict.get('servings', '')),
            rating=recipe_dict.get('rating', 0.0),
            source=recipe_dict.get('source', ''),
            source_url=recipe_dict.get('sourceUrl', ''),
            created_at=cls._parse_datetime(recipe_dict.get('createdAt')),
            updated_at=cls._parse_datetime(recipe_dict.get('updatedAt'))
        )

        # Process collections into categories and seasons
        collections = recipe_dict.get('collections', [])
        categories, seasons = cls._process_collections(collections)
        recipe.categories = categories
        recipe.seasons = seasons

        # Determine meal type from categories
        recipe.meal_type = cls._determine_meal_type(categories)

        # Determine difficulty (placeholder logic)
        recipe.difficulty = cls._determine_difficulty(recipe_dict)

        # Process ingredients
        recipe_ingredients = cls._process_ingredients(recipe_dict, ingredient_library)
        recipe.recipe_ingredients = recipe_ingredients

        # Process instructions/steps (try both field names)
        instructions = recipe_dict.get('preparation_steps', []) or recipe_dict.get('instructions', [])
        steps = cls._process_instructions(instructions)
        recipe.preparation_steps = steps

        # Process images
        photo_data = recipe_dict.get('photo', {})
        if photo_data.get('url'):
            photo = RecipePhoto(
                url=photo_data['url'],
                alt_text=f"Photo of {name}",
                is_primary=True
            )
            recipe.photos = [photo]
        elif recipe_dict.get('image'):
            photo = RecipePhoto(
                url=recipe_dict['image'],
                alt_text=f"Photo of {name}",
                is_primary=True
            )
            recipe.photos = [photo]

        # Add metadata
        recipe.tags.extend(['imported', 'default_recipe'])
        if recipe_dict.get('is_default_recipe'):
            recipe.tags.append('default_export')

        return recipe

    @classmethod
    def _parse_time(cls, time_value) -> int:
        """Parse time value to minutes"""
        if isinstance(time_value, (int, float)):
            return int(time_value)
        elif isinstance(time_value, str):
            # Try to extract number from string
            import re
            match = re.search(r'\d+', time_value)
            if match:
                return int(match.group())
        return 0

    @classmethod
    def _parse_servings(cls, servings_value) -> int:
        """Parse servings value"""
        if isinstance(servings_value, int):
            return servings_value
        elif isinstance(servings_value, str) and servings_value.strip():
            # Try to extract number
            import re
            match = re.search(r'\d+', servings_value)
            if match:
                return int(match.group())
        return 4  # Default servings

    @classmethod
    def _parse_datetime(cls, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not datetime_str:
            return None

        try:
            # Try ISO format
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try other common formats
                return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                return None

    @classmethod
    def _process_collections(cls, collections: List) -> tuple[List[str], List[Season]]:
        """
        Process collections into categories and seasons

        Args:
            collections: List of collection dictionaries or strings

        Returns:
            Tuple of (categories, seasons)
        """
        categories = []
        seasons = []

        season_mapping = {
            'Vinter': Season.WINTER,
            'Vår': Season.SPRING,
            'Sommer': Season.SUMMER,
            'Høst': Season.FALL
        }

        for collection in collections:
            if isinstance(collection, dict):
                name = collection.get('name', '')
            else:
                name = str(collection)

            if name in season_mapping:
                seasons.append(season_mapping[name])
            else:
                categories.append(name)

        return categories, seasons

    @classmethod
    def _determine_meal_type(cls, categories: List[str]) -> Optional[MealType]:
        """Determine meal type from categories"""
        category_lower = [cat.lower() for cat in categories]

        if any(term in category_lower for term in ['frokost', 'breakfast']):
            return MealType.BREAKFAST
        elif any(term in category_lower for term in ['lunsj', 'lunch']):
            return MealType.LUNCH
        elif any(term in category_lower for term in ['middag', 'dinner']):
            return MealType.DINNER
        elif any(term in category_lower for term in ['dessert', 'kake', 'cake']):
            return MealType.DESSERT
        elif any(term in category_lower for term in ['snack', 'mellommåltid']):
            return MealType.SNACK
        elif any(term in category_lower for term in ['forrett', 'appetizer']):
            return MealType.APPETIZER
        elif any(term in category_lower for term in ['tilbehør', 'side']):
            return MealType.SIDE_DISH

        return None

    @classmethod
    def _determine_difficulty(cls, recipe_dict: Dict) -> DifficultyLevel:
        """Determine difficulty based on recipe complexity"""
        # Simple heuristic based on number of ingredients and steps
        num_ingredients = len(recipe_dict.get('ingredients', []))
        num_steps = len(recipe_dict.get('instructions', []))
        total_time = cls._parse_time(recipe_dict.get('prep_time', 0)) + cls._parse_time(recipe_dict.get('cook_time', 0))

        # Score based on complexity
        complexity_score = 0
        if num_ingredients > 10:
            complexity_score += 1
        if num_steps > 8:
            complexity_score += 1
        if total_time > 60:
            complexity_score += 1

        if complexity_score >= 2:
            return DifficultyLevel.HARD
        elif complexity_score == 1:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.EASY

    @classmethod
    def _process_ingredients(cls, recipe_dict: Dict, ingredient_library: Dict[str, Ingredient]) -> List[RecipeIngredient]:
        """Process ingredients into RecipeIngredient objects"""
        recipe_ingredients = []
        ingredients_list = recipe_dict.get('ingredients', [])

        for i, ingredient_text in enumerate(ingredients_list):
            if not isinstance(ingredient_text, str) or not ingredient_text.strip():
                continue

            # Parse the ingredient text
            parsed = IngredientExtractor.parse_ingredient_text(ingredient_text)

            # Find matching ingredient in library
            ingredient_id = cls._find_ingredient_id(parsed, ingredient_library)

            # Create RecipeIngredient
            recipe_ingredient = RecipeIngredient(
                ingredient_id=ingredient_id,
                quantity=parsed.quantity,
                unit=parsed.unit,
                preparation=parsed.preparation,
                note=""
            )

            # Try to load the ingredient reference
            if ingredient_id in ingredient_library:
                recipe_ingredient.ingredient = ingredient_library[ingredient_id]

            recipe_ingredients.append(recipe_ingredient)

        return recipe_ingredients

    @classmethod
    def _find_ingredient_id(cls, parsed: ParsedIngredient, ingredient_library: Dict[str, Ingredient]) -> str:
        """Find the best matching ingredient ID for a parsed ingredient"""
        if not parsed.name:
            return 'unknown_ingredient'

        # Normalize the name
        normalized_name = cls._normalize_name_for_matching(parsed.name)

        # Direct match by name
        for ingredient_id, ingredient in ingredient_library.items():
            if normalized_name == cls._normalize_name_for_matching(ingredient.names.get('no', '')):
                return ingredient_id

        # Partial match
        for ingredient_id, ingredient in ingredient_library.items():
            ingredient_name = ingredient.names.get('no', '').lower()
            if normalized_name in ingredient_name or ingredient_name in normalized_name:
                return ingredient_id

        # If no match found, generate ID from name
        return IngredientExtractor._generate_ingredient_id(parsed.name)

    @classmethod
    def _normalize_name_for_matching(cls, name: str) -> str:
        """Normalize name for ingredient matching"""
        return IngredientExtractor._normalize_ingredient_name(name).lower()

    @classmethod
    def _process_instructions(cls, instructions: List[str]) -> List[RecipeStep]:
        """Process instructions into RecipeStep objects"""
        steps = []

        for i, instruction in enumerate(instructions):
            if not isinstance(instruction, str) or not instruction.strip():
                continue

            step = RecipeStep(
                step_number=i + 1,
                instruction_no=instruction.strip(),
                instruction_en=""  # Could add translation later
            )

            # Try to extract time information from instruction
            time_minutes = cls._extract_time_from_instruction(instruction)
            if time_minutes:
                step.time_minutes = time_minutes

            # Try to extract temperature
            temp_celsius = cls._extract_temperature_from_instruction(instruction)
            if temp_celsius:
                step.temperature_celsius = temp_celsius

            steps.append(step)

        return steps

    @classmethod
    def _extract_time_from_instruction(cls, instruction: str) -> Optional[int]:
        """Extract time information from instruction text"""
        import re

        # Look for time patterns
        time_patterns = [
            r'(\d+)\s*min',
            r'(\d+)\s*minutt',
            r'(\d+)\s*timer',
            r'(\d+)\s*time'
        ]

        for pattern in time_patterns:
            match = re.search(pattern, instruction.lower())
            if match:
                minutes = int(match.group(1))
                # Convert hours to minutes
                if 'time' in pattern:
                    minutes *= 60
                return minutes

        return None

    @classmethod
    def _extract_temperature_from_instruction(cls, instruction: str) -> Optional[int]:
        """Extract temperature from instruction text"""
        import re

        # Look for temperature patterns
        temp_patterns = [
            r'(\d+)\s*°C',
            r'(\d+)\s*grader',
            r'(\d+)\s*celsius'
        ]

        for pattern in temp_patterns:
            match = re.search(pattern, instruction.lower())
            if match:
                return int(match.group(1))

        return None

    @classmethod
    def migrate_all_recipes(
        cls,
        recipes: List[Dict],
        ingredient_library: Dict[str, Ingredient]
    ) -> List[Recipe]:
        """
        Migrate all recipes from dictionaries to Recipe objects

        Args:
            recipes: List of recipe dictionaries
            ingredient_library: Ingredient library for linking

        Returns:
            List of Recipe objects
        """
        migrated_recipes = []
        failed_migrations = []

        for recipe_dict in recipes:
            try:
                recipe = cls.migrate_recipe(recipe_dict, ingredient_library)
                migrated_recipes.append(recipe)
            except Exception as e:
                failed_migrations.append({
                    'recipe_id': recipe_dict.get('id', 'unknown'),
                    'recipe_name': recipe_dict.get('name', 'unknown'),
                    'error': str(e)
                })
                logger.error(f"Failed to migrate recipe {recipe_dict.get('name', 'unknown')}: {e}")

        logger.info(f"Successfully migrated {len(migrated_recipes)} recipes")
        if failed_migrations:
            logger.warning(f"Failed to migrate {len(failed_migrations)} recipes")

        return migrated_recipes

    @classmethod
    def save_migrated_recipes(cls, recipes: List[Recipe], filepath: str) -> None:
        """Save migrated recipes to JSON file"""
        # Convert recipes to dictionary format
        recipes_dict = []
        for recipe in recipes:
            recipes_dict.append(recipe.to_dict())

        # Create export metadata
        export_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'total_recipes': len(recipes_dict),
                'migration_method': 'automated_dictionary_to_recipe_class',
                'uses_recipe_class': True,
                'uses_ingredient_library': True
            },
            'recipes': recipes_dict
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(recipes_dict)} migrated recipes to {filepath}")


# Convenience functions for external use

def migrate_recipes_from_file(
    recipes_file: str,
    ingredient_library: Dict[str, Ingredient]
) -> List[Recipe]:
    """Load and migrate recipes from JSON file"""
    with open(recipes_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes = data.get('recipes', [])
    return RecipeMigrator.migrate_all_recipes(recipes, ingredient_library)


def migrate_recipe_dict(
    recipe_dict: Dict,
    ingredient_library: Dict[str, Ingredient]
) -> Recipe:
    """Migrate a single recipe dictionary"""
    return RecipeMigrator.migrate_recipe(recipe_dict, ingredient_library)