# Streamlit Cloud Secrets Configuration

## IMPORTANT: Add These Secrets to Your Streamlit Cloud App

Your app at https://chefsassistant.streamlit.app/ needs the following secrets to enable Google OAuth authentication.

### Step 1: Access Your App Settings

1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io)
2. Find your app "chefsassistant"
3. Click the three dots menu (⋮) → **Settings**
4. Click **Secrets** in the left sidebar

### Step 2: Copy and Paste This Entire Configuration

**IMPORTANT**: Replace the placeholder values with your actual Google OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials), then copy this EXACTLY as shown - do not modify any formatting!

```toml
[auth]
redirect_uri = "https://chefsassistant.streamlit.app/oauth2callback"
cookie_secret = "YOUR_GENERATED_COOKIE_SECRET_HERE"
client_id = "YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_GOOGLE_OAUTH_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[google_drive]
client_id = "YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_GOOGLE_OAUTH_CLIENT_SECRET"
redirect_uri = "https://chefsassistant.streamlit.app/drive_oauth2callback"
```

**Note**: The configuration above is simplified to avoid any TOML parsing issues. The comments have been removed and the `client_kwargs` line has been omitted as it uses default values.

### Step 3: Save and Restart

1. Click **Save** in the Streamlit Cloud secrets editor
2. Your app will automatically restart
3. Wait about 1-2 minutes for the restart to complete

### Step 4: Verify Google Cloud Console Settings

Make sure these URIs are added in your [Google Cloud Console OAuth Client](https://console.cloud.google.com/apis/credentials):

**Authorized redirect URIs:**
- `https://chefsassistant.streamlit.app/oauth2callback`
- `https://chefsassistant.streamlit.app/drive_oauth2callback`

### Step 5: Test Your App

1. Go to https://chefsassistant.streamlit.app/
2. You should now see the "Sign in with Google" button
3. Click it to test the OAuth flow

## Troubleshooting

### If you see "StreamlitAuthError" or "Authentication is not configured":

This error means the secrets aren't being read properly. Here's how to fix it:

1. **Verify Secrets Are Saved**:
   - Go back to Settings → Secrets in Streamlit Cloud
   - Make sure the configuration is there
   - Click "Save" again even if it looks saved
   - Wait for the app to restart (check the logs)

2. **Check App Logs**:
   - In Streamlit Cloud, click "Manage app" → "View logs"
   - Look for any TOML parsing errors
   - If you see parsing errors, remove all comments from the configuration

3. **Ensure Proper Format**:
   - The configuration must start with `[auth]` on the first line
   - No extra spaces or tabs before `[auth]`
   - Each key-value pair should be on its own line
   - No trailing commas or semicolons

4. **Force Restart**:
   - In Streamlit Cloud dashboard, click "Manage app"
   - Click "Reboot app"
   - Wait 2-3 minutes for full restart

### If you still see "Authentication is not configured" after adding secrets:
- Clear your browser cache completely
- Try in an incognito/private window
- Make sure you're not looking at a cached version of the app

### If you get "redirect_uri_mismatch":
- Double-check the URIs in Google Cloud Console match exactly
- The production URI must be `https://` (not `http://`)
- Wait 5 minutes for Google's changes to propagate

### If login works but you can't access the app:
- Clear your browser cookies for the streamlit.app domain
- Try in an incognito/private window

## Security Note

The cookie_secret provided here is unique and secure. However, for maximum security, you can generate your own:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then replace the `cookie_secret` value in the configuration above.

## Additional Features

### Google Drive Storage
To enable Google Drive storage for recipes:
1. The `[google_drive]` section is already included above
2. Users can connect their Drive from Settings → Google Drive Storage

---

**Last Updated:** January 8, 2025
**App URL:** https://chefsassistant.streamlit.app/
**Client ID:** YOUR_GOOGLE_OAUTH_CLIENT_ID.apps.googleusercontent.com