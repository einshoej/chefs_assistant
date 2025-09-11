"""
Recipe viewer components for full-page recipe display
"""

import streamlit as st
import requests
from PIL import Image
import io
import numpy as np
from src.pages.view_recipe.session_state import add_to_weekly_recipes, get_recipe_scale_factor, set_recipe_scale_factor
from src.utils.recipe_scaling import get_scaling_options, format_scaled_quantity


@st.cache_data
def process_recipe_image_large(image_url, target_height=400):
    """
    Download and process recipe image for large display with center cropping
    Uses 16:9 aspect ratio for consistent appearance with robust retry logic
    
    Args:
        image_url: URL of the image to process
        target_height: Desired height in pixels (larger for full view)
    
    Returns:
        PIL Image object or None if processing fails
    """
    if not image_url:
        return None
    
    # Retry configuration
    max_retries = 3
    timeout = 15
    backoff_factor = 1.0
    
    for attempt in range(max_retries):
        try:
            # Calculate timeout with backoff
            current_timeout = timeout + (attempt * backoff_factor)
            
            # Download image with session for connection pooling
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            response = session.get(
                image_url, 
                timeout=current_timeout,
                stream=True  # Stream for large images
            )
            response.raise_for_status()
            
            # Open image with PIL
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary (handles RGBA, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate target dimensions (16:9 aspect ratio)
            target_width = int(target_height * 16 / 9)
            
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
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                continue
            print(f"Image download timeout after {max_retries} attempts: {image_url}")
            return None
            
        except requests.exceptions.ConnectionError as e:
            if "Failed to resolve" in str(e) or "getaddrinfo failed" in str(e):
                print(f"DNS resolution failed for image: {image_url}")
                return None
            elif attempt < max_retries - 1:
                continue
            print(f"Connection error after {max_retries} attempts: {str(e)}")
            return None
            
        except (requests.RequestException, Image.UnidentifiedImageError, Exception) as e:
            if attempt < max_retries - 1:
                continue
            print(f"Failed to process image after {max_retries} attempts: {str(e)}")
            return None
    
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
        
        # Add some spacing
        st.markdown("")
        
        # Recipe scaling section
        display_recipe_scaling(recipe)
        
        # Action button
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


def display_recipe_scaling(recipe):
    """Display recipe scaling slider and rating widget"""
    recipe_name = recipe.get('name', 'Unnamed Recipe')
    
    # Get scaling options
    options, default_idx, label = get_scaling_options(recipe)
    
    # Get current scale factor
    current_scale = get_recipe_scale_factor(recipe_name)
    
    # Find the current selection index
    current_idx = default_idx
    for i, (scale_factor, _) in enumerate(options):
        if abs(scale_factor - current_scale) < 0.01:
            current_idx = i
            break
    
    # Create columns for scaling and rating
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display the slider without label
        option_labels = [option[1] for option in options]
        current_label = options[current_idx][1]
        
        selected_label = st.select_slider(
            "Scaling",
            options=option_labels,
            value=current_label,
            key=f"scale_slider_{recipe_name}",
            label_visibility="collapsed"
        )
        
        # Find the selected index and scale factor
        selected_idx = option_labels.index(selected_label)
        new_scale_factor = options[selected_idx][0]
        
        # Update scale factor if changed
        if abs(new_scale_factor - current_scale) > 0.01:
            set_recipe_scale_factor(recipe_name, new_scale_factor)
            st.rerun()
    
    with col2:
        # Rating widget
        rating = st.feedback(
            "stars",
            key=f"rating_{recipe_name}"
        )


def is_ingredient_heading(ingredient):
    """
    Detect if an ingredient is a heading/section divider.
    Headings have empty quantity, note, and rawText fields, and name ending with double spaces.
    """
    if not isinstance(ingredient, dict):
        return False
    
    quantity = ingredient.get('quantity', '').strip()
    note = ingredient.get('note', '').strip()
    raw_text = ingredient.get('rawText', '').strip()
    name = ingredient.get('name', '')
    
    # Check if all fields are empty except name, and name ends with double spaces
    return not quantity and not note and not raw_text and name.endswith('  ')


def display_ingredients_section(recipe):
    """Display ingredients in a 3-column layout with headings properly formatted"""
    
    ingredients = recipe.get('ingredients', [])
    recipe_name = recipe.get('name', 'Unnamed Recipe')
    current_scale = get_recipe_scale_factor(recipe_name)
    
    # Always show the expander expanded
    with st.expander("Ingredients", expanded=True):
        if ingredients:
            # Convert ingredients to a consistent format
            if isinstance(ingredients, list):
                ingredients_list = ingredients
            else:
                # Old dict format
                ingredients_list = [{'name': k, 'quantity': v} for k, v in ingredients.items()]
            
            # Display each ingredient
            for ingredient in ingredients_list:
                display_ingredient_row(ingredient, current_scale)
        else:
            st.info("📋 No ingredients list available for this recipe.")


def display_ingredient_row(ingredient, scale_factor=1.0):
    """Display a single ingredient in a 3-column row format"""
    if isinstance(ingredient, dict):
        quantity = ingredient.get('quantity', '').strip()
        name = ingredient.get('name', ingredient.get('rawText', '')).strip()
        note = ingredient.get('note', '').strip()
        
        # Check if this is a heading
        if is_ingredient_heading(ingredient):
            # Display heading with emphasis and no quantity/note
            heading_name = name.rstrip()  # Remove trailing spaces
            st.subheader(heading_name)
        else:
            # Scale the quantity if we have one
            if quantity and scale_factor != 1.0:
                scaled_quantity = format_scaled_quantity(quantity, scale_factor)
            else:
                scaled_quantity = quantity
            
            # Display regular ingredient in 3 columns
            col1, col2, col3 = st.columns([1, 2, 2])
            with col1:
                st.markdown(scaled_quantity if scaled_quantity else "")
            with col2:
                st.markdown(name if name else "")
            with col3:
                st.markdown(note if note else "")
    else:
        # Plain string format - treat as ingredient name
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.markdown("")
        with col2:
            st.markdown(f"{ingredient}")
        with col3:
            st.markdown("")


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
    with st.container(border=False):
        st.subheader(f"Step {step_num}")
        st.markdown(step_desc)


def display_recipe_details(recipe):
    """Display additional recipe details if available"""
    
    # Collect additional details
    details = {}
    
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