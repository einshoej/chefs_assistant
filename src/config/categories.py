"""
Recipe category configuration with groupings
"""

# Category groups with their categories, display order, and styling
CATEGORY_GROUPS = {
    "meal_types": {
        "name": "Meal Types",
        "name_no": "Måltidstyper", 
        "icon": "🍽️",
        "color": "blue",
        "categories": [
            "Frokost",
            "Brunsj", 
            "Lunsj",
            "Middag",
            "Matpakke",
            "Helgemiddag",
            "Dessert",
            "Søtsaker",
            "Bakverk"
        ]
    },
    
    "cuisines": {
        "name": "Cuisines",
        "name_no": "Kjøkken",
        "icon": "🌍",
        "color": "green", 
        "categories": [
            "Norsk",
            "Italiensk",
            "Fransk", 
            "Spansk",
            "Asiatisk",
            "Indisk",
            "Amerikansk",
            "Meksikansk",
            "Middelhavet"
        ]
    },
    
    "main_ingredients": {
        "name": "Main Ingredients", 
        "name_no": "Hovedingredienser",
        "icon": "🥘",
        "color": "orange",
        "categories": [
            "Kjøtt og Fjærkre",
            "Fisk, sjømat, skalldyr og skjell",
            "Egg",
            "Ost", 
            "Grønnsaker",
            "Potet",
            "Sopp",
            "Bønner og gryn",
            "Pasta"
        ]
    },
    
    "cooking_methods": {
        "name": "Cooking Methods",
        "name_no": "Tilberedning", 
        "icon": "👨‍🍳",
        "color": "red",
        "categories": [
            "Grill / Steking",
            "Ovnsretter", 
            "Gryter",
            "Supper og kraft",
            "Pizza",
            "Burger/toast",
            "Wrap / Taco"
        ]
    },
    
    "dietary": {
        "name": "Dietary",
        "name_no": "Kosthold",
        "icon": "🥬", 
        "color": "violet",
        "categories": [
            "Vegetar",
            "Rask mat"
        ]
    },
    
    "seasons": {
        "name": "Seasons",
        "name_no": "Årstider",
        "icon": "🍂",
        "color": "primary",
        "categories": [
            "Vår", 
            "Sommer",
            "Høst", 
            "Vinter"
        ]
    },
    
    "other": {
        "name": "Other",
        "name_no": "Annet",
        "icon": "📂",
        "color": "gray",
        "categories": [
            "Tilbehør",
            "Salat", 
            "Grunnoppskrifter",
            "Krydder",
            "Dressing/dip/saus/vinaigrette",
            "Konservering",
            "Drinker"
        ]
    }
}

def get_all_categories():
    """Get all categories in a flat list"""
    categories = []
    for group_data in CATEGORY_GROUPS.values():
        categories.extend(group_data["categories"])
    return categories

def get_category_group(category_name):
    """Find which group a category belongs to"""
    for group_key, group_data in CATEGORY_GROUPS.items():
        if category_name in group_data["categories"]:
            return group_key, group_data
    return None, None

def get_grouped_categories():
    """Get categories organized by groups for display"""
    return CATEGORY_GROUPS

def get_group_color(group_key):
    """Get the color for a specific group"""
    return CATEGORY_GROUPS.get(group_key, {}).get("color", "gray")

def get_group_icon(group_key):
    """Get the icon for a specific group"""
    return CATEGORY_GROUPS.get(group_key, {}).get("icon", "📂")