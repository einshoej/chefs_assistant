# Chef's Assistant

🔗 **Live App**: [https://chefsassistant.streamlit.app/](https://chefsassistant.streamlit.app/)

A Streamlit-based recipe management and meal planning application for organizing recipes and planning meals.

## 🚀 Quick Start

See [SETUP.md](SETUP.md) for detailed setup instructions.

## 📋 Features

- **Google Authentication**: Secure login with Google accounts using Streamlit's native auth
- **Weekly Meal Planning**: Organize recipes into a weekly calendar view
- **Recipe Browser**: Search and filter through your recipe collection
- **Session Storage**: Fast, in-memory storage with optional Google Drive persistence
- **User Profiles**: Personalized experience with Google account integration

## 🛠️ Configuration

### Google Drive Storage (Optional)

Enable cloud persistence for your recipes and meal plans:
1. Configure Google Drive API credentials (see [SETUP.md](SETUP.md))
2. Authorize Drive access after login
3. Recipes and meal plans will auto-save to your Drive


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
├── SETUP.md                          # Setup instructions
└── src/
    ├── pages/                        # Streamlit pages
    │   ├── this_week/               # Weekly meal planning
    │   ├── browse_recipes/          # Recipe browser
    │   └── profile/                 # User profile
    ├── models/                       # Data models
    ├── utils/                        # Utilities
    │   ├── auth.py                  # Authentication helpers
    │   └── google_drive_oauth.py    # Google Drive integration
    └── scripts/
        ├── setup/                    # Setup scripts
        └── tests/                    # Test scripts
```

## 🔧 Troubleshooting

See [SETUP.md](SETUP.md) for troubleshooting common issues.

## 🔒 Security Notes

- Never commit `.streamlit/secrets.toml` to version control
- Use HTTPS in production environments
- Keep your Google OAuth credentials secure
- Session cookies expire after 30 days for security

## 💻 Development

### Running Tests

```bash
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