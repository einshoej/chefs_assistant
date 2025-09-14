"""
Ingredient extractor utility - parses ingredient strings and builds ingredient library
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from src.models.ingredient import Ingredient, create_basic_ingredient

logger = logging.getLogger(__name__)


@dataclass
class ParsedIngredient:
    """Represents a parsed ingredient from recipe text"""
    quantity: str
    unit: str
    name: str
    preparation: str
    original_text: str
    confidence: float  # 0-1 how confident we are in the parsing


class IngredientExtractor:
    """Extracts and normalizes ingredients from recipe text"""

    # Common Norwegian units
    NORWEGIAN_UNITS = {
        'stk', 'stykk', 'stykker',
        'dl', 'l', 'liter',
        'g', 'gram', 'kg', 'kilogram',
        'ss', 'spiseskje', 'spiseskjeer',
        'ts', 'teskje', 'teskjeer',
        'kopp', 'kopper', 'beger',
        'pakke', 'pakker',
        'boks', 'bokser',
        'flaske', 'flasker',
        'pose', 'poser',
        'neve', 'never',
        'klype', 'klype',
        'dråpe', 'dråper'
    }

    # Common English units
    ENGLISH_UNITS = {
        'cup', 'cups', 'c',
        'tbsp', 'tablespoon', 'tablespoons',
        'tsp', 'teaspoon', 'teaspoons',
        'oz', 'ounce', 'ounces',
        'lb', 'pound', 'pounds',
        'pt', 'pint', 'pints',
        'qt', 'quart', 'quarts',
        'gal', 'gallon', 'gallons',
        'ml', 'milliliter', 'milliliters',
        'can', 'cans', 'jar', 'jars',
        'package', 'packages', 'pkg',
        'piece', 'pieces', 'pc',
        'slice', 'slices',
        'pinch', 'pinches',
        'dash', 'dashes',
        'drop', 'drops'
    }

    ALL_UNITS = NORWEGIAN_UNITS | ENGLISH_UNITS

    # Common preparation terms (Norwegian)
    PREPARATION_TERMS = {
        'hakket', 'kuttet', 'skåret', 'revet', 'malt', 'presset',
        'kokt', 'stekt', 'rørt', 'pisket', 'blandet',
        'fersk', 'tørr', 'tørket', 'frossen', 'tint',
        'fin', 'grov', 'tynn', 'tykk',
        'hel', 'halv', 'kvart',
        'renset', 'skrelt', 'utsteinet',
        'chopped', 'diced', 'sliced', 'minced', 'grated',
        'fresh', 'dried', 'frozen', 'cooked', 'raw'
    }

    @classmethod
    def parse_ingredient_text(cls, text: str) -> ParsedIngredient:
        """
        Parse ingredient text into components

        Examples:
        "2 dl melk" -> quantity=2, unit=dl, name=melk
        "500 g hakket kjøttdeig" -> quantity=500, unit=g, name=kjøttdeig, prep=hakket
        "1 stor løk, hakket" -> quantity=1, unit=stor, name=løk, prep=hakket
        """
        original = text.strip()
        text = original.lower()

        # Initialize result
        result = ParsedIngredient(
            quantity="",
            unit="",
            name="",
            preparation="",
            original_text=original,
            confidence=0.5
        )

        # Pattern 1: Number + unit + ingredient (+ preparation)
        # "2 dl melk" or "500 g hakket kjøttdeig"
        pattern1 = r'^(\d+(?:[.,]\d+)?)\s+([a-zæøå]+)\s+(.+)$'
        match1 = re.match(pattern1, text)

        if match1:
            qty, unit, rest = match1.groups()
            result.quantity = qty.replace(',', '.')

            if unit in cls.ALL_UNITS:
                result.unit = unit
                result.confidence += 0.3
            else:
                # Unit might be part of name (like "stor løk")
                rest = f"{unit} {rest}"
                result.unit = ""

            # Split rest into name and preparation
            name_and_prep = cls._extract_preparation(rest)
            result.name = name_and_prep['name']
            result.preparation = name_and_prep['preparation']

            if result.name:
                result.confidence += 0.2

            return result

        # Pattern 2: Fraction + unit + ingredient
        # "1/2 kopp sukker"
        pattern2 = r'^(\d+/\d+)\s+([a-zæøå]+)\s+(.+)$'
        match2 = re.match(pattern2, text)

        if match2:
            qty, unit, rest = match2.groups()
            result.quantity = qty

            if unit in cls.ALL_UNITS:
                result.unit = unit
                result.confidence += 0.3
            else:
                rest = f"{unit} {rest}"
                result.unit = ""

            name_and_prep = cls._extract_preparation(rest)
            result.name = name_and_prep['name']
            result.preparation = name_and_prep['preparation']
            result.confidence += 0.2

            return result

        # Pattern 3: Just ingredient name with optional preparation
        # "salt", "hakket persille"
        name_and_prep = cls._extract_preparation(text)
        result.name = name_and_prep['name']
        result.preparation = name_and_prep['preparation']

        if result.name:
            result.confidence += 0.1

        return result

    @classmethod
    def _extract_preparation(cls, text: str) -> Dict[str, str]:
        """Extract preparation method from ingredient name"""
        text = text.strip()

        # Look for preparation terms
        for prep_term in cls.PREPARATION_TERMS:
            if prep_term in text:
                # Remove preparation term to get clean name
                name = text.replace(prep_term, '').strip()
                name = re.sub(r'\s+', ' ', name)  # Clean multiple spaces
                name = name.strip(',')  # Remove trailing commas

                return {
                    'name': name,
                    'preparation': prep_term
                }

        # Check for comma-separated preparation
        # "løk, hakket"
        if ',' in text:
            parts = text.split(',')
            if len(parts) == 2:
                name = parts[0].strip()
                prep = parts[1].strip()

                # Check if second part is likely preparation
                if any(term in prep for term in cls.PREPARATION_TERMS):
                    return {
                        'name': name,
                        'preparation': prep
                    }

        return {
            'name': text.strip(),
            'preparation': ""
        }

    @classmethod
    def extract_ingredients_from_recipe(cls, recipe_dict: Dict) -> List[ParsedIngredient]:
        """Extract all ingredients from a recipe dictionary"""
        ingredients = []

        # Get ingredients list from recipe
        recipe_ingredients = recipe_dict.get('ingredients', [])

        for ingredient_item in recipe_ingredients:
            parsed = None

            if isinstance(ingredient_item, str) and ingredient_item.strip():
                # Simple string format
                parsed = cls.parse_ingredient_text(ingredient_item)
            elif isinstance(ingredient_item, dict):
                # Structured format from export
                parsed = cls._parse_structured_ingredient(ingredient_item)

            if parsed:
                ingredients.append(parsed)

        return ingredients

    @classmethod
    def _parse_structured_ingredient(cls, ing_dict: Dict) -> ParsedIngredient:
        """Parse structured ingredient dictionary"""
        name = ing_dict.get('name', '').strip()
        quantity = ing_dict.get('quantity', '').strip()
        note = ing_dict.get('note', '').strip()
        raw_text = ing_dict.get('rawText', '')

        # Extract unit from quantity if present
        unit = ""
        if quantity:
            # Try to separate quantity and unit
            import re
            match = re.match(r'^([0-9/.,\s]+)(.*)$', quantity)
            if match:
                qty_part = match.group(1).strip()
                unit_part = match.group(2).strip()
                quantity = qty_part
                unit = unit_part

        # Combine note as preparation
        preparation = note

        return ParsedIngredient(
            quantity=quantity,
            unit=unit,
            name=name,
            preparation=preparation,
            original_text=raw_text or f"{quantity} {unit} {name}".strip(),
            confidence=0.8  # High confidence for structured data
        )

    @classmethod
    def build_ingredient_library(cls, recipes: List[Dict]) -> Dict[str, Ingredient]:
        """Build ingredient library from all recipes"""
        ingredient_names = set()
        ingredient_usage = {}  # Track how often each ingredient is used

        # First pass: collect all unique ingredient names
        for recipe in recipes:
            parsed_ingredients = cls.extract_ingredients_from_recipe(recipe)

            for parsed_ing in parsed_ingredients:
                if parsed_ing.name:
                    # Normalize name
                    name = cls._normalize_ingredient_name(parsed_ing.name)
                    ingredient_names.add(name)

                    # Track usage
                    if name not in ingredient_usage:
                        ingredient_usage[name] = []
                    ingredient_usage[name].append({
                        'recipe_id': recipe.get('id', ''),
                        'recipe_name': recipe.get('name', ''),
                        'quantity': parsed_ing.quantity,
                        'unit': parsed_ing.unit,
                        'preparation': parsed_ing.preparation
                    })

        # Second pass: create Ingredient objects
        ingredient_library = {}

        for name in ingredient_names:
            ingredient_id = cls._generate_ingredient_id(name)

            # Determine category based on name patterns
            category = cls._determine_ingredient_category(name)

            # Create ingredient with Norwegian name (most recipes are in Norwegian)
            ingredient = create_basic_ingredient(
                ingredient_id=ingredient_id,
                name_no=name,
                category=category
            )

            # Add usage statistics as metadata
            ingredient.usage_count = len(ingredient_usage.get(name, []))
            ingredient.usage_examples = ingredient_usage.get(name, [])[:5]  # First 5 examples

            ingredient_library[ingredient_id] = ingredient

        logger.info(f"Built ingredient library with {len(ingredient_library)} ingredients")
        return ingredient_library

    @classmethod
    def _normalize_ingredient_name(cls, name: str) -> str:
        """Normalize ingredient name for consistency"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())

        # Remove parenthetical notes
        name = re.sub(r'\([^)]*\)', '', name).strip()

        # Remove size descriptors that vary
        size_terms = ['stor', 'liten', 'medium', 'små', 'store']
        words = name.split()
        words = [w for w in words if w not in size_terms]
        name = ' '.join(words)

        return name.strip()

    @classmethod
    def _generate_ingredient_id(cls, name: str) -> str:
        """Generate a consistent ID for an ingredient"""
        # Convert to lowercase, replace spaces with underscores
        ingredient_id = name.lower()
        ingredient_id = re.sub(r'[æ]', 'ae', ingredient_id)
        ingredient_id = re.sub(r'[ø]', 'o', ingredient_id)
        ingredient_id = re.sub(r'[å]', 'aa', ingredient_id)
        ingredient_id = re.sub(r'[^a-z0-9\s]', '', ingredient_id)
        ingredient_id = re.sub(r'\s+', '_', ingredient_id)

        return ingredient_id

    @classmethod
    def _determine_ingredient_category(cls, name: str) -> str:
        """Determine ingredient category based on name patterns"""
        name_lower = name.lower()

        # Meat and fish
        meat_keywords = ['kjøtt', 'beef', 'kylling', 'chicken', 'fisk', 'fish', 'laks', 'torsk']
        if any(keyword in name_lower for keyword in meat_keywords):
            return 'protein'

        # Dairy
        dairy_keywords = ['melk', 'milk', 'ost', 'cheese', 'smør', 'butter', 'fløte', 'cream']
        if any(keyword in name_lower for keyword in dairy_keywords):
            return 'dairy'

        # Vegetables
        veg_keywords = ['løk', 'onion', 'gulrot', 'carrot', 'tomat', 'tomato', 'pepper', 'salat']
        if any(keyword in name_lower for keyword in veg_keywords):
            return 'vegetable'

        # Fruits
        fruit_keywords = ['eple', 'apple', 'banan', 'banana', 'sitron', 'lemon', 'appelsin']
        if any(keyword in name_lower for keyword in fruit_keywords):
            return 'fruit'

        # Grains and carbs
        grain_keywords = ['mel', 'flour', 'ris', 'rice', 'pasta', 'brød', 'bread', 'havre', 'oats']
        if any(keyword in name_lower for keyword in grain_keywords):
            return 'grain'

        # Seasonings
        seasoning_keywords = ['salt', 'pepper', 'krydder', 'spice', 'basilikum', 'oregano', 'timian']
        if any(keyword in name_lower for keyword in seasoning_keywords):
            return 'seasoning'

        return 'other'

    @classmethod
    def save_ingredient_library(cls, ingredient_library: Dict[str, Ingredient], filepath: str) -> None:
        """Save ingredient library to JSON file"""
        # Convert ingredients to dictionary format
        library_dict = {}
        for ingredient_id, ingredient in ingredient_library.items():
            library_dict[ingredient_id] = ingredient.to_dict()

        # Create export metadata
        export_data = {
            'export_info': {
                'exported_at': '2025-09-14T00:00:00',
                'total_ingredients': len(library_dict),
                'extraction_method': 'automated_from_recipes'
            },
            'ingredients': library_dict
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved ingredient library with {len(library_dict)} ingredients to {filepath}")


# Convenience functions for external use

def extract_ingredients_from_recipes(recipes: List[Dict]) -> Dict[str, Ingredient]:
    """Extract ingredient library from recipe list"""
    return IngredientExtractor.build_ingredient_library(recipes)


def parse_ingredient_string(ingredient_text: str) -> ParsedIngredient:
    """Parse a single ingredient string"""
    return IngredientExtractor.parse_ingredient_text(ingredient_text)