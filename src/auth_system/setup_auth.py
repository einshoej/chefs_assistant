#!/usr/bin/env python3
"""
Helper script to set up authentication configuration for Streamlit
"""

import os
import secrets
import shutil
from pathlib import Path

def generate_cookie_secret():
    """Generate a strong random cookie secret"""
    return secrets.token_urlsafe(32)

def setup_secrets_file():
    """Set up the secrets.toml file"""
    streamlit_dir = Path(".streamlit")
    secrets_file = streamlit_dir / "secrets.toml"
    example_file = streamlit_dir / "secrets.toml.example"
    
    # Create .streamlit directory if it doesn't exist
    streamlit_dir.mkdir(exist_ok=True)
    
    # Check if secrets.toml already exists
    if secrets_file.exists():
        response = input("secrets.toml already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing secrets.toml")
            return False
    
    # Copy example file if it exists
    if example_file.exists():
        shutil.copy(example_file, secrets_file)
        print(f"Created {secrets_file} from example file")
    else:
        # Create a new secrets.toml file
        content = f'''# Streamlit Native Authentication Configuration
[auth]
# Redirect URI - should match what's configured in Google Cloud Console
redirect_uri = "http://localhost:8501/oauth2callback"

# Cookie secret - strong, randomly generated string
cookie_secret = "{generate_cookie_secret()}"

# Google OAuth Credentials - Get these from Google Cloud Console
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"

# Google's OIDC server metadata URL (standard for all Google OIDC clients)
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
'''
        secrets_file.write_text(content)
        print(f"Created {secrets_file} with default configuration")
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("Streamlit Authentication Setup Helper")
    print("=" * 60)
    print()
    
    # Generate a cookie secret for the user to copy
    print("Generated Cookie Secret (copy this if needed):")
    print(f"  {generate_cookie_secret()}")
    print()
    
    # Ask if user wants to create secrets.toml
    response = input("Do you want to create/update .streamlit/secrets.toml? (y/N): ")
    if response.lower() == 'y':
        if setup_secrets_file():
            print("\n✅ secrets.toml file created/updated successfully!")
            print("\n⚠️  Next steps:")
            print("1. Edit .streamlit/secrets.toml")
            print("2. Replace 'your-client-id.apps.googleusercontent.com' with your Google Client ID")
            print("3. Replace 'your-client-secret' with your Google Client Secret")
            print("4. The cookie_secret has been auto-generated for you")
            print("\nGet your Google OAuth credentials from:")
            print("https://console.cloud.google.com/")
    else:
        print("\nManual setup required:")
        print("1. Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml")
        print("2. Add your Google OAuth credentials")
        print("3. Use the cookie secret generated above")
    
    print("\n" + "=" * 60)
    print("Setup complete! Run 'streamlit run main.py' to start your app")
    print("=" * 60)

if __name__ == "__main__":
    main()
