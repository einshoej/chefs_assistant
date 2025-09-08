"""
Browse Recipes page - Search and filter recipes from the database
"""

import streamlit as st
from src.pages.browse_recipes.session_state import initialize_session_state, get_all_recipes
from src.pages.browse_recipes.recipe_display import display_recipe_card
from src.pages.browse_recipes.recipe_filters import filter_recipes


def get_all_categories(recipes):
    """Extract all unique categories from recipes (collections only)"""
    categories = set()
    
    for recipe in recipes:
        # Get from collections - handle both old format (strings) and new format (objects)
        collections = recipe.get('collections', [])
        for collection in collections:
            if isinstance(collection, dict):
                categories.add(collection['name'])
            else:
                categories.add(collection)
    
    # Return sorted list, excluding empty strings
    return sorted([cat for cat in categories if cat.strip()])


def view_all_recipes():
    """Display all recipes with search and filter options"""
    st.header("📖 View All Recipes")
    
    # Force session state initialization every time
    initialize_session_state()
    
    # Initialize pagination state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    
    st.divider()
    
    # Search and filter section
    st.subheader("Find Recipes")
    
    # Check if we have recipes
    has_any_recipes = 'local_recipes' in st.session_state and st.session_state.local_recipes
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search recipes", 
            placeholder="Enter recipe name or ingredient...", 
            key="search",
            help="Search through your recipes" if has_any_recipes else "Add local recipes to enable search",
            on_change=lambda: setattr(st.session_state, 'current_page', 0)  # Reset to first page on search
        )
    
    with col2:
        # Get all recipes to extract categories
        all_recipes = get_all_recipes() if has_any_recipes else []
        available_categories = get_all_categories(all_recipes)
        
        selected_categories = st.multiselect(
            "Categories", 
            options=available_categories,
            default=[],
            key="categories",
            help="Select categories to filter by (no selection shows all)" if has_any_recipes else "Add recipes to enable filters",
            on_change=lambda: setattr(st.session_state, 'current_page', 0)  # Reset to first page on filter change
        )
    
    with col3:
        source_filter = st.selectbox(
            "Source", 
            ["All", "Local", "Default"], 
            key="source",
            help="Filter by recipe source",
            on_change=lambda: setattr(st.session_state, 'current_page', 0)  # Reset to first page on filter change
        )
    
    st.divider()
    
    # Available recipes section
    st.subheader("Recipe Library")
    
    
    # Display recipes
    display_recipes(search_term if has_any_recipes else "", selected_categories, source_filter)


def display_recipes(search_term: str = "", categories: list = None, source: str = "All"):
    """Display filtered recipes with pagination"""
    
    # Get all available recipes
    all_recipes = get_all_recipes()
    
    if not all_recipes:
        st.info("📚 No recipes available. Add local recipes to get started.")
        return
    
    # Filter recipes
    categories = categories or []
    filtered_recipes = filter_recipes(all_recipes, search_term, categories, source)
    
    if not filtered_recipes:
        st.warning("No recipes found matching your filters.")
        return
    
    # Pagination settings
    recipes_per_page = 10
    total_recipes = len(filtered_recipes)
    total_pages = (total_recipes - 1) // recipes_per_page + 1
    
    # Ensure current page is within bounds
    if st.session_state.current_page >= total_pages:
        st.session_state.current_page = total_pages - 1
    if st.session_state.current_page < 0:
        st.session_state.current_page = 0
    
    # Calculate slice for current page
    start_idx = st.session_state.current_page * recipes_per_page
    end_idx = min(start_idx + recipes_per_page, total_recipes)
    
    # Get recipes for current page
    page_recipes = filtered_recipes[start_idx:end_idx]
    
    # Display page info and navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_page > 0:
            if st.button("⬅️ Previous 10", width='stretch'):
                st.session_state.current_page -= 1
                st.rerun()
        else:
            # Empty space when button is disabled
            st.empty()
    
    with col2:
        # Display current page info
        showing_start = start_idx + 1
        showing_end = end_idx
        st.markdown(
            f"<div style='text-align: center; padding: 0.5rem;'>"
            f"Showing <b>{showing_start}-{showing_end}</b> of <b>{total_recipes}</b> recipes "
            f"(Page {st.session_state.current_page + 1} of {total_pages})"
            f"</div>",
            unsafe_allow_html=True
        )
    
    with col3:
        if st.session_state.current_page < total_pages - 1:
            if st.button("Next 10 ➡️", width='stretch'):
                st.session_state.current_page += 1
                st.rerun()
        else:
            # Empty space when button is disabled
            st.empty()
    
    st.divider()
    
    # Display recipes in two-column grid
    if page_recipes:
        # Create two columns for recipe grid
        col1, col2 = st.columns(2, gap="medium")
        
        for idx, recipe in enumerate(page_recipes):
            # Use global index for unique keys
            global_idx = start_idx + idx
            
            # Alternate between columns
            if idx % 2 == 0:
                with col1:
                    display_recipe_card(recipe, global_idx)
            else:
                with col2:
                    display_recipe_card(recipe, global_idx)


if __name__ == "__page__":
    view_all_recipes()