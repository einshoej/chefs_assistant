"""
Google OAuth token management for Drive API access
Separate from Streamlit auth to handle Drive-specific OAuth flow
"""

import streamlit as st
import json
import os
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveAuth:
    """Manages Google OAuth tokens for Drive API access"""
    
    def __init__(self):
        self.token_key = 'google_drive_token'
        self.creds_key = 'google_drive_creds'
        # Use different callback path to avoid conflict with Streamlit auth
        self.drive_redirect_uri = None
        
    def get_oauth_flow(self) -> Optional[Flow]:
        """Create OAuth flow from Streamlit secrets"""
        try:
            # Check for Drive-specific config first, then fall back to auth config
            if 'google_drive' in st.secrets:
                client_id = st.secrets.google_drive.get("client_id", st.secrets.auth.get("client_id"))
                client_secret = st.secrets.google_drive.get("client_secret", st.secrets.auth.get("client_secret"))
                # Use /drive_oauth2callback to avoid conflict with Streamlit auth
                base_url = st.secrets.google_drive.get("redirect_uri", "http://localhost:8501/drive_oauth2callback")
            elif 'auth' in st.secrets:
                client_id = st.secrets.auth.get("client_id")
                client_secret = st.secrets.auth.get("client_secret")
                # Change default to use /drive_oauth2callback
                base_url = "http://localhost:8501/drive_oauth2callback"
            else:
                logger.error("No auth configuration found in secrets")
                return None
            
            self.drive_redirect_uri = base_url
                
            client_config = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.drive_redirect_uri]
                }
            }
            
            flow = Flow.from_client_config(
                client_config,
                scopes=SCOPES,
                redirect_uri=self.drive_redirect_uri
            )
            
            return flow
            
        except Exception as e:
            logger.error(f"Failed to create OAuth flow: {e}")
            return None
    
    def get_stored_credentials(self) -> Optional[Credentials]:
        """Get stored credentials from session state"""
        if self.creds_key in st.session_state:
            try:
                creds_data = st.session_state[self.creds_key]
                creds = Credentials(
                    token=creds_data.get('token'),
                    refresh_token=creds_data.get('refresh_token'),
                    token_uri=creds_data.get('token_uri'),
                    client_id=creds_data.get('client_id'),
                    client_secret=creds_data.get('client_secret'),
                    scopes=creds_data.get('scopes')
                )
                
                # Check if token needs refresh
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self.store_credentials(creds)
                    
                return creds
                
            except Exception as e:
                logger.error(f"Failed to load stored credentials: {e}")
                del st.session_state[self.creds_key]
                
        return None
    
    def store_credentials(self, creds: Credentials):
        """Store credentials in session state"""
        try:
            creds_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            st.session_state[self.creds_key] = creds_data
            logger.info("Credentials stored in session state")
            
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
    
    def clear_credentials(self):
        """Clear stored credentials"""
        if self.creds_key in st.session_state:
            del st.session_state[self.creds_key]
        if self.token_key in st.session_state:
            del st.session_state[self.token_key]
    
    def get_authorization_url(self) -> Optional[str]:
        """Get OAuth authorization URL"""
        flow = self.get_oauth_flow()
        if not flow:
            return None
            
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store flow in session for later use
        st.session_state['google_oauth_flow'] = flow
        
        return auth_url
    
    def handle_oauth_callback(self, authorization_response: str) -> bool:
        """Handle OAuth callback and store credentials"""
        try:
            if 'google_oauth_flow' not in st.session_state:
                flow = self.get_oauth_flow()
                if not flow:
                    return False
            else:
                flow = st.session_state['google_oauth_flow']
            
            # Exchange authorization code for tokens
            flow.fetch_token(authorization_response=authorization_response)
            
            # Store credentials
            self.store_credentials(flow.credentials)
            
            # Clean up
            if 'google_oauth_flow' in st.session_state:
                del st.session_state['google_oauth_flow']
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle OAuth callback: {e}")
            return False
    
    def is_authorized(self) -> bool:
        """Check if user has valid Drive authorization"""
        creds = self.get_stored_credentials()
        return creds is not None and creds.valid
    
    def get_drive_service(self):
        """Get authenticated Google Drive service"""
        creds = self.get_stored_credentials()
        if not creds:
            return None
            
        try:
            service = build('drive', 'v3', credentials=creds)
            return service
        except Exception as e:
            logger.error(f"Failed to build Drive service: {e}")
            return None


def get_google_drive_auth() -> GoogleDriveAuth:
    """Get singleton instance of GoogleDriveAuth"""
    if 'google_drive_auth' not in st.session_state:
        st.session_state.google_drive_auth = GoogleDriveAuth()
    return st.session_state.google_drive_auth


def show_drive_authorization_component():
    """Show Google Drive authorization UI component"""
    auth = get_google_drive_auth()
    
    if auth.is_authorized():
        st.success("✅ Google Drive connected")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Drive Connection", use_container_width=True):
                service = auth.get_drive_service()
                if service:
                    try:
                        # Test by listing files
                        results = service.files().list(pageSize=1, fields="files(id, name)").execute()
                        st.success("Drive connection working!")
                    except Exception as e:
                        st.error(f"Drive test failed: {e}")
                else:
                    st.error("Could not connect to Drive")
        
        with col2:
            if st.button("Disconnect Google Drive", type="secondary", use_container_width=True):
                auth.clear_credentials()
                st.rerun()
                
    else:
        st.warning("⚠️ Google Drive not connected")
        st.info("Connect Google Drive to automatically save your recipes and meal plans")
        
        # Check for OAuth callback - look for Drive-specific callback
        query_params = st.query_params
        # Check if this is a Drive OAuth callback (has code parameter from Google)
        # Google returns to /drive_oauth2callback but Streamlit strips the path
        if 'code' in query_params:
            with st.spinner("Completing Google Drive authorization..."):
                # Build authorization response URL
                # Since Streamlit strips the path, we just use the current URL with params
                params_list = []
                for key in query_params:
                    value = query_params[key]
                    params_list.append(f"{key}={value}")
                
                # Use the root URL since that's where Google actually redirects
                auth_response = f"http://localhost:8501/?{'&'.join(params_list)}"
                
                if auth.handle_oauth_callback(auth_response):
                    st.success("✅ Google Drive connected successfully!")
                    # Clear query params
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.error("Failed to complete authorization")
        
        else:
            auth_url = auth.get_authorization_url()
            if auth_url:
                st.markdown(f"""
                ### Connect Google Drive
                
                Click the button below to authorize access to Google Drive:
                
                [🔗 Connect Google Drive]({auth_url})
                
                This will allow the app to:
                - Create a folder for your recipes
                - Save and load your recipes and meal plans
                - Keep your data synced across devices
                """)
            else:
                st.error("Could not generate authorization URL. Please check your configuration.")