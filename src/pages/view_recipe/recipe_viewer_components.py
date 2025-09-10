"""
Recipe viewer components for full-page recipe display
"""

import streamlit as st
import requests
from PIL import Image
import io
import numpy as np
from src.pages.view_recipe.session_state import add_to_weekly_recipes


@st.cache_data
def process_recipe_image_large(image_url, target_height=400):
    """
    Download and process recipe image for large display with center cropping
    Uses 16:9 aspect ratio for consistent appearance
    
    Args:
        image_url: URL of the image to process
        target_height: Desired height in pixels (larger for full view)
    
    Returns:
        PIL Image object or None if processing fails
    """
    if not image_url:
        return None
        
    try:
        # Download image
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Open image with PIL
        img = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary (handles RGBA, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate target dimensions (16:9 aspect ratio)
        target_width = int(target_height * 16 / 9)  # 16:9 aspect ratio
        
        # Get original dimensions
        original_width, original_height = img.size
        original_aspect = original_width / original_height
        target_aspect = target_width / target_height
        
        # Determine how to crop to target aspect ratio
        if original_aspect > target_aspect:
            # Image is wider than target - crop width
            new_height = original_height
            new_width = int(new_height * target_aspect)
            left = (original_width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = original_height
        else:
            # Image is taller than target - crop height
            new_width = original_width
            new_height = int(new_width / target_aspect)
            left = 0
            top = (original_height - new_height) // 2
            right = original_width
            bottom = top + new_height
        
        # Crop image to target aspect ratio
        img = img.crop((left, top, right, bottom))
        
        # Resize to final dimensions
        processed_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        return np.array(processed_img)
        
    except (requests.RequestException, Image.UnidentifiedImageError, Exception) as e:
        print(f"Failed to process image: {str(e)}")
        return None


def display_recipe_hero(recipe):
    """Display the recipe hero section with large image, title and badges"""
    
    # Get recipe data
    image_url = recipe.get('image') or recipe.get('picture')
    photo_data = recipe.get('photo', {})
    
    if not image_url and photo_data.get('hasPhoto'):
        image_url = photo_data.get('url')
    
    # Hero container
    with st.container(border=True):
        # Large image section
        if image_url:
            processed_image = process_recipe_image_large(image_url, target_height=400)
            if processed_image is not None:
                st.image(processed_image, width="stretch")
            else:
                # Elegant placeholder for failed image
                st.markdown(
                    """
                    <div style='
                        height: 400px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 0.5rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 1.5rem;
                        margin-bottom: 1rem;
                    '>
                        🖼️ Image could not be loaded
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            # Elegant placeholder for no image
            st.markdown(
                """
                <div style='
                    height: 400px; 
                    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    border-radius: 0.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #666;
                    font-size: 1.5rem;
                    margin-bottom: 1rem;
                '>
                    🍽️ No image available
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Recipe title
        recipe_name = recipe.get('name', 'Unnamed Recipe')
        st.title(recipe_name)
        
        # Badges section
        display_recipe_badges(recipe)
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button(
                "Add to This Week",
                type="primary",
                width="stretch",
                icon=":material/add:",
                help="Add this recipe to your weekly plan"
            ):
                if add_to_weekly_recipes(recipe):
                    st.success("Added to weekly recipes!")
                else:
                    st.info("Already in weekly recipes")
                st.rerun()
        
        with col2:
            if st.button(
                "Print Recipe",
                type="secondary",
                width="stretch",
                icon=":material/print:",
                help="Print-friendly view (opens new window)"
            ):
                st.info("Print functionality coming soon!")


def display_recipe_badges(recipe):
    """Display recipe badges with enhanced styling"""
    
    # Calculate total time
    total_time = recipe.get('total_time', 0) or 0
    prep_time = recipe.get('prep_time', 0) or 0
    cook_time = recipe.get('cook_time', 0) or 0
    
    # Use total_time if available, otherwise calculate from prep + cook time
    if total_time > 0:
        total_minutes = total_time // 60
    else:
        total_minutes = (prep_time + cook_time) // 60 if (prep_time + cook_time) > 0 else 0
    
    # Get categories from collections
    collections = recipe.get('collections', [])
    collection_names = [c['name'] if isinstance(c, dict) else c for c in collections]
    
    # Build rating
    rating = recipe.get('rating', 0)
    
    # Create badge columns
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        # Time badge
        if total_minutes > 0:
            st.markdown(f":blue-badge[🕐 {total_minutes} min]")
        else:
            st.markdown(f":gray-badge[🕐 Time not set]")
    
    with col2:
        # Rating badge
        if rating > 0:
            stars = ":material/chef_hat:" * rating
            st.markdown(f":orange-badge[{stars}]")
        else:
            st.markdown(":gray-badge[:material/chef_hat: Not rated]")
    
    with col3:
        # Category badge (first one if multiple)
        if collection_names:
            category = collection_names[0]  # Show first category
            extra_text = f" +{len(collection_names)-1}" if len(collection_names) > 1 else ""
            st.markdown(f":green-badge[🏷️ {category}{extra_text}]")
        else:
            st.markdown(":gray-badge[🏷️ Uncategorized]")
    
    with col4:
        # Source badge
        source = recipe.get('source', '').strip()
        if source:
            st.markdown(f":violet-badge[📚 {source}]")
        else:
            st.markdown(":gray-badge[📚 No source]")


def display_ingredients_section(recipe):
    """Display ingredients in an expanded expander with enhanced layout"""
    
    ingredients = recipe.get('ingredients', [])
    
    # Always show the expander expanded
    with st.expander("Ingredients", expanded=True):
        if ingredients:
            # Convert ingredients to a consistent format
            if isinstance(ingredients, list):
                ingredients_list = ingredients
            else:
                # Old dict format
                ingredients_list = [{'name': k, 'quantity': v} for k, v in ingredients.items()]
            
            # Display ingredients in two columns if there are many, otherwise single column
            if len(ingredients_list) <= 6:
                # Single column for short lists
                for ing in ingredients_list:
                    display_ingredient_large(ing)
            else:
                # Two columns for longer lists
                cols_ing = st.columns(2)
                half = len(ingredients_list) // 2 + len(ingredients_list) % 2
                
                with cols_ing[0]:
                    for ing in ingredients_list[:half]:
                        display_ingredient_large(ing)
                
                with cols_ing[1]:
                    for ing in ingredients_list[half:]:
                        display_ingredient_large(ing)
        else:
            st.info("📋 No ingredients list available for this recipe.")


def display_ingredient_large(ingredient):
    """Display a single ingredient with enhanced formatting"""
    if isinstance(ingredient, dict):
        # New format from official API
        quantity = ingredient.get('quantity', '')
        name = ingredient.get('name', ingredient.get('rawText', ''))
        if quantity:
            st.markdown(f"**•** {quantity} {name}")
        else:
            st.markdown(f"**•** {name}")
    else:
        # Plain string format
        st.markdown(f"**•** {ingredient}")


def display_instructions_section(recipe):
    """Display preparation steps in an expanded expander with enhanced layout"""
    
    prep_steps = recipe.get('preparation_steps', [])
    
    # Always show the expander expanded
    with st.expander("Instructions", expanded=True):
        if prep_steps:
            if isinstance(prep_steps, list):
                # New format: list of strings
                for step_num, step_desc in enumerate(prep_steps, 1):
                    display_instruction_step(step_num, step_desc)
            else:
                # Old format: dictionary
                for step_num, step_desc in sorted(prep_steps.items()):
                    display_instruction_step(step_num, step_desc)
        else:
            st.info("📋 No preparation steps available for this recipe.")


def display_instruction_step(step_num, step_desc):
    """Display a single instruction step with enhanced formatting"""
    with st.container(border=True):
        st.markdown(f"**Step {step_num}**")
        st.markdown(step_desc)


def display_recipe_details(recipe):
    """Display additional recipe details if available"""
    
    # Collect additional details
    details = {}
    
    # Servings
    servings = recipe.get('servings') or recipe.get('yields')
    if servings:
        details['Servings'] = servings
    
    # Difficulty
    difficulty = recipe.get('difficulty')
    if difficulty:
        details['Difficulty'] = difficulty
    
    # Cuisine
    cuisine = recipe.get('cuisine')
    if cuisine:
        details['Cuisine'] = cuisine
    
    # Notes or description
    notes = recipe.get('notes') or recipe.get('description')
    if notes:
        details['Notes'] = notes
    
    # URL
    url = recipe.get('url')
    if url:
        details['Recipe URL'] = f"[View Original]({url})"
    
    # Display details if we have any
    if details:
        with st.expander("📋 Recipe Details"):
            for key, value in details.items():
                if key == 'Recipe URL':
                    st.markdown(f"**{key}:** {value}")
                else:
                    st.markdown(f"**{key}:** {value}")


def display_recipe_selector(recipes, current_selection):
    """Display recipe selector with search functionality"""
    if not recipes:
        st.error("No recipes available")
        return None
    
    recipe_names = [recipe.get('name', f'Recipe {idx}') for idx, recipe in enumerate(recipes)]
    
    # Find current index
    current_idx = 0
    if current_selection:
        current_name = current_selection.get('name', '')
        if current_name in recipe_names:
            current_idx = recipe_names.index(current_name)
    
    # Recipe selector
    selected_name = st.selectbox(
        "Choose a recipe to view:",
        options=recipe_names,
        index=current_idx,
        key="recipe_selector",
        help="Select any recipe to view it in full detail"
    )
    
    # Find and return selected recipe
    for recipe in recipes:
        if recipe.get('name') == selected_name:
            return recipe
    
    return recipes[0] if recipes else None