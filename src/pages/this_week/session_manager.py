"""
Session state management for the This Week page
"""

import streamlit as st
from typing import List, Dict, Any
import logging
import random
from .week_utils import get_week_key

logger = logging.getLogger(__name__)


class WeeklyRecipeManager:
    """Manager for weekly recipe session state"""
    
    SESSION_KEY = 'weekly_recipes'
    WEEKLY_PLANS_KEY = 'weekly_plans'
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize session state for weekly recipes"""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = []
        if cls.WEEKLY_PLANS_KEY not in st.session_state:
            st.session_state[cls.WEEKLY_PLANS_KEY] = {}
    
    @classmethod
    def save_to_drive(cls) -> bool:
        """Save weekly recipes to Google Drive"""
        try:
            from src.data.google_drive_storage import get_google_drive_storage
            
            storage = get_google_drive_storage()
            if storage:
                # Prepare weekly recipes data
                weekly_data = {
                    'current_week': st.session_state.get(cls.SESSION_KEY, []),
                    'weekly_plans': st.session_state.get(cls.WEEKLY_PLANS_KEY, {})
                }
                
                # Save weekly recipes
                if storage.save_weekly_recipes(weekly_data):
                    logger.info("Saved weekly recipes to Google Drive")
                    return True
                else:
                    logger.error("Failed to save weekly recipes to Google Drive")
                    return False
                    
        except Exception as e:
            logger.error(f"Error saving weekly recipes to Drive: {e}")
            return False
    
    @classmethod
    def get_recipes(cls) -> List[Dict[str, Any]]:
        """Get the current week's recipes from session state
        
        Returns:
            List of recipe dictionaries
        """
        cls.initialize()  # Ensure initialization
        return st.session_state[cls.SESSION_KEY]
    
    @classmethod
    def add_recipe(cls, recipe: Dict[str, Any]) -> None:
        """Add a recipe to the weekly plan
        
        Args:
            recipe: Recipe dictionary to add
        """
        cls.initialize()
        st.session_state[cls.SESSION_KEY].append(recipe)
        # Auto-save to Drive
        cls.save_to_drive()
    
    @classmethod
    def remove_recipe(cls, index: int) -> None:
        """Remove a recipe from the weekly plan by index
        
        Args:
            index: Index of recipe to remove
        """
        recipes = cls.get_recipes()
        if 0 <= index < len(recipes):
            recipes.pop(index)
            # Auto-save to Drive
            cls.save_to_drive()
    
    @classmethod
    def clear_all(cls) -> None:
        """Clear all recipes from the weekly plan"""
        st.session_state[cls.SESSION_KEY] = []
        # Auto-save to Drive
        cls.save_to_drive()
    
    @classmethod
    def has_recipes(cls) -> bool:
        """Check if there are any recipes in the weekly plan
        
        Returns:
            True if recipes exist, False otherwise
        """
        return len(cls.get_recipes()) > 0
    
    @classmethod
    def get_recipe_count(cls) -> int:
        """Get the number of recipes in the weekly plan
        
        Returns:
            Number of recipes
        """
        return len(cls.get_recipes())
    
    # New methods for multi-week support
    
    @classmethod
    def get_recipes_for_week(cls, week_offset: int) -> List[Dict[str, Any]]:
        """Get recipes for a specific week offset from current week
        
        Args:
            week_offset: Number of weeks from current week (0 = this week, 1 = next week, etc.)
            
        Returns:
            List of recipe dictionaries for the specified week
        """
        cls.initialize()
        week_key = get_week_key(week_offset)
        return st.session_state[cls.WEEKLY_PLANS_KEY].get(week_key, [])
    
    @classmethod
    def add_recipe_to_week(cls, recipe: Dict[str, Any], week_offset: int) -> None:
        """Add a recipe to a specific week
        
        Args:
            recipe: Recipe dictionary to add
            week_offset: Number of weeks from current week
        """
        cls.initialize()
        week_key = get_week_key(week_offset)
        
        if week_key not in st.session_state[cls.WEEKLY_PLANS_KEY]:
            st.session_state[cls.WEEKLY_PLANS_KEY][week_key] = []
        
        st.session_state[cls.WEEKLY_PLANS_KEY][week_key].append(recipe)
        cls.save_to_drive()
    
    @classmethod
    def remove_recipe_from_week(cls, recipe_index: int, week_offset: int) -> None:
        """Remove a recipe from a specific week by index
        
        Args:
            recipe_index: Index of recipe to remove
            week_offset: Number of weeks from current week
        """
        cls.initialize()
        week_key = get_week_key(week_offset)
        
        if week_key in st.session_state[cls.WEEKLY_PLANS_KEY]:
            recipes = st.session_state[cls.WEEKLY_PLANS_KEY][week_key]
            if 0 <= recipe_index < len(recipes):
                recipes.pop(recipe_index)
                cls.save_to_drive()
    
    @classmethod
    def clear_week(cls, week_offset: int) -> None:
        """Clear all recipes from a specific week
        
        Args:
            week_offset: Number of weeks from current week
        """
        cls.initialize()
        week_key = get_week_key(week_offset)
        st.session_state[cls.WEEKLY_PLANS_KEY][week_key] = []
        cls.save_to_drive()
    
    @classmethod
    def populate_week_with_random_recipes(cls, week_offset: int, force: bool = False) -> bool:
        """Populate a week with seasonal recipes based on user's meals_per_week preference
        
        Args:
            week_offset: Number of weeks from current week
            force: If True, populate even if week already has recipes
            
        Returns:
            bool: True if recipes were added, False if no recipes available
        """
        cls.initialize()
        
        # Check if week already has recipes (unless force is True)
        if not force and len(cls.get_recipes_for_week(week_offset)) > 0:
            return False
        
        # Get user's meals per week preference
        meals_per_week = st.session_state.get('meals_per_week', 3)
        
        # Get all available recipes
        try:
            from src.pages.browse_recipes.session_state import get_all_recipes
            all_recipes = get_all_recipes()
        except:
            logger.error("Could not import get_all_recipes function")
            return False
        
        if not all_recipes or len(all_recipes) == 0:
            logger.warning(f"No recipes available to populate week {week_offset}")
            return False
        
        # Select recipes using seasonal weighting
        num_recipes_to_add = min(meals_per_week, len(all_recipes))
        
        # Get recipes already used in other weeks to try to avoid duplicates
        used_recipe_names = set()
        for other_week in range(4):  # Check 4 weeks
            if other_week != week_offset:
                other_week_recipes = cls.get_recipes_for_week(other_week)
                for recipe in other_week_recipes:
                    used_recipe_names.add(recipe.get('name', ''))
        
        # Use seasonal recipe selector
        try:
            from src.utils.seasonal_recipe_selector import select_seasonal_recipes
            selected_recipes = select_seasonal_recipes(
                all_recipes, 
                num_recipes_to_add,
                used_recipe_names=used_recipe_names
            )
            
            if not selected_recipes:
                logger.warning(f"Seasonal selector returned no recipes for week {week_offset}")
                return False
                
            logger.info(f"Populated week {week_offset} with {len(selected_recipes)} seasonal recipes")
            
        except Exception as e:
            # Fall back to original random selection if seasonal selection fails
            logger.warning(f"Seasonal selection failed, falling back to random selection: {e}")
            
            # Try to select recipes not used in other weeks first
            unused_recipes = [r for r in all_recipes if r.get('name', '') not in used_recipe_names]
            
            if len(unused_recipes) >= num_recipes_to_add:
                # We have enough unused recipes
                selected_recipes = random.sample(unused_recipes, num_recipes_to_add)
            elif len(unused_recipes) > 0:
                # Use all unused recipes and fill the rest from all recipes
                selected_recipes = unused_recipes.copy()
                remaining_needed = num_recipes_to_add - len(unused_recipes)
                remaining_recipes = random.sample(all_recipes, remaining_needed)
                selected_recipes.extend(remaining_recipes)
            else:
                # All recipes are used, just select randomly
                selected_recipes = random.sample(all_recipes, num_recipes_to_add)
                
            logger.info(f"Populated week {week_offset} with {len(selected_recipes)} random recipes (fallback)")
        
        # Add recipes to the week
        week_key = get_week_key(week_offset)
        st.session_state[cls.WEEKLY_PLANS_KEY][week_key] = selected_recipes.copy()
        cls.save_to_drive()
        
        return True
    
    @classmethod
    def get_week_recipe_count(cls, week_offset: int) -> int:
        """Get the number of recipes for a specific week
        
        Args:
            week_offset: Number of weeks from current week
            
        Returns:
            Number of recipes for the specified week
        """
        return len(cls.get_recipes_for_week(week_offset))
    
    @classmethod
    def has_recipes_for_week(cls, week_offset: int) -> bool:
        """Check if there are any recipes for a specific week
        
        Args:
            week_offset: Number of weeks from current week
            
        Returns:
            True if recipes exist for the week, False otherwise
        """
        return cls.get_week_recipe_count(week_offset) > 0
