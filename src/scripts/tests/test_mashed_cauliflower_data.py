#!/usr/bin/env python3
"""
Test script to verify Mashed Cauliflower recipe data capture from AnyList
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


def test_mashed_cauliflower():
    """Test fetching and verifying Mashed Cauliflower recipe data"""
    
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
        print("=" * 60)
        
        # Fetch recipes
        print("\n🔄 Fetching recipes...")
        recipes = client.fetch_recipes()
        
        if not recipes:
            print("❌ No recipes were fetched")
            return False
        
        print(f"✅ Successfully fetched {len(recipes)} recipes!")
        
        # Find Mashed Cauliflower recipe
        mashed_cauliflower = None
        for recipe in recipes:
            if "Mashed Cauliflower" in recipe.get('name', ''):
                mashed_cauliflower = recipe
                break
        
        if not mashed_cauliflower:
            print("\n⚠️ Mashed Cauliflower recipe not found!")
            print("Available recipes containing 'cauliflower' (case-insensitive):")
            cauliflower_recipes = [r for r in recipes if 'cauliflower' in r.get('name', '').lower()]
            for r in cauliflower_recipes[:5]:
                print(f"  - {r.get('name')}")
            return False
        
        print("\n✅ Found Mashed Cauliflower recipe!")
        print("=" * 60)
        
        # Display recipe details
        print("\n📖 Recipe Details:")
        print(f"Name: {mashed_cauliflower.get('name')}")
        print(f"ID: {mashed_cauliflower.get('id')}")
        
        # Check for picture
        photo = mashed_cauliflower.get('photo', {})
        has_photo = photo.get('hasPhoto', False)
        photo_url = photo.get('url', '') if has_photo else None
        
        print("\n🖼️  Picture:")
        if has_photo and photo_url:
            print(f"  ✅ Has picture: {photo_url[:50]}...")
        else:
            print("  ❌ No picture found")
        
        # Check for collections
        collections = mashed_cauliflower.get('collections', [])
        expected_collections = ['Grønnsaker', 'Vår', 'Sommer', 'Høst', 'Vinter', 'Tilbehør']
        
        print("\n📁 Collections:")
        if collections:
            print(f"  Found {len(collections)} collection(s):")
            for coll in collections:
                check = "✅" if coll in expected_collections else "📌"
                print(f"    {check} {coll}")
            
            # Check which expected collections are missing
            missing_collections = [c for c in expected_collections if c not in collections]
            if missing_collections:
                print("\n  ⚠️ Missing expected collections:")
                for coll in missing_collections:
                    print(f"    ❌ {coll}")
            else:
                print("\n  ✅ All expected collections found!")
        else:
            print("  ❌ No collections found")
            print(f"  Expected: {', '.join(expected_collections)}")
        
        # Display other recipe information
        print("\n📊 Other Information:")
        if mashed_cauliflower.get('description'):
            desc = mashed_cauliflower.get('description', '')
            if desc:
                print(f"  Description: {desc[:100]}...")
        if mashed_cauliflower.get('prep_time'):
            print(f"  Prep Time: {mashed_cauliflower.get('prep_time')} minutes")
        if mashed_cauliflower.get('cook_time'):
            print(f"  Cook Time: {mashed_cauliflower.get('cook_time')} minutes")
        if mashed_cauliflower.get('servings'):
            print(f"  Servings: {mashed_cauliflower.get('servings')}")
        rating = mashed_cauliflower.get('rating')
        if rating and rating > 0:
            print(f"  Rating: {'★' * rating}{'☆' * (5 - rating)}")
        
        ingredients = mashed_cauliflower.get('ingredients', [])
        if ingredients:
            print(f"  Ingredients: {len(ingredients)} items")
        
        steps = mashed_cauliflower.get('preparation_steps', [])
        if steps:
            print(f"  Preparation Steps: {len(steps)} steps")
        
        print("\n" + "=" * 60)
        
        # Test fetching collections separately
        print("\n🔄 Testing collection fetch...")
        collections_result = client.get_recipe_collections()
        if collections_result:
            print(f"✅ Successfully fetched {len(collections_result)} collections")
            print("\nAvailable collections:")
            for coll in collections_result[:10]:
                print(f"  - {coll.get('name')} ({coll.get('recipeCount', 0)} recipes)")
        else:
            print("⚠️ Could not fetch collections separately")
        
        print("\n" + "=" * 60)
        
        # Summary
        print("\n📋 SUMMARY:")
        validation_passed = True
        
        # Check picture
        if has_photo and photo_url:
            print("✅ Picture: Found")
        else:
            print("❌ Picture: Missing")
            validation_passed = False
        
        # Check collections
        if collections and all(c in collections for c in expected_collections):
            print(f"✅ Collections: All {len(expected_collections)} expected collections found")
        elif collections:
            found_count = sum(1 for c in expected_collections if c in collections)
            print(f"⚠️ Collections: {found_count}/{len(expected_collections)} expected collections found")
            validation_passed = False
        else:
            print("❌ Collections: None found")
            validation_passed = False
        
        return validation_passed
        
    except (ConnectionError, TimeoutError, ValueError) as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        client.close()
        print("\n🔒 Client closed")


if __name__ == "__main__":
    print("=" * 60)
    print("MASHED CAULIFLOWER DATA VERIFICATION TEST")
    print("=" * 60)
    
    success = test_mashed_cauliflower()
    
    if success:
        print("\n🎉 All data captured successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Some data is missing - please check the output above")
        sys.exit(1)
