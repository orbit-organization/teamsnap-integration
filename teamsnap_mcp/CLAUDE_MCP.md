# Claude Code Guide - TeamSnap MCP Server

This guide helps future Claude Code instances understand and work with the TeamSnap MCP server effectively.

## Quick Context

This is a Model Context Protocol (MCP) server that gives Claude Desktop read/write access to the TeamSnap API. The server runs locally and communicates with Claude via stdio.

**Parent Project**: This is part of the larger TeamSnap integration project. See `../CLAUDE.md` for overall context.

## Essential Commands

### Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_client.py -v

# Run with coverage
uv run pytest tests/ --cov=. --cov-report=html
```

### Development
```bash
# Install dependencies
uv sync

# Update dependencies
uv sync --upgrade

# Run server manually (for testing)
export TEAMSNAP_ACCESS_TOKEN="your_token"
uv run python server.py

# Check imports work
uv run python -c "from client import TeamSnapAsyncClient; print('OK')"
uv run python -c "from server import app; print('OK')"
```

### Configuration
```bash
# Set up environment
cp .env.example .env
# Then edit .env with your access token

# Get access token from parent directory
cd ..
uv run python teamsnap_auth.py
# Copy token from config.ini to teamsnap_mcp/.env
```

## Project Structure

```
teamsnap_mcp/
├── server.py              # MCP server with FastMCP (@app.tool() decorators)
├── client.py              # Async TeamSnap API client (httpx)
├── tests/                 # Test suite
│   ├── conftest.py       # Shared fixtures
│   ├── test_client.py    # Client tests
│   └── test_server.py    # Server/tool tests
├── pyproject.toml        # Dependencies (mcp[cli], httpx, python-dotenv)
├── .env.example          # Environment template
├── .env                  # Actual environment (gitignored)
├── claude_desktop_config.json  # Claude Desktop config template
├── README.md            # Full documentation
├── QUICKSTART.md        # Quick setup guide
└── MAINTENANCE.md       # Maintenance procedures
```

## Architecture

### Communication Flow
```
Claude Desktop
    ↕️ (MCP Protocol via stdio)
server.py (@app.tool() functions)
    ↕️
client.py (TeamSnapAsyncClient)
    ↕️ (HTTP/JSON)
TeamSnap API v3
```

### Key Components

**server.py**:
- FastMCP server using `@app.tool()` decorators
- Each tool returns `list[TextContent]`
- Tools are async functions
- Uses context manager pattern for client instances
- Error handling returns user-friendly messages

**client.py**:
- Async HTTP client using httpx
- Mirrors sync client from parent directory but async
- Includes read operations (search_teams, search_events, etc.)
- Includes write operations (create_event, update_member, etc.)
- Uses environment variable for access token
- Context manager support (`async with client:`)

**tests/**:
- pytest with pytest-asyncio
- Mock-based testing (no real API calls)
- Tests for import, functionality, error handling
- Shared fixtures in conftest.py

## MCP-Specific Details

### Tool Definition Pattern

```python
@app.tool()
async def tool_name(param: Type) -> list[TextContent]:
    """
    Tool description that Claude sees.

    Args:
        param: Parameter description

    Returns:
        Result description
    """
    async with get_client() as client:
        try:
            result = await client.api_method()
            return [TextContent(type="text", text="Success message")]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error: {str(e)}")]
```

### Important MCP Patterns

1. **Always return `list[TextContent]`**
   - Even single results should be in a list
   - Use `TextContent(type="text", text="...")`

2. **Use async context managers**
   - `async with get_client() as client:`
   - Ensures proper cleanup

3. **User-friendly messages**
   - Use emojis (✅, ❌, 📋, 🔍)
   - Clear success/failure indicators
   - Include relevant IDs and details

4. **Error handling**
   - Catch all exceptions
   - Return errors as TextContent (don't raise)
   - Include helpful troubleshooting hints

### Claude Desktop Configuration

Users add this to their Claude Desktop config:

```json
{
  "mcpServers": {
    "teamsnap": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/teamsnap_mcp", "python", "server.py"],
      "env": {"TEAMSNAP_ACCESS_TOKEN": "token_here"}
    }
  }
}
```

**Critical**: Path must be absolute, not relative!

## Common Tasks

### Adding a New Tool

1. **Add client method** (if needed) to `client.py`:
```python
async def new_operation(self, param: Type) -> Dict[str, Any]:
    """Method docstring"""
    return await self.get(f'/endpoint/{param}')
```

2. **Add server tool** to `server.py`:
```python
@app.tool()
async def new_tool(param: Type) -> list[TextContent]:
    """Tool description for Claude"""
    async with get_client() as client:
        result = await client.new_operation(param)
        # Format and return TextContent
        return [TextContent(type="text", text="...")]
```

3. **Add tests** to `tests/test_server.py`:
```python
@pytest.mark.asyncio
async def test_new_tool(mock_env):
    from server import new_tool
    # Test with mocks
```

4. **Update documentation** in `README.md`:
   - Add to "Available Tools" section
   - Add usage example

### Debugging Tools

**Tool not appearing in Claude**:
- Check `@app.tool()` decorator is present
- Verify function signature is correct
- Check Claude Desktop config path is absolute
- Restart Claude Desktop completely

**Tool errors**:
- Check client method works: `uv run python -c "from client import TeamSnapAsyncClient; ..."`
- Add logging: `import logging; logging.basicConfig(level=logging.DEBUG)`
- Check `.env` file has valid token
- Verify TeamSnap API permissions

**Import errors**:
- Run: `uv sync`
- Check Python version: `python --version` (must be 3.12+)
- Check all imports in server.py resolve

### Testing Patterns

**Test client method**:
```python
@pytest.mark.asyncio
async def test_method(mock_env):
    with patch.object(TeamSnapAsyncClient, 'get', new_callable=AsyncMock) as mock:
        mock.return_value = {"data": "value"}
        async with TeamSnapAsyncClient() as client:
            result = await client.method()
            assert result == {"data": "value"}
```

**Test server tool**:
```python
@pytest.mark.asyncio
async def test_tool(mock_env):
    with patch.object(TeamSnapAsyncClient, 'method', new_callable=AsyncMock) as mock:
        mock.return_value = sample_data
        result = await tool_function()
        assert isinstance(result, list)
        assert result[0].type == "text"
```

## TeamSnap API Integration

The MCP server uses the same TeamSnap API as the parent project:

- **Base URL**: https://api.teamsnap.com/v3
- **Format**: Collection+JSON (need to extract data)
- **Auth**: OAuth 2.0 Bearer token
- **Tokens**: Expire after ~2 hours (need refresh)

### Collection+JSON Parsing

TeamSnap returns data like this:
```json
{
  "collection": {
    "items": [{
      "data": [
        {"name": "id", "value": 123},
        {"name": "name", "value": "Team Name"}
      ]
    }]
  }
}
```

Extract with:
```python
data = client.extract_item_data(item)
# Now: data = {"id": 123, "name": "Team Name"}
```

## Maintenance

### Dependencies
- **Automated**: Dependabot + GitHub Actions (weekly)
- **Manual**: `uv sync --upgrade`
- **Test after update**: `uv run pytest tests/ -v`

### API Monitoring
- Inherits from parent project's API monitoring
- See `../monitor_api.py`
- Weekly automated checks via GitHub Actions

### Token Rotation
```bash
# Get new token
cd ..
uv run python teamsnap_auth.py

# Update .env
cd teamsnap_mcp
# Edit .env with new token from ../config.ini

# Restart Claude Desktop
```

## Security Notes

1. **Never commit `.env`** - Contains access token
2. **Use environment variables** - Don't hardcode tokens
3. **Gitignore is set up** - `.env` is excluded
4. **Token expiry** - Monitor for 401 errors
5. **Permissions** - Verify TeamSnap account access

## Troubleshooting

### Server won't start in Claude Desktop
1. Check config path is absolute: `/Users/name/...` not `~/...`
2. Verify uv is in PATH: `which uv`
3. Check `.env` exists and has token
4. Look for errors in Claude Desktop logs

### Tests failing
1. Ensure test env var is set: `export TEAMSNAP_ACCESS_TOKEN=test_token`
2. Update dependencies: `uv sync`
3. Check Python version: `uv run python --version`
4. Clear pytest cache: `rm -rf .pytest_cache`

### Import errors in tools
1. Verify client.py syntax: `uv run python -m py_compile client.py`
2. Check all dependencies installed: `uv sync`
3. Test imports directly: `uv run python -c "from client import TeamSnapAsyncClient"`

## Differences from Parent Project

| Feature | Parent (teamsnap_client.py) | MCP Server (client.py) |
|---------|----------------------------|------------------------|
| HTTP Library | requests (sync) | httpx (async) |
| Auth | config.ini file | Environment variable |
| Methods | Sync | Async (await) |
| Context | Can re-auth interactively | No interactive prompts |
| Imports | Can be imported anywhere | Only in MCP server context |

## Resources

- **MCP Protocol**: https://modelcontextprotocol.io
- **FastMCP**: https://github.com/jlowin/fastmcp
- **TeamSnap API**: https://api.teamsnap.com/v3
- **Parent Project**: See `../CLAUDE.md`
- **Maintenance**: See `MAINTENANCE.md`

## Development Workflow

**Typical workflow when adding features**:

1. Understand requirement
2. Check if TeamSnap API supports it (see `../explore_api.py`)
3. Add async method to `client.py`
4. Add `@app.tool()` to `server.py`
5. Write tests in `tests/`
6. Update README.md
7. Test in Claude Desktop
8. Commit changes

**Before committing**:
- ✅ Run tests: `uv run pytest tests/ -v`
- ✅ Check imports: `uv run python -c "from server import app"`
- ✅ Update docs if needed
- ✅ Verify `.env` not in commit
