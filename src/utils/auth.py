"""
Authentication utilities for Chef's Assistant
"""

import streamlit as st


def check_auth_configured():
    """Check if authentication is properly configured"""
    try:
        # Check if st.user.is_logged_in exists (only available when auth is configured)
        return hasattr(st.user, 'is_logged_in')
    except AttributeError:
        return False


def is_user_logged_in():
    """Safely check if user is logged in"""
    try:
        return hasattr(st.user, 'is_logged_in') and st.user.is_logged_in
    except AttributeError:
        return False


def get_user_name():
    """Get the user's display name"""
    if not is_user_logged_in():
        return "User"
    
    # Try to get given name first, then full name, then default
    return getattr(st.user, 'given_name', None) or getattr(st.user, 'name', 'User')


def show_login_page():
    """Display the login page"""
    
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.title("Chef's Assistant")
        st.write("Plan your weekly meals with our easy-to-use recipe calendar application.")

        st.divider()
        st.title("Please sign in to continue")
        
        # Use native st.login with callback
        if st.button("Sign in with Google", width='stretch', type="primary", icon=":material/login:"):
            st.login()
        
        
        # Setup instructions if auth is not configured
        if not check_auth_configured():
            st.divider()
            st.error("⚠️ Authentication is not configured. Please set up Google OAuth.")
            
            with st.expander("📖 Setup Instructions", expanded=True):
                st.markdown("""
                ### Quick Setup Guide
                
                1. **Install required packages:**
                   ```bash
                   pip install -r requirements.txt
                   ```
                   Or specifically:
                   ```bash
                   pip install "streamlit[auth]>=1.37.0"
                   ```
                
                2. **Get Google OAuth Credentials:**
                   - Go to [Google Cloud Console](https://console.cloud.google.com/)
                   - Create a new project or select existing one
                   - Enable Google+ API
                   - Create OAuth 2.0 credentials (Web application)
                   - Add redirect URI: `http://localhost:8501/oauth2callback`
                
                3. **Configure Streamlit:**
                   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
                   - Fill in your Google OAuth credentials:
                     - `client_id`: Your Google client ID
                     - `client_secret`: Your Google client secret
                     - `cookie_secret`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
                   - Ensure the redirect URI matches exactly
                
                4. **Restart the app**
                
                See `STREAMLIT_NATIVE_AUTH_SETUP.md` for detailed instructions.
                """)


