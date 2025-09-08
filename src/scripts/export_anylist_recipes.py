#!/usr/bin/env python3
"""
Export all recipes from AnyList account to create default recipes for the app
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.anylist_integration.anylist_official_client import AnyListOfficialClient
from src.anylist_integration.credential_manager import get_credential_manager

# Setup logging to see detailed info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def progress_callback(current, total, message):
    """Progress callback for recipe fetching"""
    if total > 0:
        percent = (current / total) * 100
        print(f"\r{message} ({current}/{total} - {percent:.1f}%)", end="", flush=True)
    else:
        print(f"\r{message}", end="", flush=True)


def export_anylist_recipes():
    """Export all recipes from AnyList to default recipes file"""
    
    print("=" * 60)
    print("ANYLIST RECIPES EXPORT")
    print("=" * 60)
    
    # Get credentials from the manager
    cred_manager = get_credential_manager()
    
    # Check if we have saved credentials
    saved_creds = None
    try:
        # Try to load from session file first
        session_file = Path(__file__).parent.parent / "data" / "anylist_nodejs_session.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                email = session_data.get('email')
                if email:
                    saved_creds = cred_manager.get_credentials(email)
                    if saved_creds:
                        print(f"Found saved credentials for: {email}")
    except Exception as e:
        logger.debug(f"Could not load session file: {e}")
    
    # If no saved credentials, prompt for them
    if not saved_creds:
        print("\nAnyList Credentials Required")
        print("=" * 40)
        email = input("Enter your AnyList email: ")
        password = input("Enter your AnyList password: ")
        
        # Save credentials for future use
        try:
            username = email.split('@')[0]  # Use part before @ as username
            cred_manager.save_credentials(username, email, password)
            print(f"Credentials saved for future use")
        except Exception as e:
            print(f"Could not save credentials: {e}")
        
        creds = {'email': email, 'password': password}
    else:
        creds = saved_creds
    
    print(f"\nUsing AnyList account: {creds['email']}")
    print("=" * 60)
    
    # Create client and login
    client = AnyListOfficialClient(creds['email'], creds['password'])
    
    try:
        print("Logging in to AnyList...")
        if not client.login():
            print("Failed to login to AnyList")
            return False
        
        print("Successfully logged in!")
        print("=" * 60)
        
        # Fetch all recipes with full details
        print("\nFetching all recipes with full details...")
        print("This may take a while depending on how many recipes you have...")
        
        recipes = client.fetch_recipes(
            fetch_details=True, 
            progress_callback=progress_callback
        )
        
        print()  # New line after progress
        
        if not recipes:
            print("No recipes were fetched")
            return False
        
        print(f"\nSuccessfully fetched {len(recipes)} recipes!")
        print("=" * 60)
        
        # Filter out any non-recipe entries (like collection headers)
        actual_recipes = []
        for recipe in recipes:
            name = recipe.get('name', '')
            # Skip collection headers or other non-recipe entries
            if 'AnyList Recipe Collection' not in name and name.strip():
                actual_recipes.append(recipe)
        
        print(f"\nFound {len(actual_recipes)} actual recipes (filtered out {len(recipes) - len(actual_recipes)} non-recipe entries)")
        
        if not actual_recipes:
            print("No actual recipes found after filtering")
            return False
        
        # Show some statistics
        recipes_with_photos = sum(1 for r in actual_recipes if r.get('photo', {}).get('hasPhoto'))
        recipes_with_ingredients = sum(1 for r in actual_recipes if r.get('ingredients'))
        recipes_with_steps = sum(1 for r in actual_recipes if r.get('preparationSteps'))
        recipes_with_rating = sum(1 for r in actual_recipes if r.get('rating', 0) > 0)
        
        print(f"{recipes_with_photos} recipes have photos")
        print(f"{recipes_with_ingredients} recipes have ingredients")
        print(f"{recipes_with_steps} recipes have preparation steps")
        print(f"{recipes_with_rating} recipes have ratings")
        
        # Prepare export data
        export_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'exported_from': creds['email'],
                'total_recipes': len(actual_recipes),
                'recipes_with_photos': recipes_with_photos,
                'recipes_with_ingredients': recipes_with_ingredients,
                'recipes_with_steps': recipes_with_steps,
                'recipes_with_rating': recipes_with_rating
            },
            'recipes': actual_recipes
        }
        
        # Save to default recipes file
        output_file = Path(__file__).parent.parent / "data" / "default_recipes.json"
        
        print(f"\nSaving recipes to: {output_file}")
        
        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully saved {len(actual_recipes)} recipes to default_recipes.json")
        print(f"File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        # Show sample recipes
        print("\nSample of exported recipes:")
        print("-" * 40)
        for i, recipe in enumerate(actual_recipes[:5], 1):
            name = recipe.get('name', 'Unnamed')
            rating = recipe.get('rating', 0)
            ingredients_count = len(recipe.get('ingredients', []))
            steps_count = len(recipe.get('preparationSteps', []))
            has_photo = recipe.get('photo', {}).get('hasPhoto', False)
            
            print(f"{i}. {name}")
            if rating > 0:
                print(f"   Rating: {rating}/5")
            if ingredients_count > 0:
                print(f"   {ingredients_count} ingredients")
            if steps_count > 0:
                print(f"   {steps_count} steps")
            if has_photo:
                print(f"   Has photo")
        
        if len(actual_recipes) > 5:
            print(f"   ... and {len(actual_recipes) - 5} more recipes")
        
        print("\n" + "=" * 60)
        print("Export completed successfully!")
        print(f"Your {len(actual_recipes)} recipes are now available as default recipes in the app")
        
        return True
        
    except Exception as e:
        print(f"\nError during export: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        client.close()


if __name__ == "__main__":
    success = export_anylist_recipes()
    
    if success:
        print("\nExport completed successfully!")
        print("The recipes will now be available as default recipes when you start the app")
        sys.exit(0)
    else:
        print("\nExport failed - please check the output above")
        sys.exit(1)