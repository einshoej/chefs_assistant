"""
Profile page - Display user profile information
"""

import streamlit as st
from src.utils.settings import save_user_settings_to_drive


def on_meals_per_week_change():
    """Callback function triggered when meals_per_week slider changes"""
    try:
        success = save_user_settings_to_drive()
        if success:
            st.toast("✅ Settings saved to Google Drive!", icon="✅")
        else:
            st.toast("⚠️ Could not save to Google Drive", icon="⚠️")
    except Exception as e:
        st.toast(f"❌ Error saving settings: {str(e)}", icon="❌")


def profile():
    """Display user profile information with tabs"""
    st.title("👤 Profile")
    
    # Initialize meals per week preference if not exists
    if "meals_per_week" not in st.session_state:
        st.session_state.meals_per_week = 3
    
    # Create tabs
    tab1, tab2 = st.tabs(["📋 Subscription", "👤 Personal Information"])
    
    with tab1:
        st.header("Subscription Details")
        
        # Subscription status
        st.success("🎯 **Current Plan:** Beta User")
        st.info("You're currently enjoying early access to Chef's Assistant!")
        
        st.divider()
        
        # Meal planning preference
        st.subheader("Meal Planning Preferences")
        meals_per_week = st.slider(
            "How many meals per week would you like to plan?",
            min_value=1,
            max_value=7,
            value=st.session_state.meals_per_week,
            help="This setting helps us customize your meal planning experience",
            on_change=on_meals_per_week_change,
            key="meals_per_week"
        )
    
    with tab2:
        st.header("Personal Information")
        
        # User avatar and basic info section
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if hasattr(st.user, 'picture') and st.user.picture:
                st.image(st.user.picture, width=120)
            else:
                st.markdown("📷 No profile picture")
        
        with col2:
            # Display user information in a cleaner format
            user_name = getattr(st.user, 'name', 'N/A')
            user_email = getattr(st.user, 'email', 'N/A')
            
            st.markdown(f"**Name:** {user_name}")
            st.markdown(f"**Email:** {user_email}")
            
            # Additional user details if available
            if hasattr(st.user, 'given_name') and hasattr(st.user, 'family_name'):
                given = getattr(st.user, 'given_name', '')
                family = getattr(st.user, 'family_name', '')
                if given or family:
                    st.markdown(f"**Full Name:** {given} {family}".strip())
            
            if hasattr(st.user, 'email_verified'):
                verified = getattr(st.user, 'email_verified', False)
                if verified:
                    st.success("✅ Email Verified")
                else:
                    st.warning("❌ Email Not Verified")
        
        st.divider()
        
        # Account actions
        st.subheader("Account Actions")
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.logout()


if __name__ == "__page__":
    profile()
