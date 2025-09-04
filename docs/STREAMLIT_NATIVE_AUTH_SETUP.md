# Streamlit Native Authentication Setup Guide

## Overview
This application uses Streamlit's native authentication features (`st.login()`, `st.logout()`, and `st.user`) with Google OpenID Connect (OIDC). This provides a secure, built-in authentication system without requiring custom OAuth implementation.

## Prerequisites
- Streamlit version 1.37.0 or higher with auth support
- Google Cloud account with a project
- Python 3.8 or higher

## Quick Start

### 1. Install Dependencies

**Important**: You must install Streamlit with the `auth` extra to use native authentication:

```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install "streamlit[auth]>=1.37.0"
```

This installs Streamlit with Authlib (>=1.3.2), which is required for OAuth/OIDC support.

### 2. Set Up Google OAuth 2.0 Credentials

#### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API** for your project

#### Step 2: Create OAuth 2.0 Credentials
1. Navigate to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Web application** as the application type
4. Configure the following:
   - **Name**: Recipe Calendar App (or any name you prefer)
   - **Authorized redirect URIs**: 
     - For local development: `http://localhost:8501/oauth2callback`
     - For production: `https://yourdomain.com/oauth2callback`
   - **Important**: The redirect URI must end with `/oauth2callback`
5. Click **Create**
6. Copy the **Client ID** and **Client Secret** (you'll need these next)

### 3. Configure Streamlit Authentication

#### Option A: Use the Setup Helper (Recommended)
Run the setup helper script:
```bash
python setup_auth.py
```
This will:
- Generate a secure cookie secret for you
- Create the `.streamlit/secrets.toml` file
- Provide instructions for adding your Google OAuth credentials

#### Option B: Manual Configuration
1. Copy the example configuration:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your credentials:
   ```toml
   [auth]
   redirect_uri = "http://localhost:8501/oauth2callback"
   cookie_secret = "your-strong-random-secret-here"
   client_id = "your-client-id.apps.googleusercontent.com"
   client_secret = "your-client-secret"
   server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
   ```

#### Step 2: Generate a Cookie Secret
Generate a strong, random cookie secret:
```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and use it as your `cookie_secret` value.

### 4. Run the Application
```bash
streamlit run main.py
```

The app will open in your browser. Click **"Sign in with Google"** to authenticate.

## How It Works

### Native Authentication Flow
1. **Login**: When a user clicks "Sign in with Google", `st.login()` redirects them to Google
2. **Authentication**: Google verifies the user's identity
3. **Callback**: Google redirects back to your app with an authorization code
4. **Session**: Streamlit creates a secure session cookie
5. **User Info**: User information is available via `st.user`
6. **Logout**: `st.logout()` clears the session and logs out the user

### User Information
Once logged in, the following user attributes are typically available via `st.user`:
- `st.user.is_logged_in` - Boolean indicating login status
- `st.user.name` - User's full name
- `st.user.email` - User's email address
- `st.user.given_name` - First name
- `st.user.family_name` - Last name
- `st.user.picture` - URL to user's profile picture
- `st.user.email_verified` - Whether email is verified

### Code Example
```python
import streamlit as st

# Check if user is logged in
if not st.user.is_logged_in:
    # Show login button
    if st.button("Sign in with Google"):
        st.login()
    st.stop()

# User is logged in - show app content
st.write(f"Welcome, {st.user.name}!")

# Logout button
if st.button("Logout"):
    st.logout()
```

## Production Deployment

### 1. Update Redirect URI
In production, update your redirect URI in both:
- Google Cloud Console (add your production URL)
- `.streamlit/secrets.toml` (update redirect_uri)

Example for production:
```toml
[auth]
redirect_uri = "https://your-app-domain.com/oauth2callback"
```

### 2. Environment-Specific Configuration
Use different secrets files for different environments:
- `.streamlit/secrets.toml` for local development (gitignored)
- Set secrets via Streamlit Community Cloud settings for hosted apps
- Use environment variables or secret management services for other deployments

### 3. Security Best Practices
- **Never commit secrets.toml** to version control
- Use strong, randomly generated cookie secrets
- Regularly rotate your client secrets
- Use HTTPS in production (required for OAuth)
- Restrict redirect URIs to only necessary domains

## Troubleshooting

### "Authentication is not configured" Warning
- Ensure `.streamlit/secrets.toml` exists and contains valid credentials
- Check that all required fields are present in the `[auth]` section
- Verify the file path is correct: `.streamlit/secrets.toml`

### "Invalid redirect URI" Error
- Ensure the redirect URI in secrets.toml exactly matches what's configured in Google Cloud Console
- The URI must end with `/oauth2callback`
- Check for typos or missing protocol (http:// or https://)
- Port number must match (e.g., `:8501` for local development)

### User Remains Logged In After Closing Browser
- This is expected behavior - the session cookie persists for 30 days
- Users must explicitly click "Logout" to end their session immediately
- You can implement custom session timeout logic if needed

### "state parameter" Error
- Clear browser cookies and try again
- This usually happens when the OAuth flow is interrupted

### Login Button Does Nothing
- Check browser console for JavaScript errors
- Ensure pop-ups are not blocked
- Try a different browser or incognito mode

## Advanced Configuration

### Custom OIDC Parameters
You can pass additional parameters to Google via `client_kwargs`:
```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "xxx"
client_id = "xxx"
client_secret = "xxx"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
client_kwargs = { prompt = "select_account" }
```

Common parameters:
- `prompt = "select_account"` - Force account selection
- `prompt = "consent"` - Force consent screen
- `access_type = "offline"` - Request refresh token
- `include_granted_scopes = "true"` - Incremental authorization

### Multiple Identity Providers
While this app uses Google, you can configure multiple providers:
```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "xxx"

[auth.google]
client_id = "xxx"
client_secret = "xxx"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[auth.microsoft]
client_id = "xxx"
client_secret = "xxx"
server_metadata_url = "https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration"
```

Then in your code:
```python
st.button("Sign in with Google", on_click=st.login, args=["google"])
st.button("Sign in with Microsoft", on_click=st.login, args=["microsoft"])
```

## Migration from Custom OAuth

If you previously used the custom `google_auth.py` implementation:

1. **Data Migration**: User sessions don't transfer - users must log in again
2. **Configuration**: Move from `config.py` to `.streamlit/secrets.toml`
3. **Code Changes**: Replace custom auth checks with `st.user.is_logged_in`
4. **Cleanup**: Remove old OAuth packages from requirements.txt

## Resources

- [Streamlit Authentication Documentation](https://docs.streamlit.io/develop/concepts/connections/authentication)
- [Google Identity Platform](https://developers.google.com/identity)
- [OpenID Connect Specification](https://openid.net/specs/openid-connect-core-1_0.html)
- [Google Cloud Console](https://console.cloud.google.com/)

## Support

For issues related to:
- **Streamlit authentication**: Check [Streamlit Forums](https://discuss.streamlit.io/)
- **Google OAuth**: See [Google Identity Documentation](https://developers.google.com/identity/protocols/oauth2)
- **This application**: Check the error messages and this documentation
