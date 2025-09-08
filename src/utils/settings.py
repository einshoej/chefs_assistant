"""
User settings management for Chef's Assistant
Handles saving and loading user preferences to/from Google Drive
"""

import streamlit as st
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def save_user_settings_to_drive() -> bool:
    """
    Save current user settings from session state to Google Drive
    
    Returns:
        True if successful, False otherwise
    """
    try:
        from src.data.google_drive_storage import get_google_drive_storage
        
        # Get Google Drive storage instance
        storage = get_google_drive_storage()
        if not storage:
            logger.warning("Google Drive not available for saving settings")
            return False
        
        # Prepare settings data from session state
        settings_data = {
            'meals_per_week': st.session_state.get('meals_per_week', 3)
        }
        
        # Save to Google Drive
        success = storage.save_user_settings(settings_data)
        if success:
            logger.info("Successfully saved user settings to Google Drive")
        else:
            logger.error("Failed to save user settings to Google Drive")
            
        return success
        
    except Exception as e:
        logger.error(f"Error saving user settings to Google Drive: {e}")
        return False


def load_user_settings_from_drive() -> bool:
    """
    Load user settings from Google Drive into session state
    
    Returns:
        True if settings were loaded, False if not found or error
    """
    try:
        from src.data.google_drive_storage import get_google_drive_storage
        
        # Get Google Drive storage instance
        storage = get_google_drive_storage()
        if not storage:
            logger.info("Google Drive not available for loading settings")
            return False
        
        # Load from Google Drive
        settings_data = storage.load_user_settings()
        if not settings_data:
            logger.info("No user settings found in Google Drive")
            return False
        
        # Apply settings to session state
        if 'meals_per_week' in settings_data:
            st.session_state.meals_per_week = settings_data['meals_per_week']
            logger.info(f"Loaded meals_per_week setting: {settings_data['meals_per_week']}")
        
        logger.info("Successfully loaded user settings from Google Drive")
        return True
        
    except Exception as e:
        logger.error(f"Error loading user settings from Google Drive: {e}")
        return False


def initialize_user_settings():
    """
    Initialize user settings in session state
    Load from Google Drive if available, otherwise use defaults
    """
    # Set default values first
    if 'meals_per_week' not in st.session_state:
        st.session_state.meals_per_week = 3
    
    # Try to load from Google Drive
    try:
        load_user_settings_from_drive()
    except Exception as e:
        logger.error(f"Error initializing user settings: {e}")
    
    logger.info(f"User settings initialized: meals_per_week={st.session_state.meals_per_week}")


def get_user_setting(key: str, default=None):
    """
    Get a user setting from session state with optional default
    
    Args:
        key: Setting key to retrieve
        default: Default value if key not found
        
    Returns:
        Setting value or default
    """
    return st.session_state.get(key, default)


def set_user_setting(key: str, value, save_to_drive: bool = True):
    """
    Set a user setting in session state and optionally save to Google Drive
    
    Args:
        key: Setting key to set
        value: Setting value to set
        save_to_drive: Whether to automatically save to Google Drive
    """
    st.session_state[key] = value
    
    if save_to_drive:
        save_user_settings_to_drive()