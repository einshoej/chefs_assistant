"""
Profile page - Display user profile information
"""

import streamlit as st


def profile():
    """Display user profile information"""
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 👤 User Profile")
        
        # Display user avatar if available
        if hasattr(st.user, 'picture') and st.user.picture:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{st.user.picture}" style="border-radius: 50%; width: 100px; height: 100px;">
            </div>
            """, unsafe_allow_html=True)
        
        # Display user information
        st.info(f"**Name:** {getattr(st.user, 'name', 'N/A')}")
        st.info(f"**Email:** {getattr(st.user, 'email', 'N/A')}")
        
        # Display additional user attributes if available
        if hasattr(st.user, 'given_name') or hasattr(st.user, 'family_name'):
            given = getattr(st.user, 'given_name', '')
            family = getattr(st.user, 'family_name', '')
            if given or family:
                st.info(f"**Full Name:** {given} {family}".strip())
        
        if hasattr(st.user, 'email_verified'):
            verified = getattr(st.user, 'email_verified', False)
            st.success(f"**Email Verified:** {'✅ Yes' if verified else '❌ No'}")
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            st.logout()


if __name__ == "__page__":
    profile()
