"""
Recipe filtering functionality for browse recipes page
"""


def filter_recipes(recipes, search_term, categories, source):
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
            
            # Check tags
            if any(search_lower in tag.lower() for tag in r.get('tags', [])):
                search_filtered.append(r)
                continue
            
            # Check collections - handle both old format (strings) and new format (objects)
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
            
            # Add from tags
            recipe_categories.update(t.lower() for t in r.get('tags', []))
            
            # Add from collections - handle both old format (strings) and new format (objects)
            collections = r.get('collections', [])
            collection_names = [c['name'] if isinstance(c, dict) else c for c in collections]
            recipe_categories.update(c.lower() for c in collection_names)
            
            # Add from category field
            category_field = r.get('category', '')
            if category_field:
                recipe_categories.add(category_field.lower())
            
            # Check if ALL selected categories match recipe categories (AND logic)
            selected_lower = set(cat.lower() for cat in categories)
            return selected_lower.issubset(recipe_categories)
        
        filtered = [r for r in filtered if matches_categories(r)]
    
    # Filter by source
    if source != "All":
        filtered = [r for r in filtered if r.get('source', 'Local') == source]
    
    # Sort by rating (descending - highest first, unrated last)
    filtered = sorted(filtered, key=lambda r: r.get('rating', 0), reverse=True)
    
    return filtered
