"""
Check for Node.js availability in the environment
"""

import subprocess
import os
import logging

logger = logging.getLogger(__name__)


def is_nodejs_available():
    """
    Check if Node.js is available in the current environment.
    
    Returns:
        bool: True if Node.js is available, False otherwise
    """
    try:
        # Try to run node --version
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=False,
            shell=True if os.name == 'nt' else False,  # Use shell on Windows
            timeout=5  # Add timeout to prevent hanging
        )
        
        if result.returncode == 0:
            logger.info(f"Node.js is available: {result.stdout.strip()}")
            return True
        else:
            logger.warning("Node.js command found but returned error")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        logger.warning(f"Node.js is not available: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking for Node.js: {e}")
        return False


def get_nodejs_status_message():
    """
    Get a user-friendly message about Node.js availability.
    
    Returns:
        tuple: (is_available: bool, message: str)
    """
    if is_nodejs_available():
        return True, "✅ Node.js is installed - AnyList sync is available"
    else:
        # Check if we're in Streamlit Cloud
        if os.getenv('STREAMLIT_CLOUD_ENVIRONMENT') or os.getenv('STREAMLIT_RUNTIME_ENVIRONMENT'):
            return False, (
                "⚠️ Running on Streamlit Cloud - AnyList sync is not available.\n"
                "You can still use the app to manage recipes manually.\n"
                "For full functionality including AnyList sync, run the app locally."
            )
        else:
            return False, (
                "⚠️ Node.js is not installed - AnyList sync is disabled.\n"
                "To enable AnyList sync, install Node.js from https://nodejs.org/\n"
                "You can still use the app to manage recipes manually."
            )