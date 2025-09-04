# Google OAuth Configuration Instructions

## Overview
This guide provides step-by-step instructions for updating the Google OAuth configuration to include Google Drive access scope for the Chef's Assistant application.

## Prerequisites
- Access to Google Cloud Console
- Admin access to the OAuth consent screen
- The application's OAuth 2.0 Client ID

## Step 1: Update Local Configuration ✅

The `.streamlit/secrets.toml` file has been updated with the necessary scope configuration:

```toml
[auth.client_kwargs]
scope = "openid email profile https://www.googleapis.com/auth/drive.file"
```

This adds the `https://www.googleapis.com/auth/drive.file` scope which allows the application to:
- Create new files in Google Drive
- Access and modify files created by the app
- Store recipes and meal plans in the user's Drive

## Step 2: Update Google Cloud Console

### Access the Console
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select the "Chef's Assistant" project
3. Navigate to "APIs & Services" → "OAuth consent screen"

### Update OAuth Consent Screen
1. Click "Edit App" on the OAuth consent screen
2. Navigate to the "Scopes" section
3. Click "Add or Remove Scopes"
4. Add the following scope:
   - `https://www.googleapis.com/auth/drive.file` (Google Drive Files)
5. Review the changes and save

### Verify Authorized Domains
Ensure these redirect URIs are configured:
- `http://localhost:8501/oauth2callback` (for local development)
- Add production URLs when deploying

## Step 3: Test the Configuration

### Local Testing
1. Restart the Streamlit application
2. Clear browser cookies/cache for localhost:8501
3. Log in again through Google OAuth
4. Verify the consent screen shows Drive access permission
5. Accept the permissions

### Verification Steps
1. After login, check that the user can:
   - Connect AnyList account
   - Import recipes
   - See recipes stored in Google Drive

## Step 4: Production Deployment

When deploying to production:

1. **Update Redirect URI**:
   - Add production URL to Google Cloud Console
   - Update `.streamlit/secrets.toml` with production redirect URI

2. **Verify Scopes**:
   - Ensure all required scopes are in production config
   - Test with a fresh user account

3. **Security Review**:
   - Review OAuth consent screen text
   - Ensure privacy policy URL is correct
   - Verify terms of service URL

## Troubleshooting

### Common Issues

#### "Access Blocked" Error
- **Cause**: App not verified or user not added to test users
- **Solution**: Add user email to test users list in OAuth consent screen

#### "Invalid Scope" Error
- **Cause**: Scope not properly configured in Google Cloud Console
- **Solution**: Follow Step 2 to add the Drive scope

#### Drive Access Not Working
- **Cause**: User didn't grant permission or scope not requested
- **Solution**: 
  1. Clear user session
  2. Re-authenticate
  3. Ensure consent screen shows Drive permission

### Debug Checklist
- [ ] Scope added to `.streamlit/secrets.toml`
- [ ] Scope added to Google Cloud Console
- [ ] User re-authenticated after changes
- [ ] Consent screen shows Drive permission
- [ ] Test with new user account

## Security Notes

- The `drive.file` scope is the most restrictive Drive scope
- It only allows access to files created by the app
- Users' existing Drive files remain inaccessible
- This is the recommended scope for apps that store user data

## Next Steps

After completing the OAuth configuration:

1. Test recipe import and storage
2. Verify Google Drive folder creation
3. Check recipe synchronization
4. Test with multiple user accounts

## Support

For issues or questions:
- Check the application logs for OAuth errors
- Review Google Cloud Console audit logs
- Verify all configuration matches exactly
