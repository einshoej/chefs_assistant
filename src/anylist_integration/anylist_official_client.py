"""
AnyList Official Client - Python wrapper for the official Node.js anylist package
"""

import json
import subprocess
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AnyListOfficialClient:
    """Python wrapper for the official AnyList Node.js package"""
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """Initialize AnyList client"""
        self.email = email
        self.password = password
        self.logged_in = False
        self.nodejs_available = False
        
        # Path to Node.js bridge script
        self.bridge_dir = Path(__file__).parent / "nodejs"
        self.bridge_script = self.bridge_dir / "anylist_bridge.js"
        
        # Check if Node.js is installed
        try:
            self._check_nodejs()
            self.nodejs_available = True
            # Install npm dependencies if needed
            self._setup_npm_dependencies()
        except RuntimeError as e:
            logger.warning(f"Node.js not available: {e}")
            self.nodejs_available = False
    
    def _check_nodejs(self):
        """Check if Node.js is installed"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                check=False,
                shell=True  # Use shell=True on Windows to find node in PATH
            )
            if result.returncode != 0:
                raise RuntimeError("Node.js is not installed")
            logger.info("Node.js version: %s", result.stdout.strip())
        except FileNotFoundError:
            raise RuntimeError(
                "\n❌ Node.js is not installed or not in PATH!\n"
                "Please install Node.js first:\n"
                "1. Download Node.js from https://nodejs.org/\n"
                "2. Install it (npm comes with Node.js)\n"
                "3. Restart your terminal/IDE to update PATH\n"
                "4. Run the setup script: powershell src/scripts/setup/setup_nodejs_anylist.ps1"
            )
    
    def _setup_npm_dependencies(self):
        """Install npm dependencies if not already installed"""
        node_modules = self.bridge_dir / "node_modules"
        
        if not node_modules.exists():
            # First check if npm is available
            try:
                # Check if npm is installed
                npm_check = subprocess.run(
                    ["npm", "--version"],
                    capture_output=True,
                    text=True,
                    shell=True  # Use shell=True on Windows to find npm in PATH
                )
                if npm_check.returncode != 0:
                    raise FileNotFoundError("npm not found")
                    
                logger.info("Installing npm dependencies...")
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=str(self.bridge_dir),
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=True  # Use shell=True on Windows
                )
                logger.info("✅ npm dependencies installed successfully")
                
            except FileNotFoundError:
                error_msg = (
                    "\n❌ Node.js/npm is not installed or not in PATH!\n"
                    "Please install Node.js first:\n"
                    "1. Download Node.js from https://nodejs.org/\n"
                    "2. Install it (npm comes with Node.js)\n"
                    "3. Restart your terminal/IDE to update PATH\n"
                    "4. Run the setup script: powershell src/scripts/setup/setup_nodejs_anylist.ps1\n"
                    "Or manually run 'npm install' in src/anylist_integration/nodejs/"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            except subprocess.CalledProcessError as e:
                logger.error("Failed to install npm dependencies: %s", e.stderr)
                raise RuntimeError(f"Failed to install npm dependencies: {e.stderr}")
    
    def _run_bridge_command(self, command: str, *args) -> Dict:
        """Run a command through the Node.js bridge"""
        if not self.nodejs_available:
            logger.warning("Node.js is not available, cannot run AnyList commands")
            return {"success": False, "error": "Node.js is not available"}
        
        cmd = ["node", str(self.bridge_script), command] + list(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace any characters that can't be decoded
                check=False,
                shell=True  # Use shell=True on Windows to find node in PATH
            )
            
            # Parse JSON output from stdout
            if result.stdout:
                # Find the JSON part (it should be the last line containing valid JSON)
                lines = result.stdout.strip().split('\n')
                for line in reversed(lines):
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            return json.loads(line)
                        except json.JSONDecodeError:
                            continue
                
                # If no valid JSON found in stdout, check stderr
                if result.stderr:
                    # Try to find JSON in stderr
                    lines = result.stderr.strip().split('\n')
                    for line in reversed(lines):
                        line = line.strip()
                        if line.startswith('{') and line.endswith('}'):
                            try:
                                return json.loads(line)
                            except json.JSONDecodeError:
                                continue
                
                # Log for debugging
                if result.stdout:
                    logger.debug("Stdout (last 200 chars): %s", result.stdout[-200:])
                if result.stderr:
                    logger.debug("Stderr (last 200 chars): %s", result.stderr[-200:])
                
                return {"success": False, "error": "No valid JSON response from bridge"}
            
            return {"success": False, "error": "No response from bridge"}
            
        except subprocess.CalledProcessError as e:
            logger.error("Bridge command failed: %s", e)
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error("Unexpected error running bridge command: %s", e)
            return {"success": False, "error": str(e)}
    
    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Login to AnyList"""
        email = email or self.email
        password = password or self.password
        
        if not email or not password:
            logger.error("Email and password are required")
            return False
        
        logger.info("Logging in to AnyList...")
        result = self._run_bridge_command("login", email, password)
        
        if result.get("success"):
            self.logged_in = True
            self.email = email
            self.password = password
            logger.info("✅ %s", result.get("message", "Successfully logged in"))
            return True
        else:
            logger.error("Login failed: %s", result.get("error", "Unknown error"))
            return False
    
    def fetch_recipes(self, fetch_details: bool = True, progress_callback=None, max_recipes: Optional[int] = None) -> List[Dict]:
        """Fetch recipes from AnyList
        
        Args:
            fetch_details: Ignored (always fetches full details with official API)
            progress_callback: Optional callback function(current, total, message) for progress updates
            max_recipes: Optional maximum number of recipes to return
        """
        if not self.email or not self.password:
            logger.error("Must provide credentials to fetch recipes")
            return []
        
        logger.info("Fetching recipes from AnyList...")
        
        if progress_callback:
            progress_callback(0, 100, "Connecting to AnyList...")
        
        result = self._run_bridge_command("fetch-recipes", self.email, self.password)
        
        if result.get("success"):
            recipes = result.get("recipes", [])
            
            # Apply max_recipes limit if specified
            if max_recipes and len(recipes) > max_recipes:
                recipes = recipes[:max_recipes]
            
            # Post-process recipes to enhance photo information
            processed_recipes = []
            for recipe in recipes:
                processed_recipe = recipe.copy()
                
                # Enhance photo information
                photo = processed_recipe.get("photo", {})
                if photo.get("hasPhoto") and photo.get("source") == "constructed":
                    logger.debug("Recipe %s has constructed photo URLs: %s", 
                               recipe.get("name", "Unknown"), photo.get("urls", []))
                
                processed_recipes.append(processed_recipe)
            
            logger.info("✅ Successfully fetched %d recipes from AnyList", len(processed_recipes))
            recipes_with_photos = sum(1 for r in processed_recipes if r.get("photo", {}).get("hasPhoto"))
            logger.info("📸 %d recipes have photos", recipes_with_photos)
            
            if progress_callback:
                progress_callback(len(processed_recipes), len(processed_recipes), 
                                f"Successfully loaded {len(processed_recipes)} recipes ({recipes_with_photos} with photos)")
            
            return processed_recipes
        else:
            logger.error("Failed to fetch recipes: %s", result.get("error", "Unknown error"))
            return []
    
    def fetch_recipe_by_id(self, recipe_id: str) -> Optional[Dict]:
        """Fetch a specific recipe by ID"""
        if not self.email or not self.password:
            logger.error("Must provide credentials to fetch recipe")
            return None
        
        logger.info("Fetching recipe %s from AnyList...", recipe_id)
        result = self._run_bridge_command("fetch-recipe", self.email, self.password, recipe_id)
        
        if result.get("success"):
            return result.get("recipe")
        else:
            logger.error("Failed to fetch recipe: %s", result.get("error", "Unknown error"))
            return None
    
    def get_lists(self) -> List[Dict]:
        """Get shopping lists"""
        if not self.email or not self.password:
            logger.error("Must provide credentials to get lists")
            return []
        
        logger.info("Fetching lists from AnyList...")
        result = self._run_bridge_command("get-lists", self.email, self.password)
        
        if result.get("success"):
            lists = result.get("lists", [])
            logger.info("✅ Found %d lists", len(lists))
            return lists
        else:
            logger.error("Failed to fetch lists: %s", result.get("error", "Unknown error"))
            return []
    
    def get_recipe_collections(self) -> List[Dict]:
        """Get recipe collections/categories"""
        if not self.email or not self.password:
            logger.error("Must provide credentials to get collections")
            return []
        
        logger.info("Fetching recipe collections from AnyList...")
        result = self._run_bridge_command("get-collections", self.email, self.password)
        
        if result.get("success"):
            collections = result.get("collections", [])
            logger.info("✅ Found %d collections", len(collections))
            return collections
        else:
            logger.error("Failed to fetch collections: %s", result.get("error", "Unknown error"))
            return []
    

    def create_recipe(self, recipe_data: Dict) -> Optional[Dict]:
        """Create a new recipe"""
        if not self.email or not self.password:
            logger.error("Must provide credentials to create recipe")
            return None
        
        logger.info("Creating recipe: %s", recipe_data.get("name", "Unknown"))
        
        # Convert recipe data to JSON string for command line
        recipe_json = json.dumps(recipe_data)
        
        result = self._run_bridge_command("create-recipe", self.email, self.password, recipe_json)
        
        if result.get("success"):
            logger.info("✅ Successfully created recipe")
            return result.get("recipe")
        else:
            logger.error("Failed to create recipe: %s", result.get("error", "Unknown error"))
            return None
    
    def close(self):
        """Cleanup (no browser to close with official API)"""
        self.logged_in = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
