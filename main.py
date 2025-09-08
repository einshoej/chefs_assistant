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

import streamlit as st
from src.utils.auth import is_user_logged_in, show_login_page
from src.pages.this_week.main import main as this_week
from src.pages.browse_recipes.main import view_all_recipes
from src.pages.profile.main import profile

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