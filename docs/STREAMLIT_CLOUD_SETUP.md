# Streamlit Cloud Setup Guide

This guide explains how to deploy Chef's Assistant to Streamlit Cloud.

## Prerequisites

1. A GitHub repository with the Chef's Assistant code
2. A Streamlit Cloud account (free tier available at [streamlit.io/cloud](https://streamlit.io/cloud))
3. Google OAuth credentials configured for your domain

## Step 1: Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Select "Web application" as the application type
6. Add the following authorized redirect URIs:
   - `https://YOUR-APP-NAME.streamlit.app/oauth2callback` (for login)
   - `https://YOUR-APP-NAME.streamlit.app/drive_oauth2callback` (for Google Drive, optional)
7. Save your `client_id` and `client_secret`

## Step 2: Deploy to Streamlit Cloud

1. Fork or push this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and select your repository
4. Set the main file path to `main.py`
5. Choose your branch (usually `main` or `master`)

## Step 3: Configure Secrets

In your Streamlit Cloud app settings, go to "Settings" → "Secrets" and add the following configuration:

```toml
[auth]
# Production redirect URI
redirect_uri = "https://YOUR-APP-NAME.streamlit.app/oauth2callback"

# Generate a strong cookie secret (32+ characters)
# You can generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"
cookie_secret = "YOUR-STRONG-RANDOM-COOKIE-SECRET-HERE"

# Google OAuth Credentials from Step 1
client_id = "YOUR-CLIENT-ID.apps.googleusercontent.com"
client_secret = "YOUR-GOOGLE-CLIENT-SECRET"

# Google's OIDC server (standard for all Google OIDC clients)
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

# OAuth scopes for login
client_kwargs = { scope = "openid email profile" }

# Optional: Google Drive Storage Configuration
# Uncomment and configure if you want to enable Google Drive storage
# [google_drive]
# redirect_uri = "https://YOUR-APP-NAME.streamlit.app/drive_oauth2callback"
# client_id = "YOUR-CLIENT-ID.apps.googleusercontent.com"  # Can be same as auth.client_id
# client_secret = "YOUR-GOOGLE-CLIENT-SECRET"  # Can be same as auth.client_secret
```

Replace the following placeholders:
- `YOUR-APP-NAME`: Your Streamlit app name (e.g., `chefsassistant`)
- `YOUR-STRONG-RANDOM-COOKIE-SECRET-HERE`: A randomly generated 32+ character string
- `YOUR-CLIENT-ID`: Your Google OAuth client ID
- `YOUR-GOOGLE-CLIENT-SECRET`: Your Google OAuth client secret

## Step 4: Verify Deployment

1. Once deployed, visit your app at `https://YOUR-APP-NAME.streamlit.app`
2. Click "Sign in with Google" 
3. Authorize the application
4. You should be redirected back to the app and logged in

## Limitations on Streamlit Cloud

### Node.js and AnyList Integration
- Streamlit Cloud does not provide Node.js runtime by default
- The AnyList integration requires Node.js to work
- When running on Streamlit Cloud, the AnyList sync feature will be disabled
- Users can still use the app for meal planning with manually added recipes

### Workarounds
1. **Manual Recipe Entry**: Users can manually add recipes instead of syncing from AnyList
2. **Local Development**: For full functionality including AnyList sync, run the app locally
3. **Alternative Hosting**: Consider deploying to a platform that supports both Python and Node.js (e.g., Heroku, Google Cloud Run, AWS)

## Troubleshooting

### "To use authentication features you need to configure credentials"
- This error means the secrets are not properly configured
- Double-check that you've added all required fields in the Secrets section
- Ensure there are no typos in the TOML format

### "KeyError: 'src'" or similar import errors
- Ensure all `__init__.py` files are present in the repository
- The app should have `__init__.py` files in all Python package directories

### Authentication redirect errors
- Verify that the redirect_uri in your secrets matches exactly what's configured in Google Cloud Console
- The URI must include the full path including `/oauth2callback`

### "Sign in with Google" button doesn't work
- Check browser console for errors
- Ensure cookies are enabled in your browser
- Try clearing browser cache and cookies for the Streamlit app domain

## Security Best Practices

1. **Never commit secrets.toml to version control** - It's already in .gitignore
2. **Use strong cookie secrets** - Generate cryptographically secure random strings
3. **Limit OAuth scopes** - Only request the minimum necessary permissions
4. **Regular credential rotation** - Periodically update your client secrets
5. **Monitor usage** - Check Google Cloud Console for unusual authentication patterns

## Support

For issues specific to:
- **Streamlit Cloud**: Contact [Streamlit support](https://streamlit.io/cloud/support)
- **Google OAuth**: Check [Google OAuth documentation](https://developers.google.com/identity/protocols/oauth2)
- **This application**: Open an issue in the GitHub repository