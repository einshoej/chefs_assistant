# AnyList Integration

This application integrates with AnyList using the official `anylist` npm package through a Node.js bridge.

## Prerequisites

1. **Node.js** - Required for the AnyList API
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **AnyList Account** - You need valid AnyList credentials

## Setup

### 1. Install Dependencies

Run the setup script to install the required npm packages:

**Windows (Command Prompt):**
```cmd
cd src\scripts\setup
setup_nodejs_anylist.bat
```

**Windows (PowerShell):**
```powershell
cd src\scripts\setup
.\setup_nodejs_anylist.ps1
```

**Manual Installation:**
```bash
cd src/anylist_integration/nodejs
npm install
```

### 2. Connect Your Account

1. Open the Streamlit app
2. Navigate to **AnyList Settings** in the sidebar
3. Enter your AnyList email and password
4. Click **Connect AnyList**
5. Test the connection

## Features

- **Recipe Syncing** - Import all recipes from your AnyList account
- **Full Recipe Data** - Includes ingredients, instructions, ratings, times, and photos
- **Fast Performance** - Direct API access (no web scraping)
- **Automatic Updates** - Changes sync with your AnyList mobile apps

## Usage

### Sync Recipes

1. Go to **Browse Recipes** page
2. Click **🔄 Sync Recipes** button
3. Wait for recipes to load (typically 3-5 seconds per 10 recipes)

### View Recipe Details

- Browse synced recipes in the card view
- Click "View Full Recipe Details" to see ingredients and instructions
- Add recipes to your meal plan

## Technical Details

### Architecture

```
Streamlit (Python)
    ↓
AnyListOfficialClient
    ↓
Node.js Bridge (anylist_bridge.js)
    ↓
Official anylist npm package
    ↓
AnyList API
```

### File Structure

```
src/anylist_integration/
├── anylist_official_client.py   # Python wrapper
├── credential_manager.py         # Encrypted credential storage
└── nodejs/
    ├── package.json             # npm dependencies
    ├── anylist_bridge.js        # Node.js bridge script
    └── node_modules/            # npm packages
```

### Data Format

Recipes are returned in this format:

```python
{
    'id': 'unique-id',
    'name': 'Recipe Name',
    'description': 'Notes',
    'prep_time': 300,        # seconds
    'cook_time': 1800,       # seconds
    'servings': '4 servings',
    'rating': 5,
    'source': 'Website Name',
    'sourceUrl': 'https://...',
    'ingredients': [
        {
            'name': 'Flour',
            'quantity': '2 cups',
            'note': 'all-purpose',
            'rawText': '2 cups flour, all-purpose'
        }
    ],
    'preparation_steps': ['Step 1', 'Step 2'],
    'photo': {
        'url': 'https://...',
        'hasPhoto': True
    }
}
```

## Troubleshooting

### Node.js Not Found
- Install Node.js from https://nodejs.org/
- Restart your terminal/IDE after installation

### Login Failed
- Verify your AnyList credentials work on anylist.com
- Check if 2FA is enabled (not currently supported)
- Try disconnecting and reconnecting in AnyList Settings

### No Recipes Found
- Ensure you have recipes in your AnyList account
- Try syncing again
- Check the console for error messages

### SSL Certificate Errors
The integration automatically handles corporate SSL certificates. If you still have issues, check your network settings.

## Security

- Credentials are encrypted using Fernet encryption
- Stored locally in `src/data/anylist_creds.json`
- Never committed to version control
- Password is decrypted only when needed for API calls

## Limitations

- Recipe collections/categories are not available in the current anylist package version (0.8.5)
- 2FA is not currently supported
- Requires Node.js to be installed

## Support

For issues with:
- **This integration**: Check the error messages in the Streamlit app
- **AnyList API**: See https://github.com/codetheweb/anylist
- **AnyList service**: Contact AnyList support
