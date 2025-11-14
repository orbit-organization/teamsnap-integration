# Maintenance Guide - TeamSnap MCP Server

Best practices for keeping the TeamSnap MCP server up-to-date and secure.

## Automated Updates (Recommended)

### GitHub Dependabot (Enabled)

Dependabot automatically checks for dependency updates weekly and creates PRs.

- **When:** Every Monday at 9am UTC
- **What:** Checks Python packages and GitHub Actions
- **How:** Creates individual PRs for each update
- **Action:** Review and merge the PRs

### GitHub Actions Workflow (Enabled)

Weekly automated dependency updates via GitHub Actions.

- **File:** `.github/workflows/mcp-update-dependencies.yml`
- **When:** Every Monday at 9am UTC, or manually triggered
- **What:** Updates all MCP server dependencies and creates a single PR
- **Action:** Review, test locally, and merge

## Manual Updates

### Update All Dependencies

```bash
# From teamsnap_mcp directory
uv sync --upgrade

# Check what changed
git diff uv.lock
```

### Update Specific Package

```bash
# Update a specific package
uv add mcp --upgrade

# Or edit pyproject.toml and run
uv sync
```

### Update FastMCP

```bash
# Check for FastMCP updates
uv add "mcp[cli]" --upgrade
```

## Python Version Updates

### Current: Python 3.12+

Update the Python version when a new version is released:

1. **Update `.python-version`** (if you have one):
   ```bash
   echo "3.13" > .python-version
   ```

2. **Update `pyproject.toml`**:
   ```toml
   requires-python = ">=3.12"  # or newer
   ```

3. **Test with new version**:
   ```bash
   uv sync
   # Test the server manually
   ```

4. **Update CI workflows** in `.github/workflows/`

### Python EOL Schedule

- **Python 3.12:** EOL October 2028
- **Python 3.13:** EOL October 2029

## Security Updates

### Automated Security Scanning

GitHub automatically scans for security vulnerabilities in dependencies.

**To enable:**
1. Go to repository Settings → Security → Dependabot
2. Enable "Dependabot security updates"
3. Security PRs will be created automatically

### Manual Security Check

```bash
# Install safety (security checker)
uv add --dev safety

# Run security audit
uv run safety check
```

## Testing Updates

### Before Merging Update PRs

1. **Pull the branch locally**:
   ```bash
   gh pr checkout <PR_NUMBER>
   ```

2. **Sync dependencies**:
   ```bash
   cd teamsnap_mcp
   uv sync
   ```

3. **Test the server**:
   ```bash
   # Set environment variable
   export TEAMSNAP_ACCESS_TOKEN="your_token"

   # Run tests
   uv run pytest tests/ -v
   ```

4. **Test in Claude Desktop**:
   - Restart Claude Desktop
   - Try basic operations (list teams, list events)
   - Try write operations (create/update/delete)

5. **If everything works, merge the PR**

## Monitoring API Changes

The MCP server uses the same TeamSnap API as the parent integration, so it benefits from the same API monitoring.

### Automated API Monitoring (Enabled)

**GitHub Actions Workflow:** `../.github/workflows/monitor-api.yml`
- **When:** Every Monday at 10am UTC
- **What:** Checks for API version changes, new/removed endpoints, deprecations
- **Action:** Creates GitHub issue if changes detected

### Manual API Monitoring

```bash
# From parent directory
cd ..

# Check current API state
uv run python monitor_api.py

# Compare with previous state
uv run python monitor_api.py --compare

# Show deprecations
uv run python monitor_api.py --show-deprecations
```

### What to Watch For

**Version Changes:**
- Major version changes (v3 → v4) require code updates in client.py
- Minor version changes usually backward compatible

**Deprecation Warnings:**
- Update client.py to use replacement endpoints
- Test all MCP tools still work

**New Endpoints:**
- Consider adding new MCP tools for new functionality
- Update documentation

**Removed Endpoints:**
- Breaking change - immediate action required
- Update client.py and affected tools

## Token Management

### Rotating Access Tokens

TeamSnap OAuth tokens expire. To refresh:

```bash
# From parent directory
cd ..
uv run python teamsnap_auth.py
```

Then update your token in:
1. `.env` file (for local testing)
2. Claude Desktop config (for production use)
3. GitHub Secrets (if using CI/CD)

### Token Expiration

- Default token lifetime: 2 hours
- Refresh tokens can extend this
- Monitor for 401 errors indicating expired tokens

## Maintenance Schedule

### Weekly (Automated)
- ✅ Dependabot checks for updates
- ✅ GitHub Actions creates update PRs
- ✅ API monitoring checks for changes (parent directory)
- ✅ API snapshots saved automatically

### Monthly (Manual)
- 🔍 Review and merge pending update PRs
- 🔍 Check for new Python versions
- 🔍 Review GitHub security alerts
- 🔍 Review API monitoring issues (if any)
- 🔍 Test MCP server in Claude Desktop

### Quarterly (Manual)
- 🔍 Test all MCP tools comprehensively
- 🔍 Update Python version if needed
- 🔍 Review and update documentation
- 🔍 Check for new TeamSnap API endpoints to add
- 🔍 Rotate OAuth tokens

### Yearly (Manual)
- 🔍 Drop support for EOL Python versions
- 🔍 Major dependency upgrades
- 🔍 Review and refactor code if needed
- 🔍 Update MCP protocol version if needed

## Keeping uv Up-to-Date

Update the `uv` tool itself:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with brew
brew upgrade uv

# Check version
uv --version
```

## Breaking Changes

When making breaking changes to the MCP server:

1. **Increment version** in `pyproject.toml`
2. **Update CHANGELOG** (create one if needed)
3. **Tag the release** in git
4. **Update README** with migration steps
5. **Notify users** via GitHub release notes

## Useful Commands

```bash
# Check what would be updated
uv sync --upgrade --dry-run

# Update and show changes
uv sync --upgrade --verbose

# Lock dependencies without installing
uv lock --upgrade

# Reinstall everything from scratch
rm -rf .venv uv.lock
uv sync

# View dependency tree
uv tree
```

## MCP Protocol Updates

The Model Context Protocol is actively developed. Stay current:

### Check for MCP Updates

```bash
# Check current version
uv run python -c "import mcp; print(mcp.__version__)"

# Update MCP
uv add "mcp[cli]" --upgrade
```

### Migration Steps

If MCP releases a breaking change:

1. **Read release notes**: Check MCP changelog
2. **Update code**: Modify server.py for new API
3. **Test thoroughly**: Verify all tools still work
4. **Update docs**: Document any changes
5. **Version bump**: Increment version in pyproject.toml

## Troubleshooting

### Dependencies Not Installing

```bash
# Clear cache and retry
uv cache clean
uv sync
```

### Version Conflicts

```bash
# Check what's causing the conflict
uv tree | grep <package-name>

# Pin specific versions in pyproject.toml if needed
```

### Server Crashes After Update

1. Check Python version compatibility
2. Review MCP package changelog
3. Test with previous version to isolate issue
4. Check GitHub issues for similar problems

### Claude Desktop Not Loading Server

1. Verify config file syntax (valid JSON)
2. Check absolute paths are correct
3. Ensure uv is in PATH
4. Check Claude Desktop logs for errors

## Resources

- **uv docs:** https://docs.astral.sh/uv/
- **MCP docs:** https://modelcontextprotocol.io
- **FastMCP:** https://github.com/jlowin/fastmcp
- **Python EOL:** https://endoflife.date/python
- **TeamSnap API:** https://api.teamsnap.com/v3/
- **Security:** https://github.com/pyupio/safety

## Questions?

Open an issue in the repository for maintenance questions or problems with updates.
