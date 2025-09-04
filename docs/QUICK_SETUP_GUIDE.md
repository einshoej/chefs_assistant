# Quick Setup Guide - Google Drive OAuth Fix

## What Changed
We've separated the OAuth callbacks to prevent conflicts:
- **Login**: Uses `/oauth2callback` (unchanged)
- **Google Drive**: Now uses `/drive_oauth2callback` (NEW)

## Steps to Configure

### 1. Update Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** > **Credentials**
4. Click on your OAuth 2.0 Client ID
5. In **Authorized redirect URIs**, add:
   ```
   http://localhost:8501/drive_oauth2callback
   ```
   Keep the existing `http://localhost:8501/oauth2callback` for login
6. Save the changes

### 2. Update Your Local Configuration

Edit `.streamlit/secrets.toml` and add the Google Drive section:

```toml
# Keep your existing [auth] section as-is

# Add this new section for Google Drive
[google_drive]
redirect_uri = "http://localhost:8501/drive_oauth2callback"
client_id = "your-client-id.apps.googleusercontent.com"  # Same as auth.client_id
client_secret = "your-client-secret"  # Same as auth.client_secret
```

### 3. Test the Setup

1. Restart your Streamlit app
2. Log in with Google (should work as before)
3. Go to **Settings** > **Google Drive Storage** tab
4. Click "Connect Google Drive"
5. Authorize access when prompted
6. You should see "✅ Google Drive connected"

## Production Deployment

For production (e.g., Streamlit Cloud), use your actual domain:
- Login: `https://yourdomain.streamlit.app/oauth2callback`
- Drive: `https://yourdomain.streamlit.app/drive_oauth2callback`

## Troubleshooting

### "Missing provider" error
- This should no longer occur with the separated callbacks
- If it still happens, ensure you're using the correct URLs

### "Redirect URI mismatch" error
- Double-check that you added `/drive_oauth2callback` in Google Cloud Console
- Ensure the URL matches exactly (http vs https, port number, etc.)

### Drive not connecting
- Check that the `[google_drive]` section exists in secrets.toml
- Verify client_id and client_secret are correct
- Try clearing browser cookies and re-authenticating

## How It Works

1. **Login Flow**: User clicks "Sign in with Google" → Goes to Google → Returns to `/oauth2callback` → Streamlit handles login
2. **Drive Flow**: User clicks "Connect Google Drive" → Goes to Google → Returns to `/drive_oauth2callback` → App stores Drive tokens
3. **Data Storage**: Once connected, recipes automatically save to user's personal Google Drive

## Benefits

- ✅ No more OAuth conflicts
- ✅ Users own their data in their personal Drive
- ✅ Can access recipes outside the app
- ✅ Can share recipe folders with family
- ✅ Automatic sync across devices