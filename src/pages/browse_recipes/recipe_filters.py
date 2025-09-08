"""
Recipe filtering functionality for browse recipes page
"""


def filter_recipes(recipes, search_term, categories, sources):
    """Filter recipes based on search criteria"""
    filtered = recipes
    
    # Filter by search term
    if search_term:
        search_lower = search_term.lower()
        search_filtered = []
        for r in filtered:
            # Check recipe name
            if search_lower in r.get('name', '').lower():
                search_filtered.append(r)
                continue
            
            # Check ingredients (handle both list and dict formats)
            ingredients = r.get('ingredients', {})
            if isinstance(ingredients, dict):
                # New format: {ingredient: quantity}
                if any(search_lower in ing.lower() for ing in ingredients.keys()):
                    search_filtered.append(r)
                    continue
            elif isinstance(ingredients, list):
                # Old format: [ingredient1, ingredient2, ...]
                if any(search_lower in str(ing).lower() for ing in ingredients):
                    search_filtered.append(r)
                    continue
            
            # Check collections for search terms
            collections = r.get('collections', [])
            collection_names = [c['name'] if isinstance(c, dict) else c for c in collections]
            if any(search_lower in coll.lower() for coll in collection_names):
                search_filtered.append(r)
                continue
        filtered = search_filtered
    
    # Filter by categories (only apply filter if categories are selected)
    if categories:
        def matches_categories(r):
            # Get all category names from recipe in lowercase for comparison
            recipe_categories = set()
            
            # Add from collections - handle both old format (strings) and new format (objects)
            collections = r.get('collections', [])
            collection_names = [c['name'] if isinstance(c, dict) else c for c in collections]
            recipe_categories.update(c.lower() for c in collection_names)
            
            # Check if ANY selected category matches recipe categories (OR logic)
            selected_lower = set(cat.lower() for cat in categories)
            return bool(selected_lower.intersection(recipe_categories))
        
        filtered = [r for r in filtered if matches_categories(r)]
    
    # Filter by sources (only apply filter if sources are selected)
    if sources:
        def matches_sources(r):
            recipe_source = r.get('source', '').strip()
            # Check if recipe source matches any of the selected sources
            return recipe_source in sources
        
        filtered = [r for r in filtered if matches_sources(r)]
    
    # Sort by rating (descending - highest first, unrated last)
    filtered = sorted(filtered, key=lambda r: r.get('rating', 0), reverse=True)
    
    return filtered
