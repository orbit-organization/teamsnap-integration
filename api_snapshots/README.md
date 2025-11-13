# API Snapshots

This directory stores snapshots of the TeamSnap API state over time.

## Files

- `latest.json` - Most recent API state
- `snapshot_YYYYMMDD_HHMMSS.json` - Timestamped snapshots

## Purpose

These snapshots are used to detect changes in the TeamSnap API:
- Version number changes
- New or removed endpoints
- Deprecation warnings
- Structural changes

## Usage

```bash
# Create a snapshot
uv run python monitor_api.py --save

# Compare current state with previous snapshot
uv run python monitor_api.py --compare
```

## Automated Monitoring

GitHub Actions automatically runs API monitoring weekly and creates snapshots.
Check the Actions tab for monitoring results.

## Manual Review

You can manually review snapshot files to see the API state at any point in time:

```bash
cat api_snapshots/latest.json | jq
```

## Retention

Snapshots are kept indefinitely to track API evolution over time.
If the directory becomes too large, old snapshots can be safely deleted.
