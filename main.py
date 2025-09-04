"""
Chef's Assistant - Recipe Calendar Application

A Streamlit-based recipe management and meal planning application that integrates 
with AnyList for recipe importing and uses session-based storage for optimal performance.

Features:
- AnyList recipe synchronization via official API
- Weekly meal planning interface
- Recipe browsing and search functionality
- Secure credential management with encryption
- Session-based storage (no persistent files)

Architecture:
- Frontend: Streamlit with multi-page navigation
- Backend: Python with Node.js bridge for AnyList API
- Storage: In-memory session state (st.session_state)
- Authentication: Streamlit native auth system
"""

import streamlit as st
from src.utils.auth import is_user_logged_in, show_login_page
from src.pages.this_week.main import main as this_week
from src.pages.browse_recipes.main import view_all_recipes
from src.pages.profile.main import profile
from src.pages.anylist_settings.main import anylist_settings

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
        # Set up navigation pages with hierarchical structure
        pages = [            
                st.Page(this_week, title="This Week", icon=":material/room_service:", url_path="this-week"),            
                st.Page(view_all_recipes, title="View all recipes", icon=":material/search:", url_path="browse-recipes"),
                st.Page(anylist_settings, title="Settings", icon=":material/settings:", url_path="settings"),
                st.Page(profile, title="Profile", icon=":material/person:", url_path="profile"),            
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