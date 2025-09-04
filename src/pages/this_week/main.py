"""
This Week page - Display the current week's recipes
"""

import streamlit as st
from src.pages.this_week.recipe_components import (
    display_recipe_card,
    display_clear_button
)
from src.pages.this_week.session_manager import WeeklyRecipeManager


def display_header() -> None:
    """Display the page header"""
    st.header("This Week")


def display_recipes(recipes: list) -> None:
    """Display all recipes in the weekly plan using two-column grid layout
    
    Args:
        recipes: List of recipe dictionaries to display
    """
    if not recipes:
        return
        
    # Display recipes in two-column grid
    col1, col2 = st.columns(2, gap="medium")
    
    for i, recipe in enumerate(recipes):
        meal_number = i + 1
        
        # Alternate between columns
        if i % 2 == 0:
            with col1:
                display_recipe_card(recipe, meal_number, i)
        else:
            with col2:
                display_recipe_card(recipe, meal_number, i)


def handle_clear_action() -> None:
    """Handle the clear all recipes action"""
    if WeeklyRecipeManager.has_recipes() and display_clear_button():
        WeeklyRecipeManager.clear_all()
        st.rerun()


def main() -> None:
    """Main orchestrator function for the This Week page"""
    # Initialize session state
    WeeklyRecipeManager.initialize()
    
    # Display page header
    display_header()
    
    # Get recipes from session state
    recipes = WeeklyRecipeManager.get_recipes()
    
    # Display content based on whether recipes exist
    if WeeklyRecipeManager.get_recipe_count() == 0:
        st.error("No recipes available!",icon=":material/no_sim:")
    elif not recipes:
        st.warning("No recipes selected for this week. Go to 'Browse Recipes' to add recipes to your plan!",icon=":material/no_shopping_cart:")
    else:
        display_recipes(recipes)
        handle_clear_action()


# Streamlit page entry point
if __name__ == "__page__":
    main()