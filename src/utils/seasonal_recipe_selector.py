"""
Seasonal recipe selection utility for weighted random recipe selection based on current season.
"""

import random
from typing import List, Dict, Any, Tuple
from datetime import date
from .seasons import get_current_season, Season


class SeasonalRecipeSelector:
    """
    Handles seasonal weighting for recipe selection based on current season.
    
    Weight distribution:
    - Current season: 50%
    - Adjacent seasons: 20% each
    - Opposite season: 10%
    """
    
    # Define seasonal adjacency (previous -> current -> next)
    SEASONAL_ADJACENCY = {
        "Vinter": {"previous": "Høst", "next": "Vår", "opposite": "Sommer"},
        "Vår": {"previous": "Vinter", "next": "Sommer", "opposite": "Høst"}, 
        "Sommer": {"previous": "Vår", "next": "Høst", "opposite": "Vinter"},
        "Høst": {"previous": "Sommer", "next": "Vinter", "opposite": "Vår"}
    }
    
    @classmethod
    def get_seasonal_weights(cls, current_season: Season) -> Dict[str, float]:
        """
        Get seasonal weights based on current season.
        
        Args:
            current_season: Current season name
            
        Returns:
            Dictionary mapping season names to their selection weights
        """
        adjacency = cls.SEASONAL_ADJACENCY[current_season]
        
        weights = {
            current_season: 0.50,
            adjacency["previous"]: 0.20,
            adjacency["next"]: 0.20,
            adjacency["opposite"]: 0.10
        }
        
        return weights
    
    @classmethod
    def categorize_recipes_by_season(cls, recipes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize recipes by their seasonal tags.
        
        Args:
            recipes: List of recipe dictionaries
            
        Returns:
            Dictionary mapping season names to lists of recipes, plus 'untagged' for recipes without seasonal tags
        """
        categorized = {
            "Vinter": [],
            "Vår": [],
            "Sommer": [], 
            "Høst": [],
            "untagged": []
        }
        
        for recipe in recipes:
            # Get collections and extract season names
            collections = recipe.get('collections', [])
            recipe_seasons = set()
            
            for collection in collections:
                collection_name = collection['name'] if isinstance(collection, dict) else collection
                if collection_name in ["Vinter", "Vår", "Sommer", "Høst"]:
                    recipe_seasons.add(collection_name)
            
            # Add recipe to appropriate seasonal categories
            if recipe_seasons:
                for season in recipe_seasons:
                    categorized[season].append(recipe)
            else:
                categorized["untagged"].append(recipe)
        
        return categorized
    
    @classmethod
    def select_recipes_with_seasonal_weights(
        cls, 
        recipes: List[Dict[str, Any]], 
        num_recipes: int,
        current_season: Season = None,
        used_recipe_names: set = None
    ) -> List[Dict[str, Any]]:
        """
        Select recipes using seasonal weighting based on current season.
        
        Args:
            recipes: Available recipes to select from
            num_recipes: Number of recipes to select
            current_season: Current season (if None, will be determined automatically)
            used_recipe_names: Set of recipe names to avoid (for duplicate prevention)
            
        Returns:
            List of selected recipe dictionaries
        """
        if not recipes:
            return []
        
        if num_recipes <= 0:
            return []
        
        if current_season is None:
            current_season = get_current_season()
        
        # Categorize recipes by season
        categorized_recipes = cls.categorize_recipes_by_season(recipes)
        
        # Get seasonal weights
        seasonal_weights = cls.get_seasonal_weights(current_season)
        
        # Apply duplicate avoidance if provided
        if used_recipe_names:
            for season in categorized_recipes:
                categorized_recipes[season] = [
                    r for r in categorized_recipes[season] 
                    if r.get('name', '') not in used_recipe_names
                ]
        
        # Build weighted recipe pool
        weighted_pool = []
        
        for season, weight in seasonal_weights.items():
            season_recipes = categorized_recipes.get(season, [])
            if season_recipes:
                # Add each recipe multiple times based on weight (scaled to integers)
                weight_factor = int(weight * 100)  # Convert 0.5 -> 50, 0.2 -> 20, etc.
                for recipe in season_recipes:
                    weighted_pool.extend([recipe] * weight_factor)
        
        # Add untagged recipes with a base weight
        untagged_recipes = categorized_recipes.get("untagged", [])
        if untagged_recipes:
            # Give untagged recipes a lower weight than seasonal recipes
            base_weight = int(10)  # 10% weight (lower than seasonal weights to prioritize seasonal)
            for recipe in untagged_recipes:
                weighted_pool.extend([recipe] * base_weight)
        
        # If weighted pool is empty, fall back to original recipes
        if not weighted_pool:
            available_recipes = recipes
            if used_recipe_names:
                available_recipes = [r for r in recipes if r.get('name', '') not in used_recipe_names]
            
            if not available_recipes:
                return []
            
            return random.sample(available_recipes, min(num_recipes, len(available_recipes)))
        
        # Select from weighted pool, avoiding duplicates
        selected = []
        selected_names = set()
        max_attempts = len(weighted_pool) * 2  # Prevent infinite loops
        attempts = 0
        
        while len(selected) < num_recipes and attempts < max_attempts:
            attempts += 1
            
            if not weighted_pool:
                break
                
            recipe = random.choice(weighted_pool)
            recipe_name = recipe.get('name', '')
            
            # Avoid duplicates in selection
            if recipe_name not in selected_names:
                selected.append(recipe)
                selected_names.add(recipe_name)
                
                # Remove all instances of this recipe from weighted pool to avoid duplicates
                weighted_pool = [r for r in weighted_pool if r.get('name', '') != recipe_name]
        
        return selected
    
    @classmethod
    def get_seasonal_distribution_info(cls, recipes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get information about seasonal distribution of recipes.
        
        Args:
            recipes: List of recipe dictionaries
            
        Returns:
            Dictionary with distribution information
        """
        categorized = cls.categorize_recipes_by_season(recipes)
        
        total_recipes = len(recipes)
        seasonal_counts = {season: len(recipe_list) for season, recipe_list in categorized.items()}
        
        # Calculate percentages
        seasonal_percentages = {}
        for season, count in seasonal_counts.items():
            percentage = (count / total_recipes * 100) if total_recipes > 0 else 0
            seasonal_percentages[season] = round(percentage, 1)
        
        current_season = get_current_season()
        current_weights = cls.get_seasonal_weights(current_season)
        
        return {
            "total_recipes": total_recipes,
            "seasonal_counts": seasonal_counts,
            "seasonal_percentages": seasonal_percentages,
            "current_season": current_season,
            "current_weights": current_weights
        }


# Convenience function for external use
def select_seasonal_recipes(
    recipes: List[Dict[str, Any]], 
    num_recipes: int,
    used_recipe_names: set = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to select recipes with seasonal weighting.
    
    Args:
        recipes: Available recipes to select from
        num_recipes: Number of recipes to select
        used_recipe_names: Set of recipe names to avoid
        
    Returns:
        List of selected recipe dictionaries
    """
    return SeasonalRecipeSelector.select_recipes_with_seasonal_weights(
        recipes, num_recipes, used_recipe_names=used_recipe_names
    )