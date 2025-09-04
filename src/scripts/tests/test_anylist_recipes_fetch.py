#!/usr/bin/env python3
"""
Test script to verify AnyList recipe fetching is working correctly
"""

import sys
import os
import logging

# Setup path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.anylist_integration.anylist_official_client import AnyListOfficialClient
from src.anylist_integration.credential_manager import get_credential_manager

# Setup logging to see detailed info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_anylist_fetch():
    """Test fetching recipes from AnyList"""
    
    # Get credentials from the manager (assuming they're already saved)
    cred_manager = get_credential_manager()
    
    # Use your actual username/email that you use for authentication
    username = input("Enter your username/email for credential lookup: ")
    
    creds = cred_manager.get_credentials(username)
    if not creds:
        print("❌ No credentials found. Please set up AnyList credentials first.")
        return False
    
    print(f"\n📧 Using AnyList account: {creds['email']}")
    print("=" * 60)
    
    # Create client and login
    client = AnyListOfficialClient(creds['email'], creds['password'])
    
    try:
        print("🔄 Logging in to AnyList...")
        if not client.login():
            print("❌ Failed to login to AnyList")
            return False
        
        print("✅ Successfully logged in!")
        print(f"📚 Total recipes in account: {client.recipes_count}")
        print("=" * 60)
        
        # Ask user if they want to fetch detailed information
        print("\n⚠️ Note: Fetching detailed recipe information takes longer")
        fetch_details = input("Fetch detailed recipe information? (y/n, default=n): ").lower() == 'y'
        
        # Fetch recipes
        print(f"\n🔄 Fetching recipes{' with details' if fetch_details else ' (names only)'}...")
        recipes = client.fetch_recipes(fetch_details=fetch_details)
        
        if not recipes:
            print("❌ No recipes were fetched")
            return False
        
        print(f"\n✅ Successfully fetched {len(recipes)} recipes!")
        print("=" * 60)
        
        # Display the fetched recipes
        print("\n📋 Fetched Recipes:")
        print("-" * 60)
        
        # Show first 10 recipes in detail, then summarize the rest
        max_detailed_display = 10
        
        for i, recipe in enumerate(recipes[:max_detailed_display], 1):
            name = recipe.get('name', 'Unnamed')
            prep_time = recipe.get('prep_time', 0)
            cook_time = recipe.get('cook_time', 0)
            servings = recipe.get('servings', 0)
            rating = recipe.get('rating', 0)
            collections = recipe.get('collections', [])
            ingredients = recipe.get('ingredients', {})
            preparation_steps = recipe.get('preparation_steps', {})
            image = recipe.get('image', None)
            
            print(f"\n{i}. {name}")
            
            # Display metadata
            if prep_time > 0:
                print(f"   ⏱️  Prep Time: {prep_time} minutes")
            if cook_time > 0:
                print(f"   🔥 Cook Time: {cook_time} minutes")
            if servings > 0:
                print(f"   🍽️  Servings: {servings}")
            if rating > 0:
                print(f"   ⭐ Rating: {'★' * rating}{'☆' * (5 - rating)}")
            
            # Show collections/tags
            if collections:
                print(f"   📁 Collections: {', '.join(collections)}")
            
            # Show ingredients if available
            if ingredients:
                print(f"   🥘 Ingredients: {len(ingredients)} items")
                # Show first 3 ingredients as examples
                for ingredient, quantity in list(ingredients.items())[:3]:
                    print(f"      - {quantity} {ingredient}" if quantity else f"      - {ingredient}")
                if len(ingredients) > 3:
                    print(f"      ... and {len(ingredients) - 3} more")
            
            # Show preparation steps if available
            if preparation_steps:
                print(f"   📝 Steps: {len(preparation_steps)} steps")
                # Show first step as example
                if 1 in preparation_steps:
                    first_step = preparation_steps[1][:100] + "..." if len(preparation_steps[1]) > 100 else preparation_steps[1]
                    print(f"      Step 1: {first_step}")
            
            # Note if image is available
            if image:
                print(f"   🖼️  Image: Available")
        
        # If there are more recipes, show summary
        if len(recipes) > max_detailed_display:
            print(f"\n... and {len(recipes) - max_detailed_display} more recipes")
            print(f"\nShowing first {max_detailed_display} recipes in detail for brevity")
        
        print("\n" + "=" * 60)
        
        # Analysis
        actual_recipes = [r for r in recipes if 'AnyList Recipe Collection' not in r.get('name', '')]
        
        if actual_recipes:
            print(f"\n✅ SUCCESS! Found {len(actual_recipes)} actual recipes")
            print("The sync is now working correctly!")
        else:
            print("\n⚠️ WARNING: Only found navigation/summary entries, no actual recipes")
            print("The AnyList web interface may require additional navigation to access recipes")
            print("\nPossible solutions:")
            print("1. The recipes might be in a different view that requires clicking")
            print("2. The website structure may have changed")
            print("3. Try running the app in non-headless mode to see what's happening")
        
        return len(actual_recipes) > 0
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        client.close()
        print("\n🔒 Browser closed")

if __name__ == "__main__":
    print("=" * 60)
    print("ANYLIST RECIPE FETCH TEST")
    print("=" * 60)
    
    success = test_anylist_fetch()
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed - please check the output above")
        sys.exit(1)
