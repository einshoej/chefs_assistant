"""
Session state management for view recipe page
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize session state for recipe viewing"""
    # Initialize selected recipe index
    if 'selected_recipe_idx' not in st.session_state:
        st.session_state.selected_recipe_idx = 0
    
    # Initialize recipe scaling state
    if 'recipe_scale_factors' not in st.session_state:
        st.session_state.recipe_scale_factors = {}
    
    # Initialize recipe data if needed (reuse from browse_recipes)
    if 'default_recipes' not in st.session_state:
        st.session_state.default_recipes = []
    
    # Try to load default recipes if empty
    if not st.session_state.default_recipes:
        load_default_recipes()
    
    # Check if we navigated here with a specific recipe selected
    if 'selected_recipe_name' in st.session_state:
        set_selected_recipe(st.session_state.selected_recipe_name)
        # Clear the navigation state
        del st.session_state.selected_recipe_name


def load_default_recipes():
    """Load default recipes from exported JSON file"""
    try:
        from src.data.default_recipes import load_default_recipes as load_defaults
        
        default_recipes = load_defaults()
        if default_recipes:
            st.session_state.default_recipes = default_recipes
            logger.info(f"Loaded {len(default_recipes)} default recipes for view recipe page")
        else:
            logger.info("No default recipes found")
            st.session_state.default_recipes = []
            
    except Exception as e:
        logger.error(f"Error loading default recipes: {e}")
        st.session_state.default_recipes = []


def get_all_recipes():
    """Get all available recipes"""
    all_recipes = []
    
    # Add default recipes
    if 'default_recipes' in st.session_state and st.session_state.default_recipes:
        all_recipes.extend(st.session_state.default_recipes)
    else:
        # Fallback: load default recipes directly if session state is empty
        logger.info("Session state empty, loading default recipes directly")
        try:
            from src.data.default_recipes import load_default_recipes as load_defaults
            default_recipes = load_defaults()
            if default_recipes:
                all_recipes.extend(default_recipes)
                # Try to save to session state for next time
                try:
                    st.session_state.default_recipes = default_recipes
                except:
                    pass  # Session state might not be available
        except Exception as e:
            logger.error(f"Failed to load default recipes directly: {e}")
    
    return all_recipes


def get_selected_recipe():
    """Get the currently selected recipe"""
    recipes = get_all_recipes()
    if not recipes:
        return None
    
    # Ensure selected index is within bounds
    if st.session_state.selected_recipe_idx >= len(recipes):
        st.session_state.selected_recipe_idx = 0
    
    if st.session_state.selected_recipe_idx < 0:
        st.session_state.selected_recipe_idx = 0
    
    return recipes[st.session_state.selected_recipe_idx]


def set_selected_recipe(recipe_name):
    """Set the selected recipe by name"""
    recipes = get_all_recipes()
    for idx, recipe in enumerate(recipes):
        if recipe.get('name') == recipe_name:
            st.session_state.selected_recipe_idx = idx
            return True
    return False


def get_recipe_names():
    """Get list of all recipe names for selectbox"""
    recipes = get_all_recipes()
    return [recipe.get('name', f'Recipe {idx}') for idx, recipe in enumerate(recipes)]


def get_recipe_scale_factor(recipe_name: str) -> float:
    """Get the current scale factor for a recipe"""
    if 'recipe_scale_factors' not in st.session_state:
        st.session_state.recipe_scale_factors = {}
    
    return st.session_state.recipe_scale_factors.get(recipe_name, 1.0)


def set_recipe_scale_factor(recipe_name: str, scale_factor: float):
    """Set the scale factor for a recipe"""
    if 'recipe_scale_factors' not in st.session_state:
        st.session_state.recipe_scale_factors = {}
    
    st.session_state.recipe_scale_factors[recipe_name] = scale_factor


def add_to_weekly_recipes(recipe):
    """Add a recipe to the weekly recipes"""
    if 'weekly_recipes' not in st.session_state:
        st.session_state.weekly_recipes = []
    
    # Check if recipe is already in weekly recipes
    recipe_name = recipe.get('name', '')
    existing_names = [r.get('name', '') for r in st.session_state.weekly_recipes]
    
    if recipe_name not in existing_names:
        st.session_state.weekly_recipes.append(recipe)
        logger.info(f"Added '{recipe_name}' to weekly recipes")
        return True
    else:
        logger.info(f"Recipe '{recipe_name}' already in weekly recipes")
        return False