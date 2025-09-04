"""
Optional AnyList integration wrapper for cloud deployment compatibility
"""

import logging
from typing import Optional, List, Dict, Any
import streamlit as st

logger = logging.getLogger(__name__)

def is_nodejs_available() -> bool:
    """Check if Node.js is available for AnyList integration"""
    try:
        import subprocess
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=False,
            shell=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False

def get_anylist_client(email: Optional[str] = None, password: Optional[str] = None):
    """
    Get AnyList client if Node.js is available, otherwise return None
    
    Returns:
        AnyListOfficialClient or None if Node.js is not available
    """
    if is_nodejs_available():
        try:
            from src.anylist_integration.anylist_official_client import AnyListOfficialClient
            return AnyListOfficialClient(email, password)
        except Exception as e:
            logger.warning(f"Failed to initialize AnyList client: {e}")
            st.warning("AnyList integration is temporarily unavailable. The app will continue without recipe import functionality.")
            return None
    else:
        logger.info("Node.js not available - AnyList integration disabled")
        return None

class MockAnyListClient:
    """Mock client for when AnyList is not available"""
    
    def __init__(self):
        self.logged_in = False
    
    def login(self) -> bool:
        """Mock login"""
        return False
    
    def fetch_recipes(self, progress_callback=None) -> List[Dict[str, Any]]:
        """Return empty recipe list"""
        return []
    
    def get_recipe_collections(self) -> List[Dict[str, Any]]:
        """Return empty collections list"""
        return []
    
    def get_recipe_details(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Return None for any recipe request"""
        return None

def get_anylist_client_safe(email: Optional[str] = None, password: Optional[str] = None):
    """
    Safely get an AnyList client - returns real client if available, mock otherwise
    
    This ensures the app works even without Node.js/AnyList integration
    """
    client = get_anylist_client(email, password)
    if client is None:
        return MockAnyListClient()
    return client