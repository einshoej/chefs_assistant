"""
View Recipe page - Full-page recipe viewer with elegant UI
"""

import streamlit as st
from src.pages.view_recipe.session_state import (
    initialize_session_state, 
    get_all_recipes, 
    get_selected_recipe, 
    set_selected_recipe
)
from src.pages.view_recipe.recipe_viewer_components import (
    display_recipe_selector,
    display_recipe_hero,
    display_ingredients_section,
    display_instructions_section,
    display_recipe_details
)
from src.components.nutrition_card import display_nutrition_card, display_daily_values
from src.components.price_estimator import display_price_card, display_price_breakdown
from src.models.recipe import Recipe


def view_recipe():
    """Main function for the recipe viewer page"""
    
    # Initialize session state
    initialize_session_state()
    
    
    # Get all available recipes
    all_recipes = get_all_recipes()
    
    if not all_recipes:
        st.error("📚 No recipes available. Please check that default recipes are loaded.")
        return
    
    # Get currently selected recipe
    current_recipe = get_selected_recipe()
    
    # Recipe selector at the top
    selected_recipe = display_recipe_selector(all_recipes, current_recipe)
    
    if not selected_recipe:
        st.error("Unable to load recipe")
        return
    
    # Update session state if selection changed
    if current_recipe != selected_recipe:
        set_selected_recipe(selected_recipe.get('name', ''))
    
    st.divider()
    
    # Display the selected recipe in full
    display_full_recipe(selected_recipe)


def display_full_recipe(recipe):
    """Display the complete recipe with all sections"""
    
    if not recipe:
        st.error("No recipe selected")
        return
    
    # Hero section with image, title, and badges
    display_recipe_hero(recipe)
    
    # Add spacing
    st.markdown("")
    
    # Ingredients section (full width)
    display_ingredients_section(recipe)
    
    # Add spacing
    st.markdown("")
    
    # Instructions section (full width)
    display_instructions_section(recipe)

    # Add spacing
    st.markdown("")

    # Nutrition and Price sections (only for Recipe objects)
    if isinstance(recipe, Recipe):
        # Use tabs for better organization
        tab1, tab2 = st.tabs(["🍽️ Næring", "💰 Kostnad"])

        with tab1:
            display_nutrition_card(recipe)
            st.markdown("")

            # Daily values
            nutrition = recipe.calculate_nutrition_per_serving()
            if nutrition:
                display_daily_values(nutrition)

        with tab2:
            display_price_card(recipe)
            st.markdown("")
            display_price_breakdown(recipe)

    # Additional details section (full width)
    st.markdown("")
    display_recipe_details(recipe)
    
view_recipe()