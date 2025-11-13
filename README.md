# TeamSnap API Integration (Python)

A clean, modern Python integration with the TeamSnap API v3, featuring OAuth 2.0 authentication using the out-of-band (OOB) flow for easy local testing.

## Features

- **OAuth 2.0 Authentication**: Complete implementation using out-of-band (OOB) flow
- **Automatic Token Management**: Tokens are saved and reused automatically
- **Clean API Client**: Easy-to-use methods for common TeamSnap operations
- **Type Hints**: Full type annotations for better IDE support
- **Local Testing**: Simple copy/paste authentication flow for local testing

## Project Structure

```
.
├── config.ini.template      # Configuration template
├── teamsnap_auth.py         # OAuth authentication module
├── teamsnap_client.py       # API client
├── example.py               # Example usage script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Prerequisites

- Python 3.7 or higher
- A TeamSnap account
- TeamSnap OAuth application credentials

## Setup

### 1. Install Dependencies

This project uses `uv` for fast, modern Python dependency management.

**If you don't have uv installed:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Install dependencies:**
```bash
uv sync
```

This creates a virtual environment in `.venv` and installs all dependencies.

**Alternative (using pip):**
```bash
pip install -r requirements.txt
```

### 2. Configure TeamSnap OAuth Application

1. Visit your OAuth application at: https://auth.teamsnap.com/oauth/applications/
   (Or create a new one at: https://auth.teamsnap.com/oauth/applications)

2. For the Redirect URI, use: `urn:ietf:wg:oauth:2.0:oob`

   **Important**: TeamSnap requires this exact value for local testing (out-of-band flow)

3. Note your **Client ID** and **Client Secret**

### 3. Create Configuration File

Copy the template and add your credentials:

```bash
cp config.ini.template config.ini
```

Edit `config.ini` and replace the placeholder values:

```ini
[teamsnap]
client_id = YOUR_ACTUAL_CLIENT_ID
client_secret = YOUR_ACTUAL_CLIENT_SECRET
redirect_uri = urn:ietf:wg:oauth:2.0:oob

# Leave these empty - they'll be auto-generated
access_token =
refresh_token =
token_expires_at =
```

**Security Note**: Never commit `config.ini` to version control! Add it to `.gitignore`.

## Usage

### Quick Start

Run the example script to authenticate and fetch data:

```bash
uv run python example.py
```

Or activate the virtual environment first:
```bash
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

python example.py
```

This will:
1. Open your browser for authentication
2. Display an authorization code in the browser
3. Prompt you to copy/paste the code
4. Exchange the code for an access token and save it to `config.ini`
5. Fetch and display your user info, teams, members, and events

### Authentication Only

To just authenticate without running the full example:

```bash
uv run python teamsnap_auth.py
```

### Using the Client in Your Code

```python
from teamsnap_client import TeamSnapClient

# Initialize client (auto-authenticates if needed)
client = TeamSnapClient()

# Get current user
me = client.get_me()
print(me)

# Search teams
teams = client.search_teams(user_id=123)

# Get team details
team = client.get_team(team_id=456)

# Search members
members = client.search_members(team_id=456)

# Search events
events = client.search_events(team_id=456)

# Make custom requests
response = client.custom_request('GET', '/custom/endpoint')
```

## API Client Methods

### User Methods
- `get_me()` - Get current authenticated user
- `get_user(user_id)` - Get specific user

### Team Methods
- `search_teams(user_id=None)` - Search teams
- `get_team(team_id)` - Get specific team

### Member Methods
- `search_members(team_id=None)` - Search team members

### Event Methods
- `search_events(team_id=None)` - Search events
- `get_event(event_id)` - Get specific event

### Other Methods
- `search_opponents(team_id=None)` - Search opponents
- `search_locations(team_id=None)` - Search locations
- `get_root()` - Get API root (available endpoints)
- `custom_request(method, endpoint, **kwargs)` - Make custom API calls

## Troubleshooting

### OAuth Authorization Issues

**Problem**: Can't add redirect URI or getting OAuth errors

**Solutions**:
1. Make sure the redirect URI in TeamSnap is exactly: `urn:ietf:wg:oauth:2.0:oob`
2. This must match the `redirect_uri` in your `config.ini` file
3. TeamSnap does not support `localhost` URLs - you must use the OOB flow

### Authorization Code Not Showing

**Problem**: Code doesn't appear in browser after authorization

**Solutions**:
1. Make sure your redirect URI in TeamSnap is `urn:ietf:wg:oauth:2.0:oob`
2. Try manually visiting the authorization URL printed in the terminal
3. After authorizing, TeamSnap should display the code in the browser window

### Invalid Client Error

**Problem**: "Invalid client_id or client_secret"

**Solutions**:
1. Double-check your credentials in `config.ini`
2. Make sure you copied the full Client ID and Secret (no spaces)
3. Verify your OAuth application is active at https://auth.teamsnap.com

### API Errors

**Problem**: API requests fail with 401 or 403

**Solutions**:
1. Re-authenticate: `uv run python teamsnap_auth.py`
2. Check that your token hasn't expired
3. Verify you have proper scopes (default is 'read write')
4. Ensure your TeamSnap account has access to the requested resources

### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'requests'"

**Solution**: Install dependencies:
```bash
uv sync
```

Or if using pip:
```bash
pip install -r requirements.txt
```

## Understanding TeamSnap's Collection+JSON Format

TeamSnap API uses the Collection+JSON format. Responses look like:

```json
{
  "collection": {
    "items": [
      {
        "data": [
          {"name": "id", "value": 123},
          {"name": "first_name", "value": "John"},
          {"name": "last_name", "value": "Doe"}
        ]
      }
    ]
  }
}
```

The client handles this automatically, but you may need to parse it for custom requests.

## Security Best Practices

1. **Never commit credentials**: Add `config.ini` to `.gitignore`
2. **Use environment variables**: For production, use environment variables instead of config files
3. **Rotate secrets regularly**: Update your Client Secret periodically
4. **Scope properly**: Only request the OAuth scopes you need
5. **HTTPS in production**: Only use `http://localhost` for local testing

## How Authentication Works

The out-of-band (OOB) OAuth flow works as follows:

1. Your app requests authorization with `redirect_uri=urn:ietf:wg:oauth:2.0:oob`
2. User approves the app in their browser
3. Instead of redirecting to a URL, TeamSnap displays the authorization code in the browser
4. User copies the code and pastes it into your application
5. Your app exchanges the code for an access token

This is perfect for local testing without needing to set up a web server or public callback URL.

### OAuth Scopes

To request different scopes, modify `teamsnap_auth.py`:

```python
auth_url = self.get_authorization_url(scope='read')  # Read-only
```

Available scopes: `read`, `write`, `read write`

## API Documentation

- TeamSnap API v3: https://api.teamsnap.com/v3/
- OAuth Apps Management: https://auth.teamsnap.com/oauth/applications

## Contributing

This is a demonstration project. Feel free to extend it for your needs!

## License

This project is provided as-is for demonstration purposes.

## Support

For TeamSnap API issues, contact TeamSnap support.
For OAuth application management, visit: https://auth.teamsnap.com
