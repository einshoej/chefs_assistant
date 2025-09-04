#!/usr/bin/env python
"""
Test script to verify Google Drive storage setup
Run this after configuring your Google OAuth with Drive scope
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_imports():
    """Test if all required Google Drive packages are installed"""
    print("Testing Google Drive API imports...")
    
    try:
        from google.oauth2.credentials import Credentials
        print("✅ google.oauth2.credentials - OK")
    except ImportError as e:
        print(f"❌ google.oauth2.credentials - FAILED: {e}")
        return False
    
    try:
        from googleapiclient.discovery import build
        print("✅ googleapiclient.discovery - OK")
    except ImportError as e:
        print(f"❌ googleapiclient.discovery - FAILED: {e}")
        return False
    
    try:
        from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
        print("✅ googleapiclient.http - OK")
    except ImportError as e:
        print(f"❌ googleapiclient.http - FAILED: {e}")
        return False
    
    try:
        from googleapiclient.errors import HttpError
        print("✅ googleapiclient.errors - OK")
    except ImportError as e:
        print(f"❌ googleapiclient.errors - FAILED: {e}")
        return False
    
    return True


def test_streamlit_config():
    """Test if Streamlit secrets are configured correctly"""
    print("\nTesting Streamlit configuration...")
    
    secrets_path = ".streamlit/secrets.toml"
    
    if not os.path.exists(secrets_path):
        print(f"❌ {secrets_path} not found")
        print("   Run: python setup_auth.py")
        return False
    
    print(f"✅ {secrets_path} exists")
    
    # Check if file contains Drive scope
    with open(secrets_path, 'r') as f:
        content = f.read()
        
        if 'client_id' not in content:
            print("❌ client_id not found in secrets.toml")
            return False
        print("✅ client_id configured")
        
        if 'client_secret' not in content:
            print("❌ client_secret not found in secrets.toml")
            return False
        print("✅ client_secret configured")
        
        if 'drive.file' in content:
            print("✅ Google Drive scope configured")
        else:
            print("⚠️  Google Drive scope not found")
            print("   Add to secrets.toml:")
            print('   client_kwargs = { scope = "openid email profile https://www.googleapis.com/auth/drive.file" }')
    
    return True


def test_module_import():
    """Test if our Google Drive storage module can be imported"""
    print("\nTesting custom module import...")
    
    try:
        from src.data.google_drive_storage import GoogleDriveRecipeStorage
        print("✅ GoogleDriveRecipeStorage module - OK")
        
        from src.data.google_drive_storage import get_google_drive_storage
        print("✅ get_google_drive_storage function - OK")
        
        return True
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False


def main():
    print("="*60)
    print("GOOGLE DRIVE STORAGE SETUP TEST")
    print("="*60)
    
    all_ok = True
    
    # Test imports
    if not test_imports():
        all_ok = False
        print("\n⚠️  Install missing packages with:")
        print("   pip install -r requirements.txt")
    
    # Test Streamlit config
    if not test_streamlit_config():
        all_ok = False
    
    # Test module
    if not test_module_import():
        all_ok = False
    
    # Summary
    print("\n" + "="*60)
    if all_ok:
        print("✅ ALL TESTS PASSED!")
        print("\nYour Google Drive storage is ready to use.")
        print("Run the app with: streamlit run main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the app.")
        print("See GOOGLE_DRIVE_STORAGE_SETUP.md for detailed instructions.")
    print("="*60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

