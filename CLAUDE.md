# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Chef's Assistant is a Streamlit-based recipe management and meal planning application that integrates with AnyList for recipe importing. It uses Streamlit's native authentication system with Google OAuth and stores data in-memory via session state.

## Architecture

### Core Components

- **Frontend**: Streamlit with multi-page navigation using `st.navigation()`
- **Authentication**: Streamlit native auth system (`streamlit[auth]`) with Google OAuth
- **Backend**: Python with Node.js bridge for AnyList API integration
- **Storage**: Session-based storage (`st.session_state`) with optional Google Drive persistence
- **API Integration**: Official AnyList Node.js package wrapped by Python client

### Key Directories

- `src/pages/`: Streamlit pages organized by feature (this_week, browse_recipes, create_meals, etc.)
- `src/anylist_integration/`: AnyList API client and Node.js bridge
- `src/utils/`: Authentication utilities and helpers
- `src/models/`: Data models (meal planning, recipes)
- `docs/`: Setup guides and integration documentation

### Application Flow

1. Authentication check via `src/utils/auth.py`
2. Multi-page navigation with icon-based menu
3. Session state management for recipes and meal plans
4. AnyList integration through Node.js subprocess bridge

## Development Commands

### Setup and Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up authentication (interactive)
python setup_auth.py

# Set up Node.js dependencies for AnyList integration
powershell src/scripts/setup/setup_nodejs_anylist.ps1
# Or manually:
cd src/anylist_integration/nodejs && npm install
```

### Running the Application
```bash
# Start the Streamlit app
streamlit run main.py

# Run with specific port
streamlit run main.py --server.port 8501
```

### Testing
```bash
# Run specific test files
python src/scripts/tests/test_anylist_recipes_fetch.py
python src/scripts/tests/test_google_drive_setup.py
python src/scripts/tests/test_mashed_cauliflower_data.py
```

## Authentication Setup

The application requires Google OAuth configuration:

1. Install `streamlit[auth]` (included in requirements.txt)
2. Set up Google Cloud Console OAuth credentials
3. Configure `.streamlit/secrets.toml` with:
   - `client_id`: Google OAuth client ID
   - `client_secret`: Google OAuth client secret
   - `cookie_secret`: Random 32-byte token for session cookies
   - Redirect URI: `http://localhost:8501/oauth2callback`

Authentication utilities in `src/utils/auth.py` handle login state and user info access.

## AnyList Integration

### Node.js Bridge Architecture

The AnyList integration uses a Python-to-Node.js bridge:

- Python client: `src/anylist_integration/anylist_official_client.py`
- Node.js bridge: `src/anylist_integration/nodejs/anylist_bridge.js`
- Communication via subprocess with JSON messaging

### AnyList Client Usage

```python
from src.anylist_integration.anylist_official_client import AnyListOfficialClient

client = AnyListOfficialClient(email, password)
recipes = client.fetch_recipes()
collections = client.get_recipe_collections()
```

## Data Flow

1. **Recipe Loading**: AnyList recipes fetched via Node.js bridge, stored in `st.session_state.anylist_recipes`
2. **Meal Planning**: Weekly meal plans stored in `st.session_state.meal_plans`
3. **Session Management**: Data stored in session state with optional Google Drive persistence
4. **User State**: Authentication state managed by Streamlit auth system
5. **Google Drive Storage**: Optional cloud persistence for recipes and meal plans
   - Automatic save when recipes are synced or meal plans modified
   - Automatic load on app startup if Drive is connected
   - Separate OAuth flow for Drive API access (`src/utils/google_auth.py`)

## Page Structure

Each page follows the pattern:
- `src/pages/{feature}/main.py` - Main page logic
- `src/pages/{feature}/session_state.py` - Session state management
- `src/pages/{feature}/{feature}_components.py` - UI components

## Key Dependencies

- `streamlit[auth]>=1.37.0` - Core framework with authentication
- `google-*` packages - Google OAuth and Drive integration
- Node.js with `anylist` package - Recipe API integration
- `cryptography` - Credential encryption

## Development Rules (from .cursor/rules)

**Always Apply:**
1. Never test your work
2. Never create a new streamlit session
3. Use streamlit native code and elements, not HTML
4. Never create `__init__` files

**Page Structure:**
- Use absolute imports, never relative imports
- Standard page structure: heading → filters → metrics → tabs
- Use `st.title`, `st.header`, `st.subheader` for headings
- Use `st.markdown` for regular text, `st.caption` for explanatory text
- Use `st.divider()` instead of markdown horizontal lines
- Never add streamlit page config unless specifically instructed

**UI Guidelines:**
- Never use inline icons with markdown unless specifically instructed
- Use streamlit native text formatting when possible

## Development Notes

- Primary storage in `st.session_state` with optional Google Drive persistence
- Authentication required for all pages except login
- Google Drive requires separate OAuth authorization after login
- Node.js must be installed for AnyList integration
- Windows-specific shell commands in subprocess calls
- Progress callbacks supported for long-running operations