# Maintenance Guide

Best practices for keeping this TeamSnap integration up-to-date and secure.

## Automated Updates (Recommended)

### GitHub Dependabot (Enabled)

Dependabot automatically checks for dependency updates weekly and creates PRs:

- **When:** Every Monday at 9am UTC
- **What:** Checks Python packages and GitHub Actions
- **How:** Creates individual PRs for each update
- **Action:** Review and merge the PRs

### GitHub Actions Workflow (Enabled)

Weekly automated dependency updates via GitHub Actions:

- **File:** `.github/workflows/update-dependencies.yml`
- **When:** Every Monday at 9am UTC, or manually triggered
- **What:** Updates all dependencies and creates a single PR
- **Action:** Review, test locally, and merge

## Manual Updates

### Update All Dependencies

```bash
# Update to latest compatible versions
uv sync --upgrade

# Check what changed
git diff uv.lock
```

### Update Specific Package

```bash
# Update a specific package
uv add requests --upgrade

# Or edit pyproject.toml and run
uv sync
```

### Check for Outdated Packages

```bash
# List outdated packages (uv doesn't have this built-in yet)
# Use pip for this check:
uv pip list --outdated
```

## Python Version Updates

### Current: Python 3.8+

Update the Python version when a new version is released:

1. **Update `.python-version`:**
   ```bash
   echo "3.12" > .python-version
   ```

2. **Update `pyproject.toml`:**
   ```toml
   requires-python = ">=3.9"  # or newer
   ```

3. **Test with new version:**
   ```bash
   uv sync
   uv run python example.py
   ```

4. **Update CI workflows** if needed

### Python EOL Schedule

Stay current with supported Python versions:

- **Python 3.8:** EOL October 2024 (⚠️ Already EOL!)
- **Python 3.9:** EOL October 2025
- **Python 3.10:** EOL October 2026
- **Python 3.11:** EOL October 2027
- **Python 3.12:** EOL October 2028

**Recommendation:** Drop support for EOL versions to benefit from security updates.

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

### Review Security Advisories

Check GitHub's Security tab regularly for alerts.

## Testing Updates

### Before Merging Update PRs

1. **Pull the branch locally:**
   ```bash
   gh pr checkout <PR_NUMBER>
   ```

2. **Sync dependencies:**
   ```bash
   uv sync
   ```

3. **Test authentication:**
   ```bash
   uv run python teamsnap_auth.py
   ```

4. **Test API access:**
   ```bash
   uv run python example.py
   uv run python view_all_data.py
   ```

5. **If everything works, merge the PR**

### Add Automated Tests (Future)

Create a test suite to automatically verify updates:

```bash
# Create tests directory
mkdir tests

# Add test file
# tests/test_client.py
```

Then tests run automatically in CI on every PR.

## Monitoring API Changes

### TeamSnap API Updates

The TeamSnap API may change over time:

1. **Monitor:** Check https://api.teamsnap.com/v3/ periodically
2. **Version:** API version is in responses: `"version": "3.867.0"`
3. **Deprecations:** Watch for deprecation warnings in API responses

### Check API Compatibility

```bash
# Run the API explorer to see current endpoints
uv run python explore_api.py
```

If endpoints are missing or changed, update `teamsnap_client.py`.

## Maintenance Schedule

### Weekly (Automated)
- ✅ Dependabot checks for updates
- ✅ GitHub Actions creates update PRs

### Monthly (Manual)
- 🔍 Review and merge pending update PRs
- 🔍 Check for new Python versions
- 🔍 Review GitHub security alerts

### Quarterly (Manual)
- 🔍 Run API explorer to check for new endpoints
- 🔍 Update Python version if needed
- 🔍 Review and update documentation
- 🔍 Check TeamSnap API changelog

### Yearly (Manual)
- 🔍 Drop support for EOL Python versions
- 🔍 Major dependency upgrades
- 🔍 Review and refactor code if needed

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

When making breaking changes:

1. **Increment version** in `pyproject.toml`
2. **Update CHANGELOG** (create one if needed)
3. **Tag the release** in git
4. **Document migration** steps in README

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

## Troubleshooting

### "Package not found" errors
```bash
# Clear cache and retry
uv cache clean
uv sync
```

### Version conflicts
```bash
# Check what's causing the conflict
uv tree | grep <package-name>

# Pin specific versions in pyproject.toml if needed
```

### API authentication fails after update
- Re-authenticate: `uv run python teamsnap_auth.py`
- Check if TeamSnap changed OAuth endpoints
- Review update PR for breaking changes

## Resources

- **uv docs:** https://docs.astral.sh/uv/
- **Python EOL:** https://endoflife.date/python
- **TeamSnap API:** https://api.teamsnap.com/v3/
- **Security:** https://github.com/pyupio/safety

## Questions?

Open an issue in the repository for maintenance questions or problems with updates.
