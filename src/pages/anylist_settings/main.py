"""
AnyList Settings Page - Configure AnyList integration
"""

import streamlit as st
from src.anylist_integration.credential_manager import get_credential_manager
from src.anylist_integration.anylist_official_client import AnyListOfficialClient
from src.anylist_integration.nodejs_check import is_nodejs_available, get_nodejs_status_message
from src.utils.auth import is_user_logged_in


def anylist_settings():
    """Display AnyList integration and Google Drive settings"""
    # Check authentication
    if not is_user_logged_in():
        st.error("Please login to access this page")
        st.stop()
    
    # Create tabs for different settings
    tab1, tab2 = st.tabs(["AnyList Integration", "Google Drive Storage"])
    
    with tab1:
        display_anylist_settings()
    
    with tab2:
        display_google_drive_settings()


def display_google_drive_settings():
    """Display Google Drive storage settings"""
    st.header("☁️ Google Drive Storage")
    
    from src.utils.google_drive_oauth import show_google_drive_auth
    
    # Show the authorization component using streamlit-oauth
    show_google_drive_auth()
    
    st.divider()
    
    # Show storage status
    st.subheader("📊 Storage Status")
    
    from src.data.google_drive_storage import get_google_drive_storage
    storage = get_google_drive_storage()
    
    if storage:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Load from Drive", use_container_width=True):
                with st.spinner("Loading from Google Drive..."):
                    from src.pages.browse_recipes.session_state import load_recipes_from_drive
                    load_recipes_from_drive()
                    st.success("Loaded data from Google Drive")
                    st.rerun()
        
        with col2:
            if st.button("💾 Save to Drive", use_container_width=True):
                with st.spinner("Saving to Google Drive..."):
                    from src.pages.browse_recipes.session_state import save_recipes_to_drive
                    from src.pages.this_week.session_manager import WeeklyRecipeManager
                    
                    recipes_saved = save_recipes_to_drive()
                    weekly_saved = WeeklyRecipeManager.save_to_drive()
                    
                    if recipes_saved and weekly_saved:
                        st.success("All data saved to Google Drive")
                    elif recipes_saved or weekly_saved:
                        st.warning("Some data saved to Google Drive")
                    else:
                        st.error("Failed to save to Google Drive")
        
        with col3:
            if st.button("🗑️ Clear Drive Data", type="secondary", use_container_width=True):
                if st.checkbox("I understand this will delete all app data from Drive"):
                    if storage.delete_all_data():
                        st.success("Deleted all app data from Google Drive")
                        st.session_state.recipes_loaded_from_drive = False
                    else:
                        st.error("Failed to delete data from Google Drive")
        
        # Display stored data info
        st.divider()
        st.subheader("📁 Stored Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            recipes_count = len(st.session_state.get('anylist_recipes', [])) + len(st.session_state.get('local_recipes', []))
            st.metric("Total Recipes", recipes_count)
        
        with col2:
            weekly_count = len(st.session_state.get('weekly_recipes', []))
            st.metric("Weekly Recipes", weekly_count)
        
        with col3:
            plans_count = len(st.session_state.get('weekly_plans', {}))
            st.metric("Meal Plans", plans_count)
        
        if st.session_state.get('last_anylist_sync'):
            st.caption(f"Last AnyList sync: {st.session_state.last_anylist_sync}")
    else:
        st.info("Connect Google Drive above to enable cloud storage for your recipes and meal plans.")


def display_anylist_settings():
    """Display AnyList integration settings"""
    st.header("🔗 AnyList Integration")
    
    # Check Node.js availability
    nodejs_available, nodejs_message = get_nodejs_status_message()
    
    if not nodejs_available:
        st.warning(nodejs_message)
        st.info(
            "You can still manually add recipes using the Browse Recipes page.\n"
            "All other features of the app will work normally."
        )
        return
    
    # Get current user
    # Use email as unique identifier for credential storage
    username = getattr(st.user, 'email', None) or st.session_state.get('username', '')
    if not username:
        st.error("User session not found. Please login again.")
        st.stop()
    
    # Get credential manager
    cred_manager = get_credential_manager()
    
    # Check if user has existing credentials
    has_creds = cred_manager.has_credentials(username)
    
    if has_creds:
        display_connected_status(username, cred_manager)
    else:
        display_connection_form(username, cred_manager)


def display_connected_status(username: str, cred_manager):
    """Display status when AnyList is connected"""
    st.success("✅ AnyList account connected")
    
    # Get stored credentials
    creds = cred_manager.get_credentials(username)
    if creds:
        st.info(f"Connected email: {creds.get('email', 'Unknown')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Test Connection", use_container_width=True):
            test_anylist_connection(username, cred_manager)
    
    with col2:
        if st.button("🔄 Sync Recipes Now", use_container_width=True):
            sync_recipes(username, cred_manager)
    
    with col3:
        if st.button("🔌 Disconnect AnyList", type="secondary", use_container_width=True):
            if cred_manager.remove_credentials(username):
                st.success("AnyList account disconnected")
                st.rerun()
            else:
                st.error("Failed to disconnect AnyList account")
    
    # Display sync settings
    st.divider()
    st.subheader("Sync Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        auto_sync = st.checkbox(
            "Enable automatic sync",
            value=st.session_state.get('anylist_auto_sync', False),
            help="Automatically sync recipes when you open the app"
        )
        if auto_sync != st.session_state.get('anylist_auto_sync', False):
            st.session_state.anylist_auto_sync = auto_sync
    
    with col2:
        sync_interval = st.selectbox(
            "Sync frequency",
            ["On app start", "Every hour", "Every day", "Manual only"],
            index=3,
            disabled=not auto_sync
        )
    
    # Display last sync info
    if 'last_anylist_sync' in st.session_state:
        st.caption(f"Last synced: {st.session_state.last_anylist_sync}")
    
    # Recipe statistics
    if 'anylist_recipes' in st.session_state:
        st.divider()
        st.subheader("📊 Recipe Statistics")
        
        recipes = st.session_state.anylist_recipes
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Recipes", len(recipes))
        
        with col2:
            # Count recipes with tags
            tagged = sum(1 for r in recipes if r.get('tags'))
            st.metric("Tagged Recipes", tagged)
        
        with col3:
            # Count recipes with complete info
            complete = sum(1 for r in recipes if r.get('ingredients') and r.get('instructions'))
            st.metric("Complete Recipes", complete)


def display_connection_form(username: str, cred_manager):
    """Display form to connect AnyList account"""
    st.info("Connect your AnyList account to import your recipes")
    
    with st.form("anylist_connection"):
        st.subheader("AnyList Login")
        
        email = st.text_input(
            "Email", 
            placeholder="your.email@example.com",
            help="The email address you use to login to AnyList"
        )
        
        password = st.text_input(
            "Password", 
            type="password",
            help="Your AnyList password (will be encrypted and stored securely)"
        )
        
        st.caption("⚠️ Your credentials will be encrypted and stored locally. We recommend using app-specific passwords if available.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_connection = st.form_submit_button(
                "Test Connection",
                use_container_width=True,
                help="Test the connection without saving credentials"
            )
        
        with col2:
            save_connection = st.form_submit_button(
                "Connect & Save",
                type="primary",
                use_container_width=True,
                help="Save credentials and connect to AnyList"
            )
        
        if test_connection:
            if email and password:
                with st.spinner("Testing connection..."):
                    client = AnyListOfficialClient(email, password)
                    if client.login():
                        st.success("✅ Connection successful! You can now save your credentials.")
                        client.close()
                    else:
                        st.error("❌ Connection failed. Please check your credentials.")
            else:
                st.error("Please enter both email and password")
        
        if save_connection:
            if email and password:
                with st.spinner("Connecting to AnyList..."):
                    # Test connection first
                    client = AnyListOfficialClient(email, password)
                    if client.login():
                        # Save credentials
                        if cred_manager.save_credentials(username, email, password):
                            st.success("✅ AnyList account connected successfully!")
                            
                            # Fetch initial recipes
                            recipes = client.fetch_recipes()
                            st.session_state.anylist_recipes = recipes
                            
                            from datetime import datetime
                            st.session_state.last_anylist_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            client.close()
                            st.rerun()
                        else:
                            st.error("Failed to save credentials")
                            client.close()
                    else:
                        st.error("❌ Connection failed. Please check your credentials.")
            else:
                st.error("Please enter both email and password")


def test_anylist_connection(username: str, cred_manager):
    """Test the stored AnyList connection"""
    creds = cred_manager.get_credentials(username)
    if not creds:
        st.error("No credentials found")
        return
    
    with st.spinner("Testing connection..."):
        client = AnyListOfficialClient(creds['email'], creds['password'])
        if client.login():
            st.success("✅ Connection test successful!")
            client.close()
        else:
            st.error("❌ Connection test failed. You may need to update your credentials.")


def sync_recipes(username: str, cred_manager):
    """Sync recipes from AnyList"""
    creds = cred_manager.get_credentials(username)
    if not creds:
        st.error("No credentials found")
        return
    
    with st.spinner("Syncing recipes from AnyList..."):
        client = AnyListOfficialClient(creds['email'], creds['password'])
        if client.login():
            recipes = client.fetch_recipes()
            if recipes:
                st.session_state.anylist_recipes = recipes
                
                from datetime import datetime
                st.session_state.last_anylist_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save to Google Drive if available
                from src.pages.browse_recipes.session_state import save_recipes_to_drive
                if save_recipes_to_drive():
                    st.success(f"✅ Synced {len(recipes)} recipes from AnyList and saved to Google Drive")
                else:
                    st.success(f"✅ Synced {len(recipes)} recipes from AnyList")
                
                st.rerun()
            else:
                st.warning("No recipes found or unable to fetch recipes")
            client.close()
        else:
            st.error("❌ Failed to connect to AnyList")


if __name__ == "__page__":
    anylist_settings()
