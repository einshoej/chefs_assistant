"""
This Week page - Display multiple weeks of recipes with tabs
"""

import streamlit as st
from src.pages.this_week.recipe_components import (
    display_recipe_card,
    display_clear_button
)
from src.pages.this_week.session_manager import WeeklyRecipeManager
from src.pages.this_week.week_utils import get_relative_week_label


def display_header() -> None:
    """Display the page header"""
    st.header("Weekly Meal Plans")


def display_recipes(recipes: list, week_offset: int) -> None:
    """Display all recipes in the weekly plan using two-column grid layout
    
    Args:
        recipes: List of recipe dictionaries to display
        week_offset: Week offset for proper recipe removal handling
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
                display_recipe_card(recipe, meal_number, i, week_offset)
        else:
            with col2:
                display_recipe_card(recipe, meal_number, i, week_offset)


def handle_clear_action(week_offset: int) -> None:
    """Handle the clear all recipes action for a specific week
    
    Args:
        week_offset: Week offset to clear
    """
    if WeeklyRecipeManager.has_recipes_for_week(week_offset) and display_clear_button():
        WeeklyRecipeManager.clear_week(week_offset)
        st.rerun()


def display_week_tab(week_offset: int) -> None:
    """Display content for a single week tab
    
    Args:
        week_offset: Number of weeks from current week (0 = this week, 1 = next week, etc.)
    """
    # Get recipes for this specific week
    recipes = WeeklyRecipeManager.get_recipes_for_week(week_offset)
    
    # Try to get all available recipes to check if any exist
    try:
        from src.pages.browse_recipes.session_state import get_all_recipes
        all_available_recipes = get_all_recipes()
    except:
        all_available_recipes = []
    
    # Display content based on recipe availability
    if not all_available_recipes:
        st.error("No recipes available! Go to 'Browse Recipes' to add recipes to your collection.", icon=":material/no_sim:")
        return
    
    # Auto-populate with random recipes if week is empty
    if not recipes:
        # Try to populate the week automatically
        if WeeklyRecipeManager.populate_week_with_random_recipes(week_offset, force=True):
            recipes = WeeklyRecipeManager.get_recipes_for_week(week_offset)
            if recipes:
                st.success(f"🎲 Auto-populated with {len(recipes)} random recipes!", icon=":material/auto_awesome:")
    
    # Display recipes if we have them
    if recipes:
        display_recipes(recipes, week_offset)
        
        # Add action buttons
        col1, col2 = st.columns(2)
        with col1:
            handle_clear_action(week_offset)
        with col2:
            # Refresh button to regenerate random recipes
            meals_per_week = st.session_state.get('meals_per_week', 3)
            if st.button(f"🔄 Refresh ({meals_per_week} new recipes)", key=f"refresh_week_{week_offset}", type="secondary"):
                WeeklyRecipeManager.clear_week(week_offset)
                if WeeklyRecipeManager.populate_week_with_random_recipes(week_offset, force=True):
                    st.success("Refreshed with new random recipes!")
                    st.rerun()
    else:
        # Fallback if auto-population failed
        meals_per_week = st.session_state.get('meals_per_week', 3)
        st.warning("Could not auto-populate this week. Please try manually.", icon=":material/warning:")
        if st.button(f"🎲 Add {meals_per_week} Random Recipes", key=f"manual_populate_week_{week_offset}"):
            if WeeklyRecipeManager.populate_week_with_random_recipes(week_offset, force=True):
                st.success("Added random recipes!")
                st.rerun()


def main() -> None:
    """Main orchestrator function for the Weekly Meal Plans page"""
    # Initialize session state and ensure recipes are loaded
    WeeklyRecipeManager.initialize()
    
    # Initialize recipe data if not already done
    try:
        from src.pages.browse_recipes.session_state import initialize_session_state
        initialize_session_state()
    except Exception as e:
        st.error(f"Failed to initialize recipe data: {e}")
    
    # Initialize meals_per_week if not set
    if "meals_per_week" not in st.session_state:
        st.session_state.meals_per_week = 3
    
    # Display page header
    display_header()
    
    # Create tabs for 4 weeks
    tab_labels = []
    for i in range(4):
        tab_labels.append(get_relative_week_label(i))
    
    tabs = st.tabs(tab_labels)
    
    # Display each week tab
    for i, tab in enumerate(tabs):
        with tab:
            display_week_tab(i)


# Streamlit page entry point
if __name__ == "__page__":
    main()