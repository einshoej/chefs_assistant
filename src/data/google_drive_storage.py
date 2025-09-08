"""
Google Drive Storage for Recipe Calendar App
Stores user recipes in their personal Google Drive
"""

import json
import io
import logging
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleDriveRecipeStorage:
    """Store and retrieve user recipes from their Google Drive"""
    
    def __init__(self, access_token: str = None, service=None):
        """
        Initialize Google Drive storage with user's access token or service
        
        Args:
            access_token: OAuth2 access token from Streamlit authentication (deprecated)
            service: Pre-built Google Drive service object
        """
        self.service = service
        self.folder_name = "Recipe Calendar App Data"
        self.recipes_file = "recipes.json"
        self.weekly_recipes_file = "weekly_recipes.json"
        self.meal_plans_file = "meal_plans.json"
        
        if access_token and not service:
            self._initialize_service(access_token)
    
    def _initialize_service(self, access_token: str):
        """Initialize Google Drive API service with user credentials"""
        try:
            # Create credentials from access token
            creds = Credentials(token=access_token)
            
            # Build the Drive service
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Google Drive service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            raise
    
    def get_or_create_app_folder(self) -> Optional[str]:
        """
        Get or create the app's data folder in user's Google Drive
        
        Returns:
            Folder ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return None
        
        try:
            # Search for existing folder
            query = f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                folder_id = folders[0]['id']
                logger.info(f"Found existing app folder: {folder_id}")
                return folder_id
            else:
                # Create new folder
                file_metadata = {
                    'name': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                
                folder_id = folder.get('id')
                logger.info(f"Created new app folder: {folder_id}")
                return folder_id
                
        except HttpError as e:
            logger.error(f"Google Drive API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error accessing/creating app folder: {e}")
            return None
    
    def save_recipes(self, recipes_data: Dict) -> bool:
        """
        Save recipes to user's Google Drive
        
        Args:
            recipes_data: Dictionary containing recipes and metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return False
        
        try:
            folder_id = self.get_or_create_app_folder()
            if not folder_id:
                return False
            
            # Add timestamp
            recipes_data['last_updated'] = datetime.now().isoformat()
            
            # Convert to JSON
            json_data = json.dumps(recipes_data, indent=2, ensure_ascii=False)
            
            # Check if file exists
            query = f"name='{self.recipes_file}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            # Prepare media upload
            media = MediaIoBaseUpload(
                io.BytesIO(json_data.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            if files:
                # Update existing file
                file_id = files[0]['id']
                updated_file = self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
                logger.info(f"Updated recipes file: {file_id}")
            else:
                # Create new file
                file_metadata = {
                    'name': self.recipes_file,
                    'parents': [folder_id],
                    'mimeType': 'application/json'
                }
                
                new_file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Created new recipes file: {new_file.get('id')}")
            
            return True
            
        except HttpError as e:
            logger.error(f"Google Drive API error while saving recipes: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving recipes to Google Drive: {e}")
            return False
    
    def load_recipes(self) -> Optional[Dict]:
        """
        Load recipes from user's Google Drive
        
        Returns:
            Dictionary containing recipes and metadata, or None if not found/error
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return None
        
        try:
            folder_id = self.get_or_create_app_folder()
            if not folder_id:
                return None
            
            # Find recipes file
            query = f"name='{self.recipes_file}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                file_id = files[0]['id']
                modified_time = files[0].get('modifiedTime', '')
                
                # Download file content
                request = self.service.files().get_media(fileId=file_id)
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.debug(f"Download progress: {int(status.progress() * 100)}%")
                
                # Parse JSON
                file_content.seek(0)
                recipes_data = json.loads(file_content.read().decode('utf-8'))
                
                logger.info(f"Loaded recipes from Google Drive (modified: {modified_time})")
                return recipes_data
            else:
                logger.info("No recipes file found in Google Drive")
                return {
                    'local_recipes': [],
                    'last_updated': None
                }
                
        except HttpError as e:
            logger.error(f"Google Drive API error while loading recipes: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing recipes JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading recipes from Google Drive: {e}")
            return None
    
    def save_weekly_recipes(self, weekly_recipes_data: Dict) -> bool:
        """
        Save weekly recipes to user's Google Drive
        
        Args:
            weekly_recipes_data: Dictionary containing weekly recipes data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return False
        
        try:
            folder_id = self.get_or_create_app_folder()
            if not folder_id:
                return False
            
            # Add timestamp
            weekly_recipes_data['last_updated'] = datetime.now().isoformat()
            
            # Convert to JSON
            json_data = json.dumps(weekly_recipes_data, indent=2, ensure_ascii=False)
            
            # Check if file exists
            query = f"name='{self.weekly_recipes_file}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            # Prepare media upload
            media = MediaIoBaseUpload(
                io.BytesIO(json_data.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            if files:
                # Update existing file
                file_id = files[0]['id']
                self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
                logger.info(f"Updated weekly recipes file: {file_id}")
            else:
                # Create new file
                file_metadata = {
                    'name': self.weekly_recipes_file,
                    'parents': [folder_id],
                    'mimeType': 'application/json'
                }
                
                new_file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Created new weekly recipes file: {new_file.get('id')}")
            
            return True
            
        except HttpError as e:
            logger.error(f"Google Drive API error while saving weekly recipes: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving weekly recipes to Google Drive: {e}")
            return False
    
    def load_weekly_recipes(self) -> Optional[Dict]:
        """
        Load weekly recipes from user's Google Drive
        
        Returns:
            Dictionary containing weekly recipes data, or None if not found/error
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return None
        
        try:
            folder_id = self.get_or_create_app_folder()
            if not folder_id:
                return None
            
            # Find weekly recipes file
            query = f"name='{self.weekly_recipes_file}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                file_id = files[0]['id']
                
                # Download file content
                request = self.service.files().get_media(fileId=file_id)
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                # Parse JSON
                file_content.seek(0)
                weekly_recipes_data = json.loads(file_content.read().decode('utf-8'))
                
                logger.info("Loaded weekly recipes from Google Drive")
                return weekly_recipes_data
            else:
                logger.info("No weekly recipes file found in Google Drive")
                return {
                    'current_week': [],
                    'weekly_plans': {},
                    'last_updated': None
                }
                
        except HttpError as e:
            logger.error(f"Google Drive API error while loading weekly recipes: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing weekly recipes JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading weekly recipes from Google Drive: {e}")
            return None
    
    def save_meal_plans(self, meal_plans_data: Dict) -> bool:
        """
        Save meal plans to user's Google Drive
        
        Args:
            meal_plans_data: Dictionary containing meal plans data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return False
        
        try:
            folder_id = self.get_or_create_app_folder()
            if not folder_id:
                return False
            
            # Add timestamp
            meal_plans_data['last_updated'] = datetime.now().isoformat()
            
            # Convert to JSON
            json_data = json.dumps(meal_plans_data, indent=2, ensure_ascii=False)
            
            # Check if file exists
            query = f"name='{self.meal_plans_file}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            # Prepare media upload
            media = MediaIoBaseUpload(
                io.BytesIO(json_data.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            if files:
                # Update existing file
                file_id = files[0]['id']
                self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
                logger.info(f"Updated meal plans file: {file_id}")
            else:
                # Create new file
                file_metadata = {
                    'name': self.meal_plans_file,
                    'parents': [folder_id],
                    'mimeType': 'application/json'
                }
                
                new_file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Created new meal plans file: {new_file.get('id')}")
            
            return True
            
        except HttpError as e:
            logger.error(f"Google Drive API error while saving meal plans: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving meal plans to Google Drive: {e}")
            return False
    
    def load_meal_plans(self) -> Optional[Dict]:
        """
        Load meal plans from user's Google Drive
        
        Returns:
            Dictionary containing meal plans data, or None if not found/error
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return None
        
        try:
            folder_id = self.get_or_create_app_folder()
            if not folder_id:
                return None
            
            # Find meal plans file
            query = f"name='{self.meal_plans_file}' and '{folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                file_id = files[0]['id']
                
                # Download file content
                request = self.service.files().get_media(fileId=file_id)
                file_content = io.BytesIO()
                downloader = MediaIoBaseDownload(file_content, request)
                
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                
                # Parse JSON
                file_content.seek(0)
                meal_plans_data = json.loads(file_content.read().decode('utf-8'))
                
                logger.info("Loaded meal plans from Google Drive")
                return meal_plans_data
            else:
                logger.info("No meal plans file found in Google Drive")
                return {
                    'weekly_plans': {},
                    'last_updated': None
                }
                
        except HttpError as e:
            logger.error(f"Google Drive API error while loading meal plans: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing meal plans JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading meal plans from Google Drive: {e}")
            return None
    
    def delete_all_data(self) -> bool:
        """
        Delete all app data from user's Google Drive (for cleanup/reset)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Drive service not initialized")
            return False
        
        try:
            # Find app folder
            query = f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                folder_id = folders[0]['id']
                
                # Move folder to trash (safer than permanent deletion)
                self.service.files().update(
                    fileId=folder_id,
                    body={'trashed': True}
                ).execute()
                
                logger.info(f"Moved app folder to trash: {folder_id}")
                return True
            else:
                logger.info("No app folder found to delete")
                return True
                
        except HttpError as e:
            logger.error(f"Google Drive API error while deleting data: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting app data from Google Drive: {e}")
            return False


# Helper function to get storage instance from Streamlit session
def get_google_drive_storage() -> Optional[GoogleDriveRecipeStorage]:
    """
    Get Google Drive storage instance using current user's credentials
    
    Returns:
        GoogleDriveRecipeStorage instance if user is logged in, None otherwise
    """
    from src.utils.google_drive_oauth import get_google_drive_oauth
    from src.utils.auth import is_user_logged_in
    
    # Check if user is logged into the app
    if not is_user_logged_in():
        logger.warning("User not logged in to app, cannot access Google Drive")
        return None
    
    # Get Google Drive OAuth manager (using streamlit-oauth)
    auth = get_google_drive_oauth()
    
    # Check if user has authorized Google Drive
    if not auth.is_authorized():
        logger.info("Google Drive not authorized yet")
        return None
    
    # Get Drive service
    service = auth.get_drive_service()
    if not service:
        logger.error("Could not get Google Drive service")
        return None
    
    try:
        # Create storage instance with service
        storage = GoogleDriveRecipeStorage()
        storage.service = service
        return storage
    except Exception as e:
        logger.error(f"Failed to initialize Google Drive storage: {e}")
        return None

