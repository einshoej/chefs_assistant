# IMPORTANT: Google Cloud Console Setup Required

🔗 **Live App**: [https://chefsassistant.streamlit.app/](https://chefsassistant.streamlit.app/)

## The Issue
You're getting a "redirect_uri_mismatch" error because the redirect URIs in Google Cloud Console don't match what the app is using.

## What You Need to Do in Google Cloud Console

### Step 1: Go to Your OAuth Client Settings
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (Chef's Assistant)
3. Navigate to **APIs & Services** > **Credentials**
4. Click on your OAuth 2.0 Client ID (the one with ID: `473098721962-ie7c5dq6n0lpkin2at7dqgs83lms52vt.apps.googleusercontent.com`)

### Step 2: Check/Update Authorized Redirect URIs

#### For Local Development:
```
http://localhost:8501/oauth2callback
http://localhost:8501/drive_oauth2callback
```

#### For Production (Streamlit Cloud):
```
https://chefsassistant.streamlit.app/oauth2callback
https://chefsassistant.streamlit.app/drive_oauth2callback
```

**IMPORTANT**: 
- The first one is for Streamlit login
- The second one is for Google Drive access
- Both must be present
- They must be exactly as shown (http, not https)
- The port must be 8501

### Step 3: Save Changes
Click "Save" at the bottom of the OAuth client configuration page.

## What's Been Fixed in the Code

✅ **secrets.toml** has been updated:
- Removed Drive scope from login auth (was causing conflicts)
- Added separate `[google_drive]` section with its own redirect URI
- Login now uses only basic scopes: "openid email profile"

✅ **OAuth flows are now separated**:
- Login: `/oauth2callback` 
- Drive: `/drive_oauth2callback`

## Testing After Google Console Update

1. **Test Login**:
   - Clear your browser cookies for localhost:8501
   - Go to http://localhost:8501
   - Click "Sign in with Google"
   - Should work without redirect_uri_mismatch error

2. **Test Google Drive** (after login works):
   - Go to Settings > Google Drive Storage tab
   - Click "Connect Google Drive"
   - Authorize when prompted
   - Should see "✅ Google Drive connected"

## Production Deployment (Already Live)

The app is deployed at https://chefsassistant.streamlit.app/

Make sure these URIs are added in Google Cloud Console:
```
https://chefsassistant.streamlit.app/oauth2callback
https://chefsassistant.streamlit.app/drive_oauth2callback
```

## Current Configuration

Your app is now configured with:
- Client ID: `473098721962-ie7c5dq6n0lpkin2at7dqgs83lms52vt.apps.googleusercontent.com`
- Two separate OAuth flows (login and Drive)
- Proper scope separation

## Troubleshooting

If you still get redirect_uri_mismatch:
1. Double-check the URIs are EXACTLY as shown above
2. Wait a few minutes for Google's changes to propagate
3. Clear browser cache/cookies
4. Make sure you're accessing the app at http://localhost:8501 (not 127.0.0.1 or another port)