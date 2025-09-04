# Chef's Assistant

A Streamlit-based recipe management and meal planning application with AnyList integration for seamless recipe importing and organization.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js (for AnyList integration)
- Google Cloud Console account (for authentication)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important**: This installs `streamlit[auth]` which includes Authlib for OAuth support.

### 2. Set Up Google OAuth

#### Get Google Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google+ API
3. Create OAuth 2.0 credentials (Web application)
4. Add redirect URI: `http://localhost:8501/oauth2callback`
5. Copy your Client ID and Client Secret

#### Configure Authentication:
1. Create `.streamlit/secrets.toml` file with your credentials:
```toml
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
cookie_secret = "your-32-byte-random-secret"
redirect_uri = "http://localhost:8501/oauth2callback"
```

2. Generate a secure cookie secret (32 bytes) for session management

### 3. Set Up AnyList Integration (Optional)

For recipe importing from AnyList:

```powershell
# Windows users:
powershell src/scripts/setup/setup_nodejs_anylist.ps1

# Or manually:
cd src/anylist_integration/nodejs
npm install
```

### 4. Run the Application

```bash
streamlit run main.py
```

The app will open at `http://localhost:8501`

## 📋 Features

- **Google Authentication**: Secure login with Google accounts using Streamlit's native auth
- **AnyList Integration**: Import and sync recipes from your AnyList account
- **Weekly Meal Planning**: Organize recipes into a weekly calendar view
- **Recipe Browser**: Search and filter through your recipe collection
- **Session Storage**: Fast, in-memory storage with optional Google Drive persistence
- **User Profiles**: Personalized experience with Google account integration

## 🛠️ Configuration

### Google Drive Storage (Optional)

Enable cloud persistence for your recipes and meal plans:
1. Configure Google Drive API credentials
2. Authorize Drive access after login
3. Recipes and meal plans will auto-save to your Drive

See [GOOGLE_DRIVE_STORAGE_SETUP.md](docs/GOOGLE_DRIVE_STORAGE_SETUP.md) for detailed instructions.

### AnyList Credentials

If using AnyList integration, you'll be prompted to enter your AnyList credentials through the app's settings page.

## 📁 Project Structure

```
chefs_assistant/
├── main.py                           # Main application entry point
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── CLAUDE.md                         # Development guidelines
├── .streamlit/
│   ├── config.toml                  # Streamlit configuration
│   └── secrets.toml                  # OAuth credentials (create this)
├── docs/                             # Documentation
│   ├── QUICK_SETUP_GUIDE.md
│   ├── STREAMLIT_NATIVE_AUTH_SETUP.md
│   ├── GOOGLE_DRIVE_STORAGE_SETUP.md
│   └── ANYLIST_INTEGRATION.md
└── src/
    ├── anylist_integration/          # AnyList API client
    │   ├── anylist_official_client.py
    │   └── nodejs/                   # Node.js bridge
    ├── pages/                        # Streamlit pages
    │   ├── this_week/               # Weekly meal planning
    │   ├── browse_recipes/          # Recipe browser
    │   ├── anylist_settings/        # AnyList configuration
    │   └── profile/                 # User profile
    ├── models/                       # Data models
    ├── utils/                        # Utilities
    │   ├── auth.py                  # Authentication helpers
    │   └── google_auth.py           # Google Drive integration
    └── scripts/
        ├── setup/                    # Setup scripts
        └── tests/                    # Test scripts
```

## 🔧 Troubleshooting

### Authentication Issues

#### "st.user has no attribute 'is_logged_in'" Error
- Ensure `streamlit[auth]` is installed: `pip install -r requirements.txt`
- Verify `.streamlit/secrets.toml` exists with valid credentials

#### OAuth Not Working
1. Check that `.streamlit/secrets.toml` contains valid Google OAuth credentials
2. Ensure redirect URI matches exactly in Google Console and secrets.toml
3. Verify you're using the correct port (default: 8501)

### AnyList Integration Issues

#### Node.js Not Found
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Run the setup script: `powershell src/scripts/setup/setup_nodejs_anylist.ps1`

#### AnyList API Errors
- Verify your AnyList credentials in the app settings
- Check that the Node.js dependencies are installed in `src/anylist_integration/nodejs/`

## 📚 Documentation

For detailed setup and usage instructions:
- [Quick Setup Guide](docs/QUICK_SETUP_GUIDE.md) - Get started quickly
- [Authentication Setup](docs/STREAMLIT_NATIVE_AUTH_SETUP.md) - Complete auth configuration
- [Google Drive Storage](docs/GOOGLE_DRIVE_STORAGE_SETUP.md) - Cloud persistence setup
- [AnyList Integration](docs/ANYLIST_INTEGRATION.md) - Recipe import configuration
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md) - Feature completion status

## 🔒 Security Notes

- Never commit `.streamlit/secrets.toml` to version control
- Use HTTPS in production environments
- Keep your Google OAuth and AnyList credentials secure
- Session cookies expire after 30 days for security

## 💻 Development

### Running Tests

```bash
# Test AnyList integration
python src/scripts/tests/test_anylist_recipes_fetch.py

# Test Google Drive setup
python src/scripts/tests/test_google_drive_setup.py
```

### Development Guidelines

See [CLAUDE.md](CLAUDE.md) for detailed development rules and architecture notes.

## 🤝 Contributing

This application is under active development. Key areas for contribution:
- Enhanced recipe search and filtering
- Meal planning AI suggestions
- Shopping list generation
- Recipe sharing features
- Mobile responsiveness improvements

## 📄 License

This project is for demonstration and personal use.