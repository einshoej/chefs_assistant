"""
Google Drive OAuth using streamlit-oauth component
This replaces the problematic custom OAuth implementation
"""

import streamlit as st
import logging
from typing import Optional
from streamlit_oauth import OAuth2Component
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import base64

logger = logging.getLogger(__name__)

# Google Drive scope
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"


class GoogleDriveOAuth:
    """Manages Google Drive OAuth using streamlit-oauth component"""
    
    def __init__(self):
        self.token_key = 'google_drive_token_oauth'
        
        # Get client credentials from secrets
        if 'google_drive' in st.secrets:
            self.client_id = st.secrets.google_drive.get("client_id")
            self.client_secret = st.secrets.google_drive.get("client_secret")
        else:
            self.client_id = None
            self.client_secret = None
            logger.error("Google Drive credentials not found in secrets")
    
    def get_oauth_component(self) -> Optional[OAuth2Component]:
        """Create OAuth2 component for Google Drive"""
        if not self.client_id or not self.client_secret:
            logger.error("Missing Google Drive credentials")
            return None
            
        # Create OAuth2 component
        return OAuth2Component(
            self.client_id,
            self.client_secret,
            "https://accounts.google.com/o/oauth2/v2/auth",
            "https://oauth2.googleapis.com/token",
            "https://oauth2.googleapis.com/token",
            "https://oauth2.googleapis.com/revoke"
        )
    
    def get_stored_token(self) -> Optional[dict]:
        """Get stored token from session state"""
        if self.token_key in st.session_state:
            return st.session_state[self.token_key]
        return None
    
    def store_token(self, token: dict):
        """Store token in session state"""
        st.session_state[self.token_key] = token
        logger.info("Google Drive token stored in session")
    
    def clear_token(self):
        """Clear stored token"""
        if self.token_key in st.session_state:
            del st.session_state[self.token_key]
        logger.info("Google Drive token cleared")
    
    def get_credentials(self) -> Optional[Credentials]:
        """Convert stored token to Google credentials"""
        token = self.get_stored_token()
        if not token:
            return None
            
        try:
            # Create credentials from token
            creds = Credentials(
                token=token.get('access_token'),
                refresh_token=token.get('refresh_token'),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=[DRIVE_SCOPE]
            )
            return creds
        except Exception as e:
            logger.error(f"Failed to create credentials: {e}")
            return None
    
    def get_drive_service(self):
        """Get authenticated Google Drive service"""
        creds = self.get_credentials()
        if not creds:
            return None
            
        try:
            service = build('drive', 'v3', credentials=creds)
            return service
        except Exception as e:
            logger.error(f"Failed to build Drive service: {e}")
            return None
    
    def is_authorized(self) -> bool:
        """Check if user has valid Drive authorization"""
        return self.get_stored_token() is not None


def show_google_drive_auth():
    """Show Google Drive authorization component"""
    auth = GoogleDriveOAuth()
    
    if auth.is_authorized():
        st.success("✅ Google Drive connected")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Drive Connection", width='stretch'):
                service = auth.get_drive_service()
                if service:
                    try:
                        # Test by listing files
                        results = service.files().list(
                            pageSize=1, 
                            fields="files(id, name)"
                        ).execute()
                        st.success("Drive connection working!")
                    except HttpError as e:
                        st.error(f"Drive test failed: {e}")
                else:
                    st.error("Could not connect to Drive")
        
        with col2:
            if st.button("Disconnect Google Drive", type="secondary", width='stretch'):
                auth.clear_token()
                st.rerun()
    
    else:
        st.warning("⚠️ Google Drive not connected")
        st.info("Connect Google Drive to automatically save your recipes and meal plans")
        
        # Get OAuth component
        oauth = auth.get_oauth_component()
        if not oauth:
            st.error("Google Drive OAuth not configured properly")
            return
        
        # Show authorization button
        result = oauth.authorize_button(
            name="Connect Google Drive",
            redirect_uri="http://localhost:8501/component/streamlit_oauth.authorize_button",
            scope=DRIVE_SCOPE,
            key="google_drive_auth",
            extras_params={"access_type": "offline", "prompt": "consent"},
            width='stretch',
            pkce='S256'  # Use PKCE for better security
        )
        
        # Handle the result
        if result:
            if 'token' in result:
                # Store the token
                auth.store_token(result['token'])
                st.success("✅ Google Drive connected successfully!")
                st.rerun()
            else:
                st.error("Authorization failed. Please try again.")


def get_google_drive_oauth() -> GoogleDriveOAuth:
    """Get singleton instance of GoogleDriveOAuth"""
    if 'google_drive_oauth_instance' not in st.session_state:
        st.session_state.google_drive_oauth_instance = GoogleDriveOAuth()
    return st.session_state.google_drive_oauth_instance