"""
Ingredient class for the Chef's Assistant ingredient library system.

This module defines ingredients as reusable catalog entities with multilingual names,
nutritional information, preparation methods, and culinary properties.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class StorageType(Enum):
    """Storage type for ingredients"""
    PANTRY = "pantry"
    REFRIGERATED = "refrigerated"
    FREEZER = "freezer"
    ROOM_TEMPERATURE = "room_temperature"


class Season(Enum):
    """Seasons for ingredient availability"""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


@dataclass
class NutritionInfo:
    """Nutritional information per 100g of ingredient"""
    calories: float = 0.0
    protein: float = 0.0  # grams
    carbs: float = 0.0  # grams
    fat: float = 0.0  # grams
    fiber: float = 0.0  # grams
    sugar: float = 0.0  # grams
    sodium: float = 0.0  # mg
    vitamins: Dict[str, float] = field(default_factory=dict)  # Various units
    minerals: Dict[str, float] = field(default_factory=dict)  # Various units
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'sugar': self.sugar,
            'sodium': self.sodium,
            'vitamins': self.vitamins,
            'minerals': self.minerals
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NutritionInfo':
        """Create from dictionary"""
        return cls(
            calories=data.get('calories', 0.0),
            protein=data.get('protein', 0.0),
            carbs=data.get('carbs', 0.0),
            fat=data.get('fat', 0.0),
            fiber=data.get('fiber', 0.0),
            sugar=data.get('sugar', 0.0),
            sodium=data.get('sodium', 0.0),
            vitamins=data.get('vitamins', {}),
            minerals=data.get('minerals', {})
        )


@dataclass
class PriceInfo:
    """Price and economic information for an ingredient"""
    average_price_per_kg: float = 0.0  # NOK
    average_price_per_unit: float = 0.0  # NOK
    price_updated: Optional[str] = None  # ISO date string
    seasonal_price_variation: bool = False
    typical_package_size: float = 0.0  # kg or units
    typical_package_unit: str = "kg"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'average_price_per_kg': self.average_price_per_kg,
            'average_price_per_unit': self.average_price_per_unit,
            'price_updated': self.price_updated,
            'seasonal_price_variation': self.seasonal_price_variation,
            'typical_package_size': self.typical_package_size,
            'typical_package_unit': self.typical_package_unit
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceInfo':
        """Create from dictionary"""
        return cls(
            average_price_per_kg=data.get('average_price_per_kg', 0.0),
            average_price_per_unit=data.get('average_price_per_unit', 0.0),
            price_updated=data.get('price_updated'),
            seasonal_price_variation=data.get('seasonal_price_variation', False),
            typical_package_size=data.get('typical_package_size', 0.0),
            typical_package_unit=data.get('typical_package_unit', 'kg')
        )


class Ingredient:
    """
    Represents an ingredient in the ingredient library/catalog system.
    
    Each ingredient is a reusable definition that can be referenced by recipes.
    Contains multilingual names, nutritional info, preparation methods, and culinary properties.
    """
    
    def __init__(
        self,
        ingredient_id: str,
        name_no: str,
        name_en: Optional[str] = None,
        category: str = "uncategorized",
        **kwargs
    ):
        """
        Initialize an ingredient with required Norwegian name.
        
        Args:
            ingredient_id: Unique identifier (e.g., 'carrot', 'onion')
            name_no: Norwegian name (required)
            name_en: English name (optional)
            category: Ingredient category (default: 'uncategorized')
            **kwargs: Additional optional properties
        """
        # Required fields
        self.id = ingredient_id
        self.names = {
            'no': name_no,
            'en': name_en or name_no,  # Default to Norwegian if English not provided
            'plural_no': kwargs.get('plural_no', ''),
            'plural_en': kwargs.get('plural_en', '')
        }
        
        # Basic properties
        self.category = category
        self.aliases = kwargs.get('aliases', [])
        
        # Physical properties
        self.typical_weight_grams = kwargs.get('typical_weight_grams', 0.0)
        self.density = kwargs.get('density', 1.0)  # g/cm³
        self.edible_portion = kwargs.get('edible_portion', 1.0)  # fraction (0-1)
        self.common_units = kwargs.get('common_units', ['stk', 'g'])
        
        # Preparation methods (list of dicts with 'no' and 'en' keys)
        self.preparation_methods = kwargs.get('preparation_methods', [])
        
        # Nutritional information
        nutrition_data = kwargs.get('nutrition', {})
        if isinstance(nutrition_data, dict):
            self.nutrition = NutritionInfo.from_dict(nutrition_data)
        elif isinstance(nutrition_data, NutritionInfo):
            self.nutrition = nutrition_data
        else:
            self.nutrition = NutritionInfo()
        
        # Price information
        price_data = kwargs.get('price_info', {})
        if isinstance(price_data, dict):
            self.price_info = PriceInfo.from_dict(price_data)
        elif isinstance(price_data, PriceInfo):
            self.price_info = price_data
        else:
            self.price_info = PriceInfo()
        
        # Culinary properties
        self.flavor_profile = kwargs.get('flavor_profile', [])
        self.texture = kwargs.get('texture', '')
        self.cooking_methods = kwargs.get('cooking_methods', [])
        self.common_pairings = kwargs.get('common_pairings', [])
        
        # Storage and seasonality
        self.shelf_life_days = kwargs.get('shelf_life_days', 0)
        self.storage_type = kwargs.get('storage_type', StorageType.ROOM_TEMPERATURE)
        if isinstance(self.storage_type, str):
            try:
                self.storage_type = StorageType(self.storage_type)
            except ValueError:
                self.storage_type = StorageType.ROOM_TEMPERATURE
        
        # Seasonality
        peak_seasons = kwargs.get('peak_season', [])
        self.peak_season = []
        for season in peak_seasons:
            if isinstance(season, str):
                try:
                    self.peak_season.append(Season(season))
                except ValueError:
                    continue
            elif isinstance(season, Season):
                self.peak_season.append(season)
        
        self.available_year_round = kwargs.get('available_year_round', True)
    
    def get_name(self, language: str = 'no', plural: bool = False) -> str:
        """
        Get ingredient name in specified language.
        
        Args:
            language: Language code ('no' for Norwegian, 'en' for English)
            plural: Whether to return plural form
            
        Returns:
            Ingredient name in requested language/form
        """
        if plural:
            key = f'plural_{language}'
            if key in self.names and self.names[key]:
                return self.names[key]
            # Fall back to regular form if plural not available
            return self.names.get(language, self.names['no'])
        else:
            return self.names.get(language, self.names['no'])
    
    def add_preparation_method(self, method_no: str, method_en: str = None) -> None:
        """
        Add a preparation method with Norwegian and optionally English translation.
        
        Args:
            method_no: Norwegian preparation method
            method_en: English preparation method (optional)
        """
        method = {
            'no': method_no,
            'en': method_en or method_no
        }
        if method not in self.preparation_methods:
            self.preparation_methods.append(method)
    
    def get_preparation_methods(self, language: str = 'no') -> List[str]:
        """
        Get all preparation methods in specified language.
        
        Args:
            language: Language code ('no' or 'en')
            
        Returns:
            List of preparation methods in requested language
        """
        return [method.get(language, method['no']) for method in self.preparation_methods]
    
    def set_nutrition(self, **nutrition_kwargs) -> None:
        """
        Set nutritional information using keyword arguments.
        
        Args:
            **nutrition_kwargs: Nutritional values (calories, protein, carbs, etc.)
        """
        for key, value in nutrition_kwargs.items():
            if hasattr(self.nutrition, key):
                setattr(self.nutrition, key, value)
    
    def update_price_info(self, **price_kwargs) -> None:
        """
        Update price information using keyword arguments.
        
        Args:
            **price_kwargs: Price information (average_price_per_kg, etc.)
        """
        for key, value in price_kwargs.items():
            if hasattr(self.price_info, key):
                setattr(self.price_info, key, value)
        
        # Auto-set price_updated to current date
        self.price_info.price_updated = datetime.now().isoformat()[:10]
    
    def is_in_season(self, season: Union[Season, str]) -> bool:
        """
        Check if ingredient is in peak season.
        
        Args:
            season: Season to check (Season enum or string)
            
        Returns:
            True if ingredient is in peak season or available year round
        """
        if self.available_year_round:
            return True
        
        if isinstance(season, str):
            try:
                season = Season(season)
            except ValueError:
                return False
        
        return season in self.peak_season
    
    def get_common_conversions(self) -> Dict[str, float]:
        """
        Get common unit conversions for this ingredient.
        
        Returns:
            Dictionary mapping units to their gram equivalents
        """
        conversions = {'g': 1.0, 'kg': 1000.0}
        
        if self.typical_weight_grams > 0:
            conversions['stk'] = self.typical_weight_grams
            conversions['piece'] = self.typical_weight_grams
        
        return conversions
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ingredient to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the ingredient
        """
        return {
            'id': self.id,
            'names': self.names,
            'category': self.category,
            'aliases': self.aliases,
            'typical_weight_grams': self.typical_weight_grams,
            'density': self.density,
            'edible_portion': self.edible_portion,
            'common_units': self.common_units,
            'preparation_methods': self.preparation_methods,
            'nutrition': self.nutrition.to_dict(),
            'price_info': self.price_info.to_dict(),
            'flavor_profile': self.flavor_profile,
            'texture': self.texture,
            'cooking_methods': self.cooking_methods,
            'common_pairings': self.common_pairings,
            'shelf_life_days': self.shelf_life_days,
            'storage_type': self.storage_type.value if isinstance(self.storage_type, StorageType) else self.storage_type,
            'peak_season': [s.value for s in self.peak_season],
            'available_year_round': self.available_year_round
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ingredient':
        """
        Create ingredient from dictionary data.
        
        Args:
            data: Dictionary containing ingredient data
            
        Returns:
            Ingredient instance
        """
        ingredient_id = data.get('id', '')
        name_no = data.get('names', {}).get('no', '')
        
        if not ingredient_id or not name_no:
            raise ValueError("Ingredient must have id and Norwegian name")
        
        # Extract names
        names = data.get('names', {})
        name_en = names.get('en', name_no)
        
        # Create ingredient with all data
        return cls(
            ingredient_id=ingredient_id,
            name_no=name_no,
            name_en=name_en,
            **{k: v for k, v in data.items() if k not in ['id', 'names']}
        )
    
    def __str__(self) -> str:
        """String representation showing Norwegian and English names"""
        if self.names['en'] != self.names['no']:
            return f"{self.names['no']} ({self.names['en']})"
        return self.names['no']
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging"""
        return f"Ingredient(id='{self.id}', name_no='{self.names['no']}', category='{self.category}')"


# Example usage and factory functions

def create_basic_ingredient(ingredient_id: str, name_no: str, name_en: str = None, category: str = "uncategorized") -> Ingredient:
    """
    Factory function to create a basic ingredient with minimal information.
    
    Args:
        ingredient_id: Unique identifier
        name_no: Norwegian name
        name_en: English name (optional)
        category: Category (optional)
        
    Returns:
        Basic Ingredient instance
    """
    return Ingredient(
        ingredient_id=ingredient_id,
        name_no=name_no,
        name_en=name_en,
        category=category
    )


def create_vegetable_ingredient(ingredient_id: str, name_no: str, name_en: str = None, typical_weight: float = 0.0) -> Ingredient:
    """
    Factory function to create a vegetable ingredient with common defaults.
    
    Args:
        ingredient_id: Unique identifier
        name_no: Norwegian name
        name_en: English name (optional)
        typical_weight: Typical weight in grams
        
    Returns:
        Vegetable Ingredient instance with appropriate defaults
    """
    return Ingredient(
        ingredient_id=ingredient_id,
        name_no=name_no,
        name_en=name_en,
        category="vegetable",
        typical_weight_grams=typical_weight,
        storage_type=StorageType.REFRIGERATED,
        common_units=['stk', 'g', 'kg'],
        cooking_methods=['raw', 'boiled', 'roasted', 'steamed', 'fried'],
        preparation_methods=[
            {'no': 'hel', 'en': 'whole'},
            {'no': 'skåret i skiver', 'en': 'sliced'},
            {'no': 'terninger', 'en': 'diced'},
            {'no': 'revet', 'en': 'grated'}
        ]
    )