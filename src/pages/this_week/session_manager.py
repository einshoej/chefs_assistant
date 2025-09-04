"""
Session state management for the This Week page
"""

import streamlit as st
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WeeklyRecipeManager:
    """Manager for weekly recipe session state"""
    
    SESSION_KEY = 'weekly_recipes'
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize session state for weekly recipes"""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = []
    
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
                    'weekly_plans': st.session_state.get('weekly_plans', {})
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
