# TeamSnap MCP Server

A Model Context Protocol (MCP) server that provides Claude with read and write access to the TeamSnap API.

## What is MCP?

Model Context Protocol (MCP) is an open standard created by Anthropic that enables AI assistants like Claude to securely connect to external data sources and tools. Think of it as a way to give Claude superpowers by connecting it to your applications.

## Features

This TeamSnap MCP server provides Claude with the ability to:

### Read Operations
- **Teams**: List teams, get team details
- **Events**: List events, get event details, view availability responses
- **Members**: List team members with contact information
- **Assignments**: View tasks assigned to members for events
- **Locations**: List team locations
- **And more**: Forum topics, messages, broadcast emails, etc.

### Write Operations
- **Events**: Create, update, and delete events (games, practices)
- **Members**: Add, update, and remove team members
- **Availability**: Update member availability for events
- **Assignments**: Create and delete task assignments
- **Locations**: Create and delete locations

## Prerequisites

- Python 3.12 or higher
- A TeamSnap account with OAuth access token
- Claude Desktop app (for local use)
- `uv` package manager (recommended) or `pip`

## Installation

### 1. Install Dependencies

From the `teamsnap_mcp` directory:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 2. Get Your TeamSnap Access Token

You need a valid TeamSnap OAuth access token. If you haven't already:

```bash
# From the parent directory
cd ..
uv run python teamsnap_auth.py
```

This will authenticate you and save the token to `config.ini`.

### 3. Configure Environment

Create a `.env` file in the `teamsnap_mcp` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your access token:

```env
TEAMSNAP_ACCESS_TOKEN=your_actual_token_from_config.ini

# Read-Only Mode (IMPORTANT!)
# Set to "true" for read-only (safe, recommended)
# Set to "false" to enable write operations (creates, updates, deletes)
TEAMSNAP_READONLY=true
```

**Security Notes**:
- Never commit `.env` to version control!
- **Server defaults to READ-ONLY mode** for safety
- Only set `TEAMSNAP_READONLY=false` if you need write access

### 4. Configure Claude Desktop

Edit your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the TeamSnap server:

```json
{
  "mcpServers": {
    "teamsnap": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/teamsnap_mcp",
        "python",
        "server.py"
      ],
      "env": {
        "TEAMSNAP_ACCESS_TOKEN": "your_access_token_here",
        "TEAMSNAP_READONLY": "true"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/teamsnap_mcp` with the actual path and add your access token.

### 5. Restart Claude Desktop

Quit and restart Claude Desktop to load the MCP server.

## Read-Only Mode (Security Feature)

**The MCP server defaults to READ-ONLY mode for your safety.**

### What This Means

- ✅ **Read operations work**: List teams, view events, check availability, etc.
- ❌ **Write operations are blocked**: Create, update, delete operations will return an error

### Why Read-Only?

This prevents accidental modifications to your TeamSnap data through Claude. You must explicitly opt-in to enable writes.

### Enabling Write Operations

If you need to create, update, or delete TeamSnap data:

**Option 1: Via .env file**
```bash
# Edit teamsnap_mcp/.env
TEAMSNAP_READONLY=false
```

**Option 2: Via Claude Desktop config**
```json
{
  "mcpServers": {
    "teamsnap": {
      ...
      "env": {
        "TEAMSNAP_ACCESS_TOKEN": "your_token",
        "TEAMSNAP_READONLY": "false"
      }
    }
  }
}
```

**Then restart Claude Desktop.**

### Checking Current Mode

When you attempt a write operation in read-only mode, you'll see:

```
❌ Write operation blocked: Server is in READ-ONLY mode

To enable write operations:
1. Edit your .env file (or Claude Desktop config)
2. Set: TEAMSNAP_READONLY=false
3. Restart Claude Desktop

⚠️  SECURITY: Only enable writes if you trust this integration and
understand the risks of modifying your TeamSnap data.
```

## Usage

Once configured, you can ask Claude to interact with your TeamSnap data:

### Example Queries

**List teams**:
> "What teams do I have access to?"

**View events**:
> "Show me the upcoming events for team 12345"

**Check availability**:
> "Who's available for event 67890?"

**Create an event**:
> "Create a practice for team 12345 on January 15, 2025 at 2pm called 'Team Practice'"

**Add a member**:
> "Add John Doe to team 12345 with email john@example.com"

**Update availability**:
> "Mark availability 999 as 'yes'"

Claude will use the appropriate MCP tools to interact with your TeamSnap account.

## Available Tools

### Read Tools

- `list_teams(user_id?)` - List all accessible teams
- `get_team_details(team_id)` - Get detailed team information
- `list_events(team_id)` - List events for a team
- `get_event_details(event_id)` - Get detailed event information
- `list_members(team_id)` - List team members
- `get_event_availability(event_id)` - View availability responses
- `list_assignments(event_id)` - View assignments for an event
- `list_locations(team_id)` - List team locations

### Write Tools

- `create_event(team_id, name, start_date, ...)` - Create a new event
- `update_event(event_id, ...)` - Update an event
- `delete_event(event_id)` - Delete an event
- `create_member(team_id, first_name, last_name, ...)` - Add a member
- `update_member(member_id, ...)` - Update member information
- `delete_member(member_id)` - Remove a member
- `update_availability(availability_id, status)` - Update availability
- `create_assignment(event_id, member_id, description)` - Create assignment
- `delete_assignment(assignment_id)` - Delete assignment
- `create_location(team_id, name, address?)` - Create location
- `delete_location(location_id)` - Delete location

## Security Best Practices

1. **Never commit `.env` file** - It contains your access token
2. **Use environment variables** - Don't hardcode tokens in config files
3. **Rotate tokens regularly** - Update your OAuth credentials periodically
4. **Limit scope** - Only request necessary OAuth permissions
5. **Monitor usage** - Check TeamSnap audit logs for API activity

## Troubleshooting

### Server Not Showing in Claude Desktop

**Check logs**:
1. Open Claude Desktop Developer Tools (if available)
2. Check for error messages about the MCP server
3. Verify the path in `claude_desktop_config.json` is absolute and correct

**Common issues**:
- Path to `teamsnap_mcp` is relative instead of absolute
- Access token is invalid or expired
- `uv` is not in PATH
- Server is not executable

### Invalid or Expired Token

Re-authenticate from the parent directory:

```bash
cd ..
uv run python teamsnap_auth.py
```

Then copy the new token from `config.ini` to your `.env` file.

### API Errors

If you see 401 (Unauthorized) or 403 (Forbidden) errors:

1. Check that your token is valid
2. Verify you have permissions for the requested resource
3. Ensure your TeamSnap account has access to the team/event

### Import Errors

Make sure dependencies are installed:

```bash
uv sync
```

## Development

### Running Tests

```bash
uv run pytest tests/ -v
```

### Manual Testing

Test the server directly:

```bash
# Set environment variable
export TEAMSNAP_ACCESS_TOKEN="your_token"

# Run server
uv run python server.py
```

The server will listen on stdin/stdout for MCP protocol messages.

### Adding New Tools

To add a new tool to the server:

1. Add the corresponding method to `client.py` (if needed)
2. Add a new `@mcp.tool()` decorated function in `server.py`
3. Update this README with the new tool
4. Add tests in `tests/`

## Maintenance

### Dependency Updates

This project uses the same automated maintenance as the parent TeamSnap integration:

- **Dependabot**: Weekly dependency updates
- **GitHub Actions**: Automated testing and updates
- **API Monitoring**: Weekly TeamSnap API change detection

See [MAINTENANCE.md](MAINTENANCE.md) for detailed procedures.

### API Monitoring

The server automatically inherits API version tracking from the client:

```bash
# Monitor API changes
cd ..
uv run python monitor_api.py
```

## Architecture

```
teamsnap_mcp/
├── server.py           # MCP server with FastMCP
├── client.py           # Async TeamSnap API client
├── pyproject.toml      # Dependencies
├── .env.example        # Environment template
├── claude_desktop_config.json  # Claude Desktop config template
└── README.md          # This file
```

**Communication Flow**:
1. Claude Desktop → MCP Protocol (stdio) → server.py
2. server.py → client.py → TeamSnap API
3. TeamSnap API → client.py → server.py
4. server.py → MCP Protocol → Claude Desktop

## Resources

- **MCP Documentation**: https://modelcontextprotocol.io
- **FastMCP Python SDK**: https://github.com/jlowin/fastmcp
- **TeamSnap API**: https://api.teamsnap.com/v3/
- **Claude Desktop**: https://claude.ai/download

## Contributing

This is part of the TeamSnap integration demonstration project. Feel free to extend it for your needs!

## License

This project is provided as-is for demonstration purposes.

## Support

For TeamSnap API issues, contact TeamSnap support.
For MCP server issues, open an issue in the repository.
