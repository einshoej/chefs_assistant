"""
Session state management for browse recipes page
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize session state for recipes if not already set"""
    # Initialize recipe storage in session state
    if 'anylist_recipes' not in st.session_state:
        st.session_state.anylist_recipes = []
    if 'local_recipes' not in st.session_state:
        st.session_state.local_recipes = []
    if 'weekly_recipes' not in st.session_state:
        st.session_state.weekly_recipes = []
    if 'weekly_plans' not in st.session_state:
        st.session_state.weekly_plans = {}
    
    # Try to load from Google Drive if not already loaded
    if not st.session_state.get('recipes_loaded_from_drive', False):
        load_recipes_from_drive()
    
    # Mark as initialized
    st.session_state.recipes_loaded = True


def load_recipes_from_drive():
    """Load recipes from Google Drive if available"""
    try:
        from src.data.google_drive_storage import get_google_drive_storage
        
        storage = get_google_drive_storage()
        if storage:
            # Load recipes
            recipes_data = storage.load_recipes()
            if recipes_data:
                st.session_state.anylist_recipes = recipes_data.get('anylist_recipes', [])
                st.session_state.local_recipes = recipes_data.get('local_recipes', [])
                st.session_state.last_anylist_sync = recipes_data.get('last_sync')
                logger.info(f"Loaded {len(st.session_state.anylist_recipes)} AnyList recipes from Drive")
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
                'anylist_recipes': st.session_state.get('anylist_recipes', []),
                'local_recipes': st.session_state.get('local_recipes', []),
                'last_sync': st.session_state.get('last_anylist_sync')
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
    
    # Add AnyList recipes if available
    if 'anylist_recipes' in st.session_state:
        all_recipes.extend(st.session_state.anylist_recipes)
    
    # Add local recipes if available
    if 'local_recipes' in st.session_state:
        all_recipes.extend(st.session_state.local_recipes)
    
    return all_recipes


def add_to_weekly_recipes(recipe):
    """Add a recipe to the weekly recipes"""
    if 'weekly_recipes' not in st.session_state:
        st.session_state.weekly_recipes = []
    st.session_state.weekly_recipes.append(recipe)
