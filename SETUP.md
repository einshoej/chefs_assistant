# Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google+ API
3. Create OAuth 2.0 credentials (Web application)
4. Add these redirect URIs:
   - **Local development:**
     - `http://localhost:8501/oauth2callback`
     - `http://localhost:8501/drive_oauth2callback`
   - **Production:**
     - `https://chefsassistant.streamlit.app/oauth2callback`
     - `https://chefsassistant.streamlit.app/drive_oauth2callback`

### 3. Local Configuration

Create `.streamlit/secrets.toml`:
```toml
[auth]
client_id = "your-google-client-id.apps.googleusercontent.com"
client_secret = "your-google-client-secret"
cookie_secret = "your-32-byte-random-secret"
redirect_uri = "http://localhost:8501/oauth2callback"

[google_drive]
client_id = "your-google-client-id.apps.googleusercontent.com"
client_secret = "your-google-client-secret"
redirect_uri = "http://localhost:8501/drive_oauth2callback"
```

Generate cookie secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run Locally
```bash
streamlit run main.py
```

## Production Deployment

App is deployed at: https://chefsassistant.streamlit.app/

To deploy:
1. Push to GitHub
2. Connect repository in Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard (same format as above, but with production URLs)

## Troubleshooting

- **redirect_uri_mismatch**: Check URIs in Google Console match exactly
- **Authentication errors**: Clear browser cache and try incognito mode
- **Google Drive access**: Authorize separately in Settings → Google Drive Storage