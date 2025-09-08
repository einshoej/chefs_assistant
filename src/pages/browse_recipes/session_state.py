"""
Session state management for browse recipes page
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize session state for recipes if not already set"""
    # Initialize recipe storage in session state
    if 'local_recipes' not in st.session_state:
        st.session_state.local_recipes = []
    if 'default_recipes' not in st.session_state:
        st.session_state.default_recipes = []
    if 'weekly_recipes' not in st.session_state:
        st.session_state.weekly_recipes = []
    if 'weekly_plans' not in st.session_state:
        st.session_state.weekly_plans = {}
    
    # Load default recipes if not already loaded
    if not st.session_state.get('default_recipes_loaded', False):
        load_default_recipes()
    
    # Try to load from Google Drive if not already loaded
    if not st.session_state.get('recipes_loaded_from_drive', False):
        load_recipes_from_drive()
    
    # Mark as initialized
    st.session_state.recipes_loaded = True


def load_default_recipes():
    """Load default recipes from exported JSON file"""
    try:
        from src.data.default_recipes import load_default_recipes as load_defaults
        
        default_recipes = load_defaults()
        if default_recipes:
            st.session_state.default_recipes = default_recipes
            logger.info(f"Loaded {len(default_recipes)} default recipes")
            st.session_state.default_recipes_loaded = True
        else:
            logger.info("No default recipes found")
            st.session_state.default_recipes = []
            st.session_state.default_recipes_loaded = True
            
    except Exception as e:
        logger.error(f"Error loading default recipes: {e}")
        st.session_state.default_recipes = []
        st.session_state.default_recipes_loaded = True


def load_recipes_from_drive():
    """Load recipes from Google Drive if available"""
    try:
        from src.data.google_drive_storage import get_google_drive_storage
        
        storage = get_google_drive_storage()
        if storage:
            # Load recipes
            recipes_data = storage.load_recipes()
            if recipes_data:
                st.session_state.local_recipes = recipes_data.get('local_recipes', [])
                logger.info(f"Loaded {len(st.session_state.local_recipes)} local recipes from Drive")
            
            # Load meal plans
            meal_plans_data = storage.load_meal_plans()
            if meal_plans_data:
                st.session_state.weekly_plans = meal_plans_data.get('weekly_plans', {})
                logger.info(f"Loaded {len(st.session_state.weekly_plans)} meal plans from Drive")
            
            # Load weekly recipes
            weekly_data = storage.load_weekly_recipes()
            if weekly_data:
                st.session_state.weekly_recipes = weekly_data.get('current_week', [])
                logger.info(f"Loaded {len(st.session_state.weekly_recipes)} weekly recipes from Drive")
            
            st.session_state.recipes_loaded_from_drive = True
            
    except Exception as e:
        logger.error(f"Error loading recipes from Drive: {e}")


def save_recipes_to_drive():
    """Save all recipes to Google Drive if available"""
    try:
        from src.data.google_drive_storage import get_google_drive_storage
        
        storage = get_google_drive_storage()
        if storage:
            # Prepare recipes data
            recipes_data = {
                'local_recipes': st.session_state.get('local_recipes', [])
            }
            
            # Save recipes
            if storage.save_recipes(recipes_data):
                logger.info("Saved recipes to Google Drive")
                return True
            else:
                logger.error("Failed to save recipes to Google Drive")
                return False
                
    except Exception as e:
        logger.error(f"Error saving recipes to Drive: {e}")
        return False


def save_weekly_recipes():
    """Save current weekly recipes to Google Drive if available"""
    try:
        from src.data.google_drive_storage import get_google_drive_storage
        
        storage = get_google_drive_storage()
        if storage:
            # Prepare weekly recipes data
            weekly_data = {
                'current_week': st.session_state.get('weekly_recipes', []),
                'weekly_plans': st.session_state.get('weekly_plans', {})
            }
            
            # Save weekly recipes
            if storage.save_weekly_recipes(weekly_data):
                logger.info("Saved weekly recipes to Google Drive")
                
    except Exception as e:
        logger.error(f"Error saving weekly recipes to Drive: {e}")


def get_all_recipes():
    """Get all available recipes from session state"""
    all_recipes = []
    
    # Add default recipes first
    if 'default_recipes' in st.session_state:
        all_recipes.extend(st.session_state.default_recipes)
    
    # Add local recipes if available
    if 'local_recipes' in st.session_state:
        all_recipes.extend(st.session_state.local_recipes)
    
    return all_recipes


def get_recipe_counts():
    """Get counts of recipes from different sources"""
    counts = {
        'default': len(st.session_state.get('default_recipes', [])),
        'local': len(st.session_state.get('local_recipes', [])),
        'weekly': len(st.session_state.get('weekly_recipes', [])),
        'total': len(get_all_recipes())
    }
    return counts


def get_default_recipes_info():
    """Get information about default recipes"""
    try:
        from src.data.default_recipes import get_default_recipes_info as get_info
        return get_info()
    except Exception as e:
        logger.error(f"Error getting default recipes info: {e}")
        return None


def add_to_weekly_recipes(recipe):
    """Add a recipe to the weekly recipes"""
    if 'weekly_recipes' not in st.session_state:
        st.session_state.weekly_recipes = []
    st.session_state.weekly_recipes.append(recipe)
