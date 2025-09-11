"""
Recipe scaling utilities for ingredient quantity parsing and scaling
"""

import re
from fractions import Fraction
from typing import Optional, Tuple


def parse_quantity(quantity_str: str) -> Optional[float]:
    """
    Parse ingredient quantity string into a float value.
    Handles various formats: "2", "1/2", "1.5", "1-2", "2 ss", etc.
    
    Args:
        quantity_str: The quantity string from the ingredient
        
    Returns:
        Float value of the quantity, or None if unparseable
    """
    if not quantity_str or not quantity_str.strip():
        return None
    
    # Clean the string - remove extra whitespace
    quantity_str = quantity_str.strip()
    
    # Handle range notation (e.g., "1-2", "2-3") - use the lower bound
    if '-' in quantity_str:
        parts = quantity_str.split('-')
        if len(parts) == 2:
            try:
                return float(parts[0].strip())
            except ValueError:
                pass
    
    # Extract numeric part before any units (e.g., "2 ss" -> "2")
    numeric_part = re.match(r'^([0-9\/.,]+)', quantity_str)
    if numeric_part:
        numeric_str = numeric_part.group(1).replace(',', '.')  # Handle European decimal notation
        
        # Handle fractions (e.g., "1/2", "3/4")
        if '/' in numeric_str:
            try:
                return float(Fraction(numeric_str))
            except (ValueError, ZeroDivisionError):
                pass
        
        # Handle regular decimals
        try:
            return float(numeric_str)
        except ValueError:
            pass
    
    return None


def extract_unit(quantity_str: str) -> str:
    """
    Extract the unit part from a quantity string.
    
    Args:
        quantity_str: The quantity string from the ingredient
        
    Returns:
        The unit part (everything after the number)
    """
    if not quantity_str or not quantity_str.strip():
        return ""
    
    # Extract everything after the numeric part
    unit_part = re.sub(r'^[0-9\/.,\-\s]+', '', quantity_str.strip())
    return unit_part.strip()


def format_scaled_quantity(original_quantity: str, scale_factor: float) -> str:
    """
    Scale an ingredient quantity and format it nicely.
    
    Args:
        original_quantity: The original quantity string
        scale_factor: The scaling factor to apply
        
    Returns:
        Formatted scaled quantity string
    """
    parsed_qty = parse_quantity(original_quantity)
    
    if parsed_qty is None:
        # If we can't parse it, return original
        return original_quantity
    
    if parsed_qty == 0:
        # If quantity is 0, return original
        return original_quantity
    
    # Scale the quantity
    scaled_qty = parsed_qty * scale_factor
    
    # Get the unit part
    unit = extract_unit(original_quantity)
    
    # Format the scaled quantity nicely
    formatted_qty = format_number(scaled_qty)
    
    # Combine with unit
    if unit:
        return f"{formatted_qty} {unit}"
    else:
        return formatted_qty


def format_number(value: float) -> str:
    """
    Format a number nicely, converting to fractions for common values.
    
    Args:
        value: The numeric value to format
        
    Returns:
        Nicely formatted string representation
    """
    # Handle very small values
    if value < 0.01:
        return "0"
    
    # Check if it's close to a simple fraction
    common_fractions = {
        0.125: "1/8",
        0.25: "1/4", 
        0.333: "1/3",
        0.5: "1/2",
        0.667: "2/3",
        0.75: "3/4"
    }
    
    for frac_val, frac_str in common_fractions.items():
        if abs(value - frac_val) < 0.01:
            return frac_str
    
    # For values close to whole numbers, show as integers
    if abs(value - round(value)) < 0.01:
        return str(int(round(value)))
    
    # For other values, show with one decimal place
    return f"{value:.1f}".rstrip('0').rstrip('.')


def get_scaling_options(recipe: dict) -> Tuple[list, int, str]:
    """
    Get scaling options for a recipe based on whether it has servings.
    
    Args:
        recipe: Recipe dictionary
        
    Returns:
        Tuple of (options_list, default_index, label_format)
        - options_list: List of (scale_factor, display_label) tuples
        - default_index: Index of the default/original option
        - label_format: Format string for the selector label
    """
    servings = recipe.get('servings')
    
    # Try to parse servings as a number
    original_servings = None
    if servings:
        try:
            original_servings = int(str(servings).strip())
        except (ValueError, TypeError):
            pass
    
    if original_servings and original_servings > 0:
        # Recipe has servings - scale from 1 to 12 servings
        options = []
        default_idx = 0
        
        for target_servings in range(1, 13):
            scale_factor = target_servings / original_servings
            label = f"{target_servings} servings"
            if target_servings == original_servings:
                label += " (original)"
                default_idx = len(options)
            options.append((scale_factor, label))
        
        return options, default_idx, "Scale to:"
    
    else:
        # Recipe doesn't have servings - scale from 1/4x to 12x
        scale_factors = [0.25, 0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 10, 12]
        options = []
        default_idx = 3  # 1x is at index 3
        
        for scale_factor in scale_factors:
            if scale_factor == 1:
                label = "1x (original)"
            elif scale_factor < 1:
                label = f"{format_number(scale_factor)}x"
            else:
                label = f"{int(scale_factor)}x"
            options.append((scale_factor, label))
        
        return options, default_idx, "Scale recipe:"