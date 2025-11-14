# TeamSnap API Integration (Python)

A clean, modern Python integration with the TeamSnap API v3, featuring OAuth 2.0 authentication using the out-of-band (OOB) flow for easy local testing.

**New**: Now includes an MCP (Model Context Protocol) server for Claude Desktop! See [teamsnap_mcp/](teamsnap_mcp/) for details.

## Features

- **OAuth 2.0 Authentication**: Complete implementation using out-of-band (OOB) flow
- **Automatic Token Management**: Tokens are saved and reused automatically
- **Clean API Client**: Easy-to-use methods for common TeamSnap operations
- **Type Hints**: Full type annotations for better IDE support
- **Local Testing**: Simple copy/paste authentication flow for local testing
- **MCP Server**: Connect Claude Desktop to your TeamSnap data with read/write access

## Project Structure

```
.
├── config.ini.template      # Configuration template
├── teamsnap_auth.py         # OAuth authentication module
├── teamsnap_client.py       # API client
├── example.py               # Example usage script
├── requirements.txt         # Python dependencies
├── teamsnap_mcp/           # MCP server for Claude Desktop
│   ├── server.py           # MCP server implementation
│   ├── client.py           # Async API client
│   └── README.md           # MCP server documentation
└── README.md               # This file
```

## Prerequisites

- Python 3.12 or higher
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

## Maintenance & Updates

This project includes automated tools to keep dependencies up-to-date:

### Automated Updates

- **Dependabot:** Automatically creates PRs for dependency updates every Monday
- **GitHub Actions:** Weekly automated dependency checks and testing
- **Security Scanning:** Automatic vulnerability detection
- **API Monitoring:** Weekly checks for TeamSnap API changes

### Manual Updates

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add requests --upgrade

# Check for security issues
uv run safety check
```

### API Monitoring

The client automatically tracks API version and deprecation warnings:

```bash
# Monitor current API state
uv run python monitor_api.py

# Compare with previous state
uv run python monitor_api.py --compare

# Check for deprecations
uv run python monitor_api.py --show-deprecations
```

**Automatic Features:**
- Logs API version on client initialization
- Detects deprecation warnings in responses
- Weekly automated monitoring via GitHub Actions
- Creates issues when API changes detected

### Testing

```bash
# Run the test suite
uv run pytest tests/ -v

# Test the integration manually
uv run python example.py
```

For detailed maintenance procedures, see [MAINTENANCE.md](MAINTENANCE.md).

## MCP Server for Claude Desktop

Want to give Claude Desktop access to your TeamSnap data? Check out the MCP server!

### What is MCP?

Model Context Protocol (MCP) is an open standard by Anthropic that lets Claude connect to external tools and data sources. The TeamSnap MCP server gives Claude the ability to:

- ✅ **Read** your teams, events, members, assignments, and more
- ✅ **Write** create events, add members, update availability
- ✅ **Manage** your TeamSnap data directly from conversations with Claude

### Quick Start

```bash
# From the teamsnap_mcp directory
cd teamsnap_mcp

# Follow the quick start guide
cat QUICKSTART.md
```

### Features

- **19+ Tools**: List teams, create events, manage members, and more
- **Full CRUD**: Create, read, update, and delete TeamSnap resources
- **Async**: High-performance async client using httpx
- **Well-Tested**: Comprehensive test suite with pytest
- **Auto-Maintained**: Same automation as main integration (Dependabot, CI, API monitoring)

### Documentation

- [teamsnap_mcp/README.md](teamsnap_mcp/README.md) - Full documentation
- [teamsnap_mcp/QUICKSTART.md](teamsnap_mcp/QUICKSTART.md) - 5-minute setup guide
- [teamsnap_mcp/MAINTENANCE.md](teamsnap_mcp/MAINTENANCE.md) - Maintenance procedures
- [teamsnap_mcp/CLAUDE_MCP.md](teamsnap_mcp/CLAUDE_MCP.md) - Developer guide

### Example Usage in Claude Desktop

Once configured, you can ask Claude:

> "List my TeamSnap teams"

> "Create a practice for team 12345 on January 15 at 2pm"

> "Who's available for event 67890?"

> "Add John Doe to team 12345"

Claude will use the MCP tools to interact with your TeamSnap account!

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
