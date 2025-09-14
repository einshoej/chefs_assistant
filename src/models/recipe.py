"""
Recipe class for the Chef's Assistant recipe management system.

This module defines recipes as structured entities that reference ingredients from the ingredient
library/catalog system, with multilingual support and rich metadata.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

# Import from our ingredient system
from src.models.ingredient import Ingredient, NutritionInfo, Season


class DifficultyLevel(Enum):
    """Recipe difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MealType(Enum):
    """Types of meals"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"
    APPETIZER = "appetizer"
    SIDE_DISH = "side_dish"


@dataclass
class RecipePhoto:
    """Photo information for a recipe"""
    url: str
    alt_text: str = ""
    caption_no: str = ""
    caption_en: str = ""
    is_primary: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'url': self.url,
            'alt_text': self.alt_text,
            'caption_no': self.caption_no,
            'caption_en': self.caption_en,
            'is_primary': self.is_primary
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecipePhoto':
        """Create from dictionary"""
        return cls(
            url=data.get('url', ''),
            alt_text=data.get('alt_text', ''),
            caption_no=data.get('caption_no', ''),
            caption_en=data.get('caption_en', ''),
            is_primary=data.get('is_primary', False)
        )


@dataclass
class RecipeStep:
    """A single preparation step in a recipe"""
    step_number: int
    instruction_no: str
    instruction_en: str = ""
    time_minutes: Optional[int] = None
    temperature_celsius: Optional[int] = None
    temperature_fahrenheit: Optional[int] = None
    
    def get_instruction(self, language: str = 'no') -> str:
        """Get instruction in specified language"""
        if language == 'en' and self.instruction_en:
            return self.instruction_en
        return self.instruction_no
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'step_number': self.step_number,
            'instruction_no': self.instruction_no,
            'instruction_en': self.instruction_en,
            'time_minutes': self.time_minutes,
            'temperature_celsius': self.temperature_celsius,
            'temperature_fahrenheit': self.temperature_fahrenheit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecipeStep':
        """Create from dictionary"""
        return cls(
            step_number=data.get('step_number', 1),
            instruction_no=data.get('instruction_no', ''),
            instruction_en=data.get('instruction_en', ''),
            time_minutes=data.get('time_minutes'),
            temperature_celsius=data.get('temperature_celsius'),
            temperature_fahrenheit=data.get('temperature_fahrenheit')
        )


@dataclass
class RecipeIngredient:
    """
    Bridge between Recipe and Ingredient catalog.
    Links a recipe to an ingredient with recipe-specific quantities and preparation.
    """
    ingredient_id: str
    quantity: str = ""
    unit: str = ""
    preparation: str = ""
    note: str = ""
    optional: bool = False
    group: str = ""  # For grouping ingredients (e.g., "For the sauce")
    
    # Optional reference to the full ingredient from catalog
    ingredient: Optional[Ingredient] = None
    
    def load_ingredient(self, ingredient_library: Dict[str, Ingredient]) -> None:
        """Load the full ingredient from the ingredient library"""
        if self.ingredient_id in ingredient_library:
            self.ingredient = ingredient_library[self.ingredient_id]
    
    def get_ingredient_name(self, language: str = 'no') -> str:
        """Get ingredient name in specified language"""
        if self.ingredient:
            return self.ingredient.get_name(language)
        return self.ingredient_id  # Fallback to ID if ingredient not loaded
    
    def get_display_text(self, language: str = 'no') -> str:
        """Get full display text for this ingredient"""
        parts = []
        
        if self.quantity:
            parts.append(self.quantity)
        if self.unit:
            parts.append(self.unit)
        
        name = self.get_ingredient_name(language)
        parts.append(name)
        
        if self.preparation:
            parts.append(f"({self.preparation})")
        
        if self.note:
            parts.append(f"- {self.note}")
        
        if self.optional:
            optional_text = "valgfritt" if language == 'no' else "optional"
            parts.append(f"({optional_text})")
        
        return " ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'ingredient_id': self.ingredient_id,
            'quantity': self.quantity,
            'unit': self.unit,
            'preparation': self.preparation,
            'note': self.note,
            'optional': self.optional,
            'group': self.group
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecipeIngredient':
        """Create from dictionary"""
        return cls(
            ingredient_id=data.get('ingredient_id', ''),
            quantity=data.get('quantity', ''),
            unit=data.get('unit', ''),
            preparation=data.get('preparation', ''),
            note=data.get('note', ''),
            optional=data.get('optional', False),
            group=data.get('group', '')
        )


class Recipe:
    """
    Represents a recipe that references ingredients from the ingredient catalog.
    
    Each recipe is a structured entity with multilingual support, timing information,
    and rich metadata. Only Norwegian name is required - everything else is optional.
    """
    
    def __init__(
        self,
        recipe_id: Optional[str] = None,
        name_no: str = "",
        **kwargs
    ):
        """
        Initialize a recipe with required Norwegian name.
        
        Args:
            recipe_id: Unique identifier (auto-generated if not provided)
            name_no: Norwegian name (required)
            **kwargs: Additional optional properties
        """
        # Required fields
        self.id = recipe_id or str(uuid.uuid4())
        self.names = {
            'no': name_no,
            'en': kwargs.get('name_en', ''),
            'description_no': kwargs.get('description_no', ''),
            'description_en': kwargs.get('description_en', '')
        }
        
        if not name_no:
            raise ValueError("Recipe must have a Norwegian name (name_no)")
        
        # Recipe ingredients (references to ingredient catalog)
        ingredients_data = kwargs.get('recipe_ingredients', [])
        self.recipe_ingredients = []
        for ing_data in ingredients_data:
            if isinstance(ing_data, dict):
                self.recipe_ingredients.append(RecipeIngredient.from_dict(ing_data))
            elif isinstance(ing_data, RecipeIngredient):
                self.recipe_ingredients.append(ing_data)
        
        # Preparation steps
        steps_data = kwargs.get('preparation_steps', [])
        self.preparation_steps = []
        for step_data in steps_data:
            if isinstance(step_data, dict):
                self.preparation_steps.append(RecipeStep.from_dict(step_data))
            elif isinstance(step_data, RecipeStep):
                self.preparation_steps.append(step_data)
            elif isinstance(step_data, str):
                # Convert simple string to RecipeStep
                step_num = len(self.preparation_steps) + 1
                self.preparation_steps.append(RecipeStep(
                    step_number=step_num,
                    instruction_no=step_data
                ))
        
        # Timing (in minutes)
        self.prep_time_minutes = kwargs.get('prep_time_minutes', 0)
        self.cook_time_minutes = kwargs.get('cook_time_minutes', 0)
        self.rest_time_minutes = kwargs.get('rest_time_minutes', 0)
        
        # Yield and scaling
        self.servings = kwargs.get('servings', 0)
        self.yield_amount = kwargs.get('yield_amount', 0.0)
        self.yield_unit = kwargs.get('yield_unit', '')

        # Recipe-as-ingredient production
        self.produces_ingredient = kwargs.get('produces_ingredient', False)
        self.produced_ingredient_id = kwargs.get('produced_ingredient_id', '')
        
        # Categories and metadata
        self.categories = kwargs.get('categories', [])
        self.tags = kwargs.get('tags', [])
        
        # Difficulty and classification
        difficulty = kwargs.get('difficulty', DifficultyLevel.MEDIUM)
        if isinstance(difficulty, str):
            try:
                self.difficulty = DifficultyLevel(difficulty)
            except ValueError:
                self.difficulty = DifficultyLevel.MEDIUM
        else:
            self.difficulty = difficulty
        
        self.cuisine = kwargs.get('cuisine', '')
        
        meal_type = kwargs.get('meal_type')
        if isinstance(meal_type, str):
            try:
                self.meal_type = MealType(meal_type)
            except ValueError:
                self.meal_type = None
        else:
            self.meal_type = meal_type
        
        # Seasonality
        seasons = kwargs.get('seasons', [])
        self.seasons = []
        for season in seasons:
            if isinstance(season, str):
                try:
                    self.seasons.append(Season(season))
                except ValueError:
                    continue
            elif isinstance(season, Season):
                self.seasons.append(season)
        
        # Ratings and source
        self.rating = kwargs.get('rating', 0.0)
        self.source = kwargs.get('source', '')
        self.source_url = kwargs.get('source_url', '')
        self.author = kwargs.get('author', '')
        
        # Media
        photos_data = kwargs.get('photos', [])
        self.photos = []
        for photo_data in photos_data:
            if isinstance(photo_data, dict):
                self.photos.append(RecipePhoto.from_dict(photo_data))
            elif isinstance(photo_data, RecipePhoto):
                self.photos.append(photo_data)
        
        self.video_url = kwargs.get('video_url', '')
        
        # Storage and versioning
        self.created_at = kwargs.get('created_at')
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.fromisoformat(self.created_at)
            except ValueError:
                self.created_at = datetime.now()
        elif self.created_at is None:
            self.created_at = datetime.now()
        
        self.updated_at = kwargs.get('updated_at')
        if isinstance(self.updated_at, str):
            try:
                self.updated_at = datetime.fromisoformat(self.updated_at)
            except ValueError:
                self.updated_at = datetime.now()
        elif self.updated_at is None:
            self.updated_at = datetime.now()
        
        self.version = kwargs.get('version', 1)
    
    def get_name(self, language: str = 'no') -> str:
        """Get recipe name in specified language"""
        key = language
        if key in self.names and self.names[key]:
            return self.names[key]
        return self.names['no']  # Fallback to Norwegian
    
    def get_description(self, language: str = 'no') -> str:
        """Get recipe description in specified language"""
        key = f'description_{language}'
        if key in self.names and self.names[key]:
            return self.names[key]
        return self.names.get('description_no', '')  # Fallback to Norwegian
    
    def get_total_time_minutes(self) -> int:
        """Calculate total time from prep + cook + rest time"""
        return self.prep_time_minutes + self.cook_time_minutes + self.rest_time_minutes
    
    def add_ingredient(
        self,
        ingredient_id: str,
        quantity: str = "",
        unit: str = "",
        preparation: str = "",
        note: str = "",
        optional: bool = False,
        group: str = ""
    ) -> None:
        """Add an ingredient to the recipe"""
        recipe_ingredient = RecipeIngredient(
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit,
            preparation=preparation,
            note=note,
            optional=optional,
            group=group
        )
        self.recipe_ingredients.append(recipe_ingredient)
        self.updated_at = datetime.now()
        self.version += 1
    
    def remove_ingredient(self, ingredient_id: str) -> bool:
        """Remove an ingredient from the recipe"""
        original_length = len(self.recipe_ingredients)
        self.recipe_ingredients = [
            ing for ing in self.recipe_ingredients 
            if ing.ingredient_id != ingredient_id
        ]
        
        if len(self.recipe_ingredients) < original_length:
            self.updated_at = datetime.now()
            self.version += 1
            return True
        return False
    
    def add_step(
        self,
        instruction_no: str,
        instruction_en: str = "",
        time_minutes: Optional[int] = None,
        temperature_celsius: Optional[int] = None
    ) -> None:
        """Add a preparation step to the recipe"""
        step_number = len(self.preparation_steps) + 1
        step = RecipeStep(
            step_number=step_number,
            instruction_no=instruction_no,
            instruction_en=instruction_en,
            time_minutes=time_minutes,
            temperature_celsius=temperature_celsius
        )
        self.preparation_steps.append(step)
        self.updated_at = datetime.now()
        self.version += 1
    
    def load_ingredients(self, ingredient_library: Dict[str, Ingredient]) -> None:
        """Load full ingredient data from the ingredient library"""
        for recipe_ingredient in self.recipe_ingredients:
            recipe_ingredient.load_ingredient(ingredient_library)
    
    def calculate_nutrition_per_serving(self) -> Optional[NutritionInfo]:
        """Calculate nutrition information per serving from loaded ingredients"""
        if not self.servings or self.servings <= 0:
            return None
        
        total_nutrition = NutritionInfo()
        
        for recipe_ingredient in self.recipe_ingredients:
            if not recipe_ingredient.ingredient:
                continue  # Skip if ingredient not loaded
            
            # This is a simplified calculation - in reality, you'd need to
            # parse quantities and convert units properly
            # For now, we'll just add up the base nutritional values
            ing_nutrition = recipe_ingredient.ingredient.nutrition
            
            total_nutrition.calories += ing_nutrition.calories
            total_nutrition.protein += ing_nutrition.protein
            total_nutrition.carbs += ing_nutrition.carbs
            total_nutrition.fat += ing_nutrition.fat
            total_nutrition.fiber += ing_nutrition.fiber
            total_nutrition.sugar += ing_nutrition.sugar
            total_nutrition.sodium += ing_nutrition.sodium
            
            # Combine vitamins and minerals
            for vitamin, amount in ing_nutrition.vitamins.items():
                if vitamin in total_nutrition.vitamins:
                    total_nutrition.vitamins[vitamin] += amount
                else:
                    total_nutrition.vitamins[vitamin] = amount
            
            for mineral, amount in ing_nutrition.minerals.items():
                if mineral in total_nutrition.minerals:
                    total_nutrition.minerals[mineral] += amount
                else:
                    total_nutrition.minerals[mineral] = amount
        
        # Divide by servings to get per-serving values
        total_nutrition.calories /= self.servings
        total_nutrition.protein /= self.servings
        total_nutrition.carbs /= self.servings
        total_nutrition.fat /= self.servings
        total_nutrition.fiber /= self.servings
        total_nutrition.sugar /= self.servings
        total_nutrition.sodium /= self.servings
        
        for vitamin in total_nutrition.vitamins:
            total_nutrition.vitamins[vitamin] /= self.servings
        
        for mineral in total_nutrition.minerals:
            total_nutrition.minerals[mineral] /= self.servings
        
        return total_nutrition
    
    def estimate_cost(self) -> float:
        """Estimate recipe cost from loaded ingredient prices"""
        total_cost = 0.0
        
        for recipe_ingredient in self.recipe_ingredients:
            if not recipe_ingredient.ingredient:
                continue  # Skip if ingredient not loaded
            
            # Simplified cost calculation - in reality, you'd parse quantities
            # and calculate based on actual amounts used
            price_per_kg = recipe_ingredient.ingredient.price_info.average_price_per_kg
            if price_per_kg > 0 and recipe_ingredient.ingredient.typical_weight_grams > 0:
                # Rough estimate based on typical weight
                ingredient_cost = (price_per_kg * recipe_ingredient.ingredient.typical_weight_grams) / 1000
                total_cost += ingredient_cost
        
        return total_cost
    
    def get_cost_per_serving(self) -> float:
        """Get estimated cost per serving"""
        total_cost = self.estimate_cost()
        if self.servings > 0:
            return total_cost / self.servings
        return total_cost
    
    def scale_recipe(self, scale_factor: float) -> 'Recipe':
        """Create a scaled version of this recipe"""
        # Create a new recipe with scaled properties
        scaled_recipe = Recipe(
            name_no=f"{self.names['no']} (x{scale_factor})",
            name_en=f"{self.names['en']} (x{scale_factor})" if self.names['en'] else "",
            description_no=self.names.get('description_no', ''),
            description_en=self.names.get('description_en', ''),
            servings=int(self.servings * scale_factor) if self.servings else 0,
            prep_time_minutes=self.prep_time_minutes,
            cook_time_minutes=self.cook_time_minutes,
            rest_time_minutes=self.rest_time_minutes,
            categories=self.categories.copy(),
            tags=self.tags.copy(),
            difficulty=self.difficulty,
            cuisine=self.cuisine,
            meal_type=self.meal_type,
            seasons=self.seasons.copy(),
            rating=self.rating,
            source=self.source,
            source_url=self.source_url,
            author=self.author
        )
        
        # Scale ingredients (quantities would need proper parsing in real implementation)
        for recipe_ingredient in self.recipe_ingredients:
            scaled_recipe.recipe_ingredients.append(RecipeIngredient(
                ingredient_id=recipe_ingredient.ingredient_id,
                quantity=recipe_ingredient.quantity,  # Would need actual scaling
                unit=recipe_ingredient.unit,
                preparation=recipe_ingredient.preparation,
                note=recipe_ingredient.note,
                optional=recipe_ingredient.optional,
                group=recipe_ingredient.group
            ))
        
        # Copy preparation steps (no scaling needed)
        scaled_recipe.preparation_steps = [
            RecipeStep(
                step_number=step.step_number,
                instruction_no=step.instruction_no,
                instruction_en=step.instruction_en,
                time_minutes=step.time_minutes,
                temperature_celsius=step.temperature_celsius,
                temperature_fahrenheit=step.temperature_fahrenheit
            ) for step in self.preparation_steps
        ]
        
        return scaled_recipe
    
    def get_shopping_list(self, language: str = 'no') -> List[Dict[str, str]]:
        """Generate a shopping list from recipe ingredients"""
        shopping_list = []
        
        for recipe_ingredient in self.recipe_ingredients:
            if recipe_ingredient.optional:
                continue  # Skip optional ingredients
            
            shopping_item = {
                'name': recipe_ingredient.get_ingredient_name(language),
                'quantity': recipe_ingredient.quantity,
                'unit': recipe_ingredient.unit,
                'note': recipe_ingredient.note,
                'ingredient_id': recipe_ingredient.ingredient_id
            }
            shopping_list.append(shopping_item)
        
        return shopping_list
    
    def is_suitable_for_season(self, season: Union[Season, str]) -> bool:
        """Check if recipe is suitable for a specific season"""
        if not self.seasons:
            return True  # Available year-round if no seasons specified
        
        if isinstance(season, str):
            try:
                season = Season(season)
            except ValueError:
                return False
        
        return season in self.seasons

    def set_as_ingredient_producer(
        self,
        ingredient_id: str,
        yield_amount: float = 0.0,
        yield_unit: str = ""
    ) -> None:
        """
        Configure this recipe as producing an ingredient for other recipes.

        Args:
            ingredient_id: ID of the ingredient this recipe produces
            yield_amount: Amount produced (optional)
            yield_unit: Unit of the yield (optional)
        """
        self.produces_ingredient = True
        self.produced_ingredient_id = ingredient_id
        if yield_amount > 0:
            self.yield_amount = yield_amount
        if yield_unit:
            self.yield_unit = yield_unit
        self.updated_at = datetime.now()
        self.version += 1

    def remove_ingredient_production(self) -> None:
        """Stop this recipe from producing an ingredient."""
        self.produces_ingredient = False
        self.produced_ingredient_id = ""
        self.updated_at = datetime.now()
        self.version += 1

    def is_ingredient_producer(self) -> bool:
        """Check if this recipe produces an ingredient for other recipes."""
        return self.produces_ingredient and bool(self.produced_ingredient_id)

    def get_produced_ingredient_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the ingredient this recipe produces.

        Returns:
            Dictionary with ingredient production info or None if not a producer
        """
        if not self.is_ingredient_producer():
            return None

        return {
            'ingredient_id': self.produced_ingredient_id,
            'yield_amount': self.yield_amount,
            'yield_unit': self.yield_unit,
            'recipe_id': self.id,
            'recipe_name': self.get_name()
        }

    def can_be_used_in_recipe(self, ingredient_library: Dict[str, Ingredient]) -> bool:
        """
        Check if this recipe can be used as an ingredient in other recipes.
        Requires that the produced ingredient exists in the ingredient library.

        Args:
            ingredient_library: Dictionary of ingredient ID -> Ingredient

        Returns:
            True if this recipe produces an ingredient that exists in the library
        """
        return (self.is_ingredient_producer() and
                self.produced_ingredient_id in ingredient_library)

    def to_dict(self) -> Dict[str, Any]:
        """Convert recipe to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'names': self.names,
            'recipe_ingredients': [ing.to_dict() for ing in self.recipe_ingredients],
            'preparation_steps': [step.to_dict() for step in self.preparation_steps],
            'prep_time_minutes': self.prep_time_minutes,
            'cook_time_minutes': self.cook_time_minutes,
            'rest_time_minutes': self.rest_time_minutes,
            'servings': self.servings,
            'yield_amount': self.yield_amount,
            'yield_unit': self.yield_unit,
            'produces_ingredient': self.produces_ingredient,
            'produced_ingredient_id': self.produced_ingredient_id,
            'categories': self.categories,
            'tags': self.tags,
            'difficulty': self.difficulty.value if self.difficulty else '',
            'cuisine': self.cuisine,
            'meal_type': self.meal_type.value if self.meal_type else '',
            'seasons': [s.value for s in self.seasons],
            'rating': self.rating,
            'source': self.source,
            'source_url': self.source_url,
            'author': self.author,
            'photos': [photo.to_dict() for photo in self.photos],
            'video_url': self.video_url,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'updated_at': self.updated_at.isoformat() if self.updated_at else '',
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """Create recipe from dictionary data"""
        recipe_id = data.get('id', str(uuid.uuid4()))
        name_no = data.get('names', {}).get('no', '')
        
        if not name_no:
            raise ValueError("Recipe must have a Norwegian name")
        
        return cls(
            recipe_id=recipe_id,
            name_no=name_no,
            **{k: v for k, v in data.items() if k not in ['id', 'names']}
        )
    
    def __str__(self) -> str:
        """String representation showing Norwegian and English names"""
        if self.names['en']:
            return f"{self.names['no']} ({self.names['en']})"
        return self.names['no']
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging"""
        return f"Recipe(id='{self.id}', name_no='{self.names['no']}', servings={self.servings})"


# Factory functions for common recipe types

def create_basic_recipe(name_no: str, name_en: str = "", servings: int = 4) -> Recipe:
    """
    Factory function to create a basic recipe with minimal information.
    
    Args:
        name_no: Norwegian recipe name
        name_en: English recipe name (optional)
        servings: Number of servings (default: 4)
        
    Returns:
        Basic Recipe instance
    """
    return Recipe(
        name_no=name_no,
        name_en=name_en,
        servings=servings
    )


def create_timed_recipe(
    name_no: str,
    prep_time: int,
    cook_time: int,
    servings: int = 4,
    difficulty: str = "medium"
) -> Recipe:
    """
    Factory function to create a recipe with timing information.
    
    Args:
        name_no: Norwegian recipe name
        prep_time: Preparation time in minutes
        cook_time: Cooking time in minutes
        servings: Number of servings
        difficulty: Difficulty level
        
    Returns:
        Recipe instance with timing information
    """
    return Recipe(
        name_no=name_no,
        prep_time_minutes=prep_time,
        cook_time_minutes=cook_time,
        servings=servings,
        difficulty=difficulty
    )