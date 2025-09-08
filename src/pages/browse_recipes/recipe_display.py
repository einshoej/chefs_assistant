"""
Recipe display components for browse recipes page
"""

import streamlit as st
import requests
from PIL import Image
import io
from src.pages.browse_recipes.session_state import add_to_weekly_recipes


@st.cache_data
def process_recipe_image(image_url, target_height=200):
    """
    Download and process recipe image to fixed dimensions with center cropping
    Uses 16:9 aspect ratio for consistent appearance
    
    Args:
        image_url: URL of the image to process
        target_height: Desired height in pixels
    
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
        
        return processed_img
        
    except (requests.RequestException, Image.UnidentifiedImageError, Exception) as e:
        st.error(f"Failed to process image: {str(e)}")
        return None


def display_recipe_card(recipe, idx):
    """Display a compact recipe card using Streamlit native components with uniform height"""
    
    # Get recipe data
    image_url = recipe.get('image')
    photo_data = recipe.get('photo', {})
    
    if not image_url and photo_data.get('hasPhoto'):
        image_url = photo_data.get('url')
    
    # Calculate total time
    prep_time = recipe.get('prep_time', 0) or 0
    cook_time = recipe.get('cook_time', 0) or 0
    total_minutes = (prep_time + cook_time) // 60 if (prep_time + cook_time) > 0 else 0
    
    # Get categories
    collections = recipe.get('collections', [])
    collection_names = [c['name'] if isinstance(c, dict) else c for c in collections]
    tags = recipe.get('tags', [])
    all_tags = collection_names + tags
    
    # Build rating stars
    rating = recipe.get('rating', 0)
    if rating > 0:
        stars = ':material/chef_hat:' * rating
    else:
        stars = None
    
    # Recipe name (truncate if too long)
    recipe_name = recipe.get('name', 'Unnamed Recipe')
    if len(recipe_name) > 50:
        recipe_name = recipe_name[:47] + "..."
    
    # Main container with border
    with st.container(border=True, height="content"):
        # Image section with preprocessing for fixed height
        if image_url:
            processed_image = process_recipe_image(image_url, target_height=200)
            if processed_image:
                st.image(processed_image, use_container_width=True)
            else:
                st.markdown("🖼️ *Image could not be loaded*")
                st.markdown("")  # Add some vertical space
        else:
            # Create placeholder space for no image
            st.markdown("🖼️ *No image available*")
            st.markdown("")  # Add some vertical space
    
        
        # Build badges in markdown format
        badges_markdown = ""
        
        # Add time badge
        if total_minutes > 0:
            badges_markdown += f":blue-badge[🕐 {total_minutes} min] "
        
        # Add category badge
        for tag in all_tags:
            badges_markdown += f":gray-badge[🏷️ {tag}] "
        
        # Display badges
        if badges_markdown:
            st.markdown(badges_markdown)
        

        # Recipe title
        st.markdown(f"### {recipe_name}")
        
        # Rating
        if stars:
            st.markdown(stars)
        else:
            st.badge("Not rated",color="gray",icon=":material/chef_hat:")
        
        # Add recipe details expander
        display_recipe_details(recipe, idx)
        
        # Add to this week's recipes button
        if st.button(
            "Add to This Week",
            key=f"add_recipe_{idx}",
            use_container_width=True,
            help="Add to This Week",
            type="primary",
            icon=":material/add:"
        ):
            add_to_weekly_recipes(recipe)
            st.success("Added!")
            st.rerun()


def display_recipe_details(recipe, idx):
    """Display full recipe details in an expander"""
    prep_steps = recipe.get('preparation_steps', [])
    ingredients = recipe.get('ingredients', [])
    
    # Always show the expander, even if no detailed data is available
    with st.expander("View Full Recipe Details"):
        # Full ingredients list
        if ingredients:
            st.markdown("### Ingredients")
            cols_ing = st.columns(2)
            
            # Convert ingredients to a consistent format
            if isinstance(ingredients, list):
                ingredients_list = ingredients
            else:
                # Old dict format
                ingredients_list = [{'name': k, 'quantity': v} for k, v in ingredients.items()]
            
            half = len(ingredients_list) // 2 + len(ingredients_list) % 2
            
            with cols_ing[0]:
                for ing in ingredients_list[:half]:
                    display_ingredient(ing)
            
            with cols_ing[1]:
                for ing in ingredients_list[half:]:
                    display_ingredient(ing)
        
        # Preparation steps
        if prep_steps:
            st.markdown("### Instructions")
            if isinstance(prep_steps, list):
                # New format: list of strings
                for step_num, step_desc in enumerate(prep_steps, 1):
                    st.write(f"**Step {step_num}:** {step_desc}")
            else:
                # Old format: dictionary
                for step_num, step_desc in sorted(prep_steps.items()):
                    st.write(f"**Step {step_num}:** {step_desc}")
        
        # Show message if no detailed data is available
        if not prep_steps and not ingredients:
            st.info("📋 No detailed recipe information available. This recipe may need additional details added.")


def display_ingredient(ingredient):
    """Display a single ingredient in the appropriate format"""
    if isinstance(ingredient, dict):
        # New format from official API
        quantity = ingredient.get('quantity', '')
        name = ingredient.get('name', ingredient.get('rawText', ''))
        if quantity:
            st.write(f"• {quantity} {name}")
        else:
            st.write(f"• {name}")
    else:
        # Plain string format
        st.write(f"• {ingredient}")
