# Deployment Guide for Chef's Assistant

🎉 **Successfully Deployed**: [https://chefsassistant.streamlit.app/](https://chefsassistant.streamlit.app/)

**GitHub Repository**: [https://github.com/einshoej/chefs_assistant](https://github.com/einshoej/chefs_assistant)

## Deploying to Streamlit Community Cloud

### Prerequisites

1. GitHub account with this repository
2. Streamlit Community Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
3. Google Cloud Console project with OAuth 2.0 credentials configured

### Step 1: Prepare Your Repository

This repository is already configured for Streamlit deployment with:
- `main.py` as the entry point
- `requirements.txt` with all Python dependencies
- `.streamlit/config.toml` for app configuration
- `.streamlit/secrets.toml.example` as a template for secrets

### Step 2: Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Create app"** or **"New app"**
3. Connect your GitHub account if not already connected
4. Select deployment method: **"From existing repo"**
5. Fill in the deployment form:
   - Repository: `einshoej/chefs_assistant`
   - Branch: `main`
   - Main file path: `main.py`
   - App URL (optional): Choose a custom subdomain
6. Click **"Deploy"**

### Step 3: Configure Secrets

After deployment, you need to configure secrets in the Streamlit Cloud dashboard:

1. Go to your app's dashboard on Streamlit Community Cloud
2. Click on **"Settings"** → **"Secrets"**
3. Add the following secrets (copy from `.streamlit/secrets.toml.example`):

```toml
# Google OAuth Configuration
client_id = "your-google-oauth-client-id"
client_secret = "your-google-oauth-client-secret"
cookie_secret = "your-random-32-byte-cookie-secret"
redirect_uri = "https://chefsassistant.streamlit.app/oauth2callback"

# Optional: AnyList Credentials (if using)
[anylist]
email = "your-anylist-email@example.com"
password = "your-anylist-password"

# Optional: Google Drive Integration
[google_drive]
client_id = "your-google-drive-client-id"
client_secret = "your-google-drive-client-secret"
```

### Step 4: Update Google OAuth Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Add your Streamlit app URL to **Authorized redirect URIs**:
   - `https://chefsassistant.streamlit.app/oauth2callback`
   - `https://chefsassistant.streamlit.app/`
5. Save the changes

### Step 5: Optional Features

#### Google Drive Integration

If you want to use Google Drive for persistent storage:

1. Enable Google Drive API in Google Cloud Console
2. Add Drive API scopes to your OAuth consent screen
3. Configure the `[google_drive]` section in secrets

#### AnyList Integration

Note: AnyList integration requires Node.js, which is not available on Streamlit Community Cloud by default. The app will work without it, but recipe importing from AnyList will be disabled.

For full AnyList support, consider:
- Self-hosting the application
- Using a Docker deployment
- Setting up a separate API service for AnyList

### Updating Your App

Your app will automatically redeploy when you push changes to your GitHub repository:

```bash
git add .
git commit -m "Update app"
git push origin main
```

### Troubleshooting

#### Authentication Issues
- Ensure OAuth redirect URIs match exactly
- Verify all secrets are correctly configured
- Check that cookie_secret is a valid 32-byte string

#### Missing Dependencies
- All Python dependencies should be in `requirements.txt`
- Streamlit will automatically install them on deployment

#### AnyList Features Not Working
- This is expected on Streamlit Community Cloud
- The app will gracefully handle the missing Node.js dependency
- Consider alternative deployment methods if this feature is critical

### Local Development

To run the app locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up authentication (if not done)
python setup_auth.py

# Run the app
streamlit run main.py
```

### Security Notes

- Never commit `secrets.toml` to version control
- Rotate your cookie_secret periodically
- Use strong passwords for all integrations
- Keep your OAuth credentials secure

## Alternative Deployment Options

### Docker Deployment

For full feature support including AnyList integration, consider using Docker:

```dockerfile
# Dockerfile example (to be created if needed)
FROM python:3.11
RUN apt-get update && apt-get install -y nodejs npm
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "main.py"]
```

### Self-Hosting

For complete control and all features:
1. Deploy to a VPS (DigitalOcean, AWS EC2, etc.)
2. Install Python and Node.js
3. Configure reverse proxy (nginx)
4. Set up SSL certificates (Let's Encrypt)
5. Run as a systemd service

## Support

For issues or questions:
- Check the [README.md](README.md) for general information
- Review [IMPORTANT_GOOGLE_CONSOLE_SETUP.md](IMPORTANT_GOOGLE_CONSOLE_SETUP.md) for OAuth setup
- Open an issue on GitHub for bugs or feature requests