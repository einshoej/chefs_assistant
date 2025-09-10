"""
Chef's Assistant - Recipe Calendar Application

A Streamlit-based recipe management and meal planning application for organizing
recipes and planning meals with session-based storage for optimal performance.

Features:
- Weekly meal planning interface
- Recipe browsing and search functionality
- Session-based storage (no persistent files)

Architecture:
- Frontend: Streamlit with multi-page navigation
- Backend: Python
- Storage: In-memory session state (st.session_state)
- Authentication: Streamlit native auth system
"""

import sys
import os
from pathlib import Path

# Add project root to Python path for imports
try:
    project_root = Path(__file__).parent
except NameError:
    # Fallback for environments where __file__ is not defined
    project_root = Path.cwd()

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import streamlit as st
from src.utils.auth import is_user_logged_in, show_login_page
from src.utils.settings import initialize_user_settings

# Configure page settings
st.set_page_config(
    page_title="Chef's Assistant",
    page_icon=":material/chef_hat:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Check if user is logged in
    if is_user_logged_in():
        # Initialize user settings (load from Google Drive if available)
        initialize_user_settings()
        
        # Set up navigation pages with hierarchical structure
        pages = [            
                st.Page("src/pages/this_week/main.py", title="This Week", icon=":material/room_service:", url_path="this-week"),            
                st.Page("src/pages/browse_recipes/main.py", title="View all recipes", icon=":material/search:", url_path="browse-recipes"),
                st.Page("src/pages/view_recipe/main.py", title="Recipe Viewer", icon=":material/visibility:", url_path="view-recipe"),
                st.Page("src/pages/profile/main.py", title="Profile", icon=":material/person:", url_path="profile"),            
        ]
        
        # Create navigation
        navigation = st.navigation(pages,position="top")
        
        # Run the selected page
        navigation.run()
    else:
        # Show login page
        show_login_page()

if __name__ == "__main__":
    main()