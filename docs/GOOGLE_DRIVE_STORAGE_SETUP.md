# Google Drive Storage Setup for Recipe Calendar App

## Overview
The Recipe Calendar App now supports storing your recipes and meal plans directly in your Google Drive! This means:
- 🔒 **Private Storage**: Your recipes are stored in YOUR Google Drive account
- ☁️ **Cloud Backup**: Never lose your recipes - they're safely backed up
- 🔄 **Sync Across Devices**: Access your recipes from any device
- 👨‍👩‍👧‍👦 **Family Sharing**: Easily share your recipe folder with family members

## How It Works
When you sign in with Google, the app creates a folder called "Recipe Calendar App Data" in your Google Drive and stores:
- `recipes.json` - All your AnyList and local recipes
- `meal_plans.json` - Your weekly meal plans

## Setup Instructions

### 1. Update Google OAuth Permissions

#### For New Users:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **OAuth consent screen**
4. Add the scope: `https://www.googleapis.com/auth/drive.file`
5. Save changes

#### For Existing Users:
You'll need to re-authenticate to grant Drive permissions:
1. Sign out of the app
2. Sign in again
3. Google will ask for permission to access your Drive files
4. Click "Allow"

### 2. Update Your App Configuration

Add a Google Drive section to your `.streamlit/secrets.toml` file:

```toml
[auth]
# Keep your existing auth configuration for login
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-existing-secret"
client_id = "your-existing-client-id"
client_secret = "your-existing-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
client_kwargs = { scope = "openid email profile" }

# Add this new section for Google Drive
[google_drive]
redirect_uri = "http://localhost:8501/drive_oauth2callback"
client_id = "your-client-id"  # Can be same as auth.client_id
client_secret = "your-client-secret"  # Can be same as auth.client_secret
```

**IMPORTANT**: You must add the new redirect URI to your Google Cloud Console:
1. Go to your OAuth 2.0 Client ID settings
2. Add `http://localhost:8501/drive_oauth2callback` to Authorized redirect URIs
3. For production, use your actual domain instead of localhost:8501

### 3. Install Required Dependencies

Run the following command to install Google Drive API libraries:

```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

### 4. Test the Integration

1. Run the app: `streamlit run main.py`
2. Sign in with Google
3. Navigate to Browse Recipes
4. Your recipes will automatically save to Google Drive
5. Check your Google Drive for the "Recipe Calendar App Data" folder

## Features

### Automatic Sync
- Recipes are automatically loaded from Google Drive when you open the app
- Any changes to your meal plan are instantly saved
- AnyList sync results are saved to Drive automatically

### Data Management
- **View in Drive**: Open Google Drive and navigate to "Recipe Calendar App Data"
- **Backup**: Your data is automatically backed up by Google
- **Delete Data**: Remove the folder from Drive to reset all app data
- **Share**: Share the folder with family members to share recipes

## Troubleshooting

### "Could not load recipes from Google Drive"
- Make sure you're signed in with Google
- Check that you've granted Drive permissions
- Try signing out and back in

### "Google Drive save failed"
- Check your internet connection
- Verify you have storage space in Google Drive
- Try refreshing the page

### "No access token found"
- Sign out and sign back in
- Clear browser cookies and try again

## Privacy & Security

- **Your Data, Your Control**: All recipes are stored in YOUR Google Drive
- **App Permissions**: The app only accesses files it creates (not your other Drive files)
- **Encryption**: Data is encrypted in transit using HTTPS
- **No Server Storage**: We don't store your recipes on our servers

## Data Structure

Your recipes are stored in JSON format:

```json
{
  "anylist_recipes": [...],
  "local_recipes": [...],
  "last_sync": "2024-01-20 10:30:00",
  "last_updated": "2024-01-20T10:30:00"
}
```

Meal plans are stored separately:

```json
{
  "current_week": [...],
  "weekly_plans": {
    "2024-W03": {...}
  },
  "last_updated": "2024-01-20T10:30:00"
}
```

## Advanced Usage

### Manual Backup
1. Open Google Drive
2. Find "Recipe Calendar App Data" folder
3. Right-click and select "Download"
4. You'll get a ZIP file with all your recipes

### Restore from Backup
1. Delete the existing folder in Drive
2. Upload your backup JSON files to a new "Recipe Calendar App Data" folder
3. Refresh the app

### Share with Family
1. Open the "Recipe Calendar App Data" folder in Drive
2. Click "Share"
3. Add family members' email addresses
4. They can now access the same recipes when they use the app

## FAQ

**Q: How much storage does this use?**
A: Very little! Even with thousands of recipes, the JSON files are typically under 1MB.

**Q: Can I edit recipes directly in Google Drive?**
A: Yes, but be careful with JSON formatting. It's safer to edit through the app.

**Q: What happens if I'm offline?**
A: The app uses session storage as a fallback. Changes will sync when you're back online.

**Q: Can I use this with multiple Google accounts?**
A: Yes! Each Google account has its own separate recipe storage.

## Support

For issues or questions about Google Drive storage:
1. Check this documentation
2. Review the [main setup guide](STREAMLIT_NATIVE_AUTH_SETUP.md)
3. Check your browser's console for error messages
4. Ensure all dependencies are installed correctly

