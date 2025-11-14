# TeamSnap MCP Server - Quick Start

Get the TeamSnap MCP server running in Claude Desktop in 5 minutes.

## What You Need

1. Claude Desktop app installed
2. Python 3.12+ on your computer
3. A TeamSnap OAuth access token (from parent directory)

## Setup (3 Steps)

### Step 1: Get Your Access Token

If you haven't already authenticated:

```bash
# From parent directory
cd ..
uv run python teamsnap_auth.py
```

After authentication, your token is saved in `../config.ini`.

Copy the `access_token` value - you'll need it in Step 2.

### Step 2: Configure Environment

```bash
# In the teamsnap_mcp directory
cp .env.example .env
```

Edit `.env` and paste your access token:

```env
TEAMSNAP_ACCESS_TOKEN=your_actual_token_here
```

### Step 3: Add to Claude Desktop

Find your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration (replace the path with your actual absolute path):

```json
{
  "mcpServers": {
    "teamsnap": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/yourname/path/to/teamsnap_mcp",
        "python",
        "server.py"
      ],
      "env": {
        "TEAMSNAP_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

**Important Notes**:
- Use the ABSOLUTE path to the `teamsnap_mcp` directory
- Replace `your_access_token_here` with your actual token
- If you have other MCP servers, add this inside the existing `mcpServers` object

### Step 4: Restart Claude Desktop

Quit Claude Desktop completely and restart it.

## Verify It Works

In Claude Desktop, try asking:

> "List my TeamSnap teams"

If it works, you'll see your teams! 🎉

## What You Can Do

### View Data

- "Show me all teams"
- "What events are coming up for team [ID]?"
- "Who's on the roster for team [ID]?"
- "Who's available for event [ID]?"

### Manage Data

- "Create a practice on Jan 15 at 2pm for team [ID]"
- "Add John Doe as a member of team [ID]"
- "Update event [ID] to start at 3pm"
- "Mark availability [ID] as 'yes'"

## Troubleshooting

### Can't Find Config File

**macOS**: Open Terminal and run:
```bash
open "~/Library/Application Support/Claude"
```

**Windows**: Open Run dialog (Win+R) and type:
```
%APPDATA%\Claude
```

### Server Not Working

1. **Check the path is absolute**:
   - ✅ `/Users/name/Documents/teamsnap_mcp`
   - ❌ `~/Documents/teamsnap_mcp` (don't use ~)
   - ❌ `./teamsnap_mcp` (don't use relative paths)

2. **Check your token is valid**:
   ```bash
   # Re-authenticate if needed
   cd ..
   uv run python teamsnap_auth.py
   ```

3. **Check uv is installed**:
   ```bash
   uv --version
   ```

   If not installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Permission Errors

Make sure your TeamSnap account has access to the teams/events you're trying to view or modify.

## Next Steps

Once it's working:
- Check out [README.md](README.md) for full documentation
- See all available tools and their parameters
- Learn about security best practices

## Need Help?

See the full [README.md](README.md) for detailed documentation and troubleshooting.
