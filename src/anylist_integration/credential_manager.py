"""
Secure credential storage for AnyList integration
Uses encryption to protect stored credentials
"""

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Optional, Dict
import streamlit as st
import logging

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manages secure storage of AnyList credentials"""
    
    def __init__(self):
        """Initialize credential manager"""
        self.data_dir = Path("src/data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.creds_file = self.data_dir / "anylist_creds.json"
        self.key_file = self.data_dir / ".encryption_key"
        
        # Initialize or load encryption key
        self.cipher = self._get_cipher()
    
    def _get_cipher(self) -> Fernet:
        """Get or create encryption cipher"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions on key file
            if os.name != 'nt':  # Unix-like systems
                os.chmod(self.key_file, 0o600)
        
        return Fernet(key)
    
    def save_credentials(self, username: str, email: str, password: str) -> bool:
        """Save encrypted credentials for a user"""
        try:
            # Load existing credentials
            creds = self._load_all_credentials()
            
            # Encrypt the password
            encrypted_password = self.cipher.encrypt(password.encode()).decode()
            
            # Store credentials
            creds[username] = {
                'email': email,
                'password': encrypted_password,
                'anylist_enabled': True
            }
            
            # Save to file
            with open(self.creds_file, 'w') as f:
                json.dump(creds, f, indent=2)
            
            logger.info(f"Saved AnyList credentials for user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            return False
    
    def get_credentials(self, username: str) -> Optional[Dict]:
        """Get decrypted credentials for a user"""
        try:
            creds = self._load_all_credentials()
            
            if username not in creds:
                return None
            
            user_creds = creds[username].copy()
            
            # Decrypt the password
            if 'password' in user_creds:
                encrypted_password = user_creds['password'].encode()
                user_creds['password'] = self.cipher.decrypt(encrypted_password).decode()
            
            return user_creds
            
        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            return None
    
    def remove_credentials(self, username: str) -> bool:
        """Remove credentials for a user"""
        try:
            creds = self._load_all_credentials()
            
            if username in creds:
                del creds[username]
                
                with open(self.creds_file, 'w') as f:
                    json.dump(creds, f, indent=2)
                
                logger.info(f"Removed AnyList credentials for user: {username}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing credentials: {e}")
            return False
    
    def has_credentials(self, username: str) -> bool:
        """Check if credentials exist for a user"""
        creds = self._load_all_credentials()
        return username in creds
    
    def _load_all_credentials(self) -> Dict:
        """Load all stored credentials"""
        if not self.creds_file.exists():
            return {}
        
        try:
            with open(self.creds_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading credentials file: {e}")
            return {}
    
    def is_anylist_enabled(self, username: str) -> bool:
        """Check if AnyList integration is enabled for user"""
        creds = self.get_credentials(username)
        return creds.get('anylist_enabled', False) if creds else False


def get_credential_manager() -> CredentialManager:
    """Get or create credential manager instance in session state"""
    if 'credential_manager' not in st.session_state:
        st.session_state.credential_manager = CredentialManager()
    return st.session_state.credential_manager

