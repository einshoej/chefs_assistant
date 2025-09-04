# Google Drive Storage Implementation

## Overview
This document describes the Google Drive storage implementation for Chef's Assistant, which allows users to save their imported recipes and meal plans to their Google account.

## Implementation Summary

### Architecture
The implementation uses a **dual OAuth approach with separated callbacks**:
1. **Streamlit Native Auth**: For user login at `/oauth2callback`
2. **Separate Google Drive OAuth**: For Drive API access at `/drive_oauth2callback`

This separation prevents conflicts between Streamlit's auth handler and Drive authorization, allowing both to work independently.

### Key Components

#### 1. OAuth Token Management (`src/utils/google_auth.py`)
- `GoogleDriveAuth` class manages OAuth tokens for Drive API access
- Handles OAuth flow, token storage, and refresh
- Stores credentials in encrypted session state
- Provides `show_drive_authorization_component()` for UI integration

#### 2. Storage Integration (`src/data/google_drive_storage.py`)
- `GoogleDriveRecipeStorage` class handles all Drive operations
- Updated to use the new token management system
- Supports saving/loading:
  - Recipes (`recipes.json`)
  - Weekly recipes (`weekly_recipes.json`)
  - Meal plans (`meal_plans.json`)

#### 3. Storage Hooks

##### Browse Recipes Page (`src/pages/browse_recipes/session_state.py`)
- `load_recipes_from_drive()`: Automatically loads on app startup
- `save_recipes_to_drive()`: Called after AnyList sync

##### This Week Page (`src/pages/this_week/session_manager.py`)
- `WeeklyRecipeManager.save_to_drive()`: Auto-saves on changes
- Hooks in `add_recipe()`, `remove_recipe()`, `clear_all()`

##### Settings Page (`src/pages/anylist_settings/main.py`)
- New "Google Drive Storage" tab
- Authorization UI component
- Manual save/load buttons
- Storage status display

### Data Flow

1. **User Login**: User signs in with Google (Streamlit auth)
2. **Drive Authorization**: User optionally connects Google Drive (separate OAuth)
3. **Automatic Loading**: On app start, recipes load from Drive if connected
4. **Automatic Saving**: 
   - When recipes are synced from AnyList
   - When meal plans are modified
   - When weekly recipes are changed
5. **Manual Controls**: Available in Settings for explicit save/load

## User Experience

### First-Time Setup
1. User logs into the app with Google
2. Navigates to Settings → Google Drive Storage
3. Clicks "Connect Google Drive" link
4. Authorizes app to access Drive
5. App automatically creates "Recipe Calendar App Data" folder

### Daily Usage
- Data automatically loads from Drive on login
- Changes save automatically in the background
- No manual intervention needed

### Features
- ✅ Automatic sync across devices
- ✅ Cloud backup of all recipes and meal plans
- ✅ Works with existing Google login
- ✅ Separate Drive authorization (optional)
- ✅ Manual save/load controls
- ✅ Clear Drive data option

## Technical Details

### Storage Format
All data is stored as JSON files in the user's Google Drive:

```
Recipe Calendar App Data/
├── recipes.json          # AnyList and local recipes
├── weekly_recipes.json   # Current week's selected recipes
└── meal_plans.json       # Historical meal plans
```

### Security
- OAuth tokens stored in encrypted session state
- Drive API uses least-privilege scope (`drive.file`)
- App only accesses files it creates
- No server-side storage of user data

### Error Handling
- Graceful fallback to session-only storage if Drive unavailable
- Automatic token refresh for expired credentials
- Clear error messages for authorization issues

## Configuration

### Required Scopes
The app requires the following Google OAuth scopes:
- `openid email profile` (for Streamlit auth)
- `https://www.googleapis.com/auth/drive.file` (for Drive storage)

### Secrets Configuration
Update `.streamlit/secrets.toml`:
```toml
[auth]
# For Streamlit login
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-secret-here"
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
client_kwargs = { scope = "openid email profile" }

[google_drive]
# For Drive API access (separate from login)
redirect_uri = "http://localhost:8501/drive_oauth2callback"
client_id = "your-client-id.apps.googleusercontent.com"  # Can be same as auth
client_secret = "your-client-secret"  # Can be same as auth
```

**Google Cloud Console Setup**:
Add BOTH redirect URIs to your OAuth 2.0 Client:
- `http://localhost:8501/oauth2callback` (for login)
- `http://localhost:8501/drive_oauth2callback` (for Drive)

## Testing

### Manual Testing Steps
1. Start the app: `streamlit run main.py`
2. Sign in with Google
3. Go to Settings → Google Drive Storage
4. Connect Google Drive
5. Sync recipes from AnyList
6. Verify files appear in Google Drive
7. Add recipes to weekly plan
8. Restart app and verify data persists

### Automated Tests
Run: `python src/scripts/tests/test_google_drive_setup.py`

## Known Limitations

1. **Separate Authorization**: Users must authorize Drive separately from login
2. **Token Storage**: OAuth tokens only persist for the session
3. **Redirect URI**: Must match exactly in Google Console and config

## Future Enhancements

1. **Persistent Token Storage**: Save refresh tokens securely
2. **Automatic Authorization**: Prompt for Drive on first AnyList sync
3. **Selective Sync**: Choose which data to save to Drive
4. **Sharing**: Share recipe folders with family members
5. **Offline Support**: Cache data locally with sync on reconnect