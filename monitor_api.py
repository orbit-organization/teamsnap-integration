"""
TeamSnap API Monitoring Script

Comprehensive monitoring tool to detect API changes, version updates,
new/removed endpoints, and deprecation warnings.

Usage:
    uv run python monitor_api.py              # Run monitoring check
    uv run python monitor_api.py --save       # Save current API state as snapshot
    uv run python monitor_api.py --compare    # Compare with previous snapshot
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from teamsnap_client import TeamSnapClient


SNAPSHOTS_DIR = Path("api_snapshots")
LATEST_SNAPSHOT = SNAPSHOTS_DIR / "latest.json"


def print_section(title, symbol="="):
    """Print a formatted section header"""
    print("\n" + symbol * 70)
    print(f" {title}")
    print(symbol * 70)


def get_current_api_state(client):
    """
    Get current state of the TeamSnap API

    Returns:
        Dictionary containing API version, endpoints, and metadata
    """
    print("📡 Fetching current API state...")

    root = client.get_root()
    collection = root.get("collection", {})

    # Extract API version
    version = collection.get("version")

    # Extract all available endpoints
    links = collection.get("links", [])
    queries = collection.get("queries", [])
    commands = collection.get("commands", [])

    # Build endpoint lists
    endpoints = {
        "links": [
            {
                "rel": link.get("rel"),
                "href": link.get("href"),
                "deprecated": link.get("deprecated", False),
            }
            for link in links
        ],
        "queries": [
            {"rel": query.get("rel"), "href": query.get("href")} for query in queries
        ],
        "commands": [
            {
                "rel": cmd.get("rel"),
                "href": cmd.get("href"),
                "method": cmd.get("method"),
            }
            for cmd in commands
        ],
    }

    # Find deprecations
    deprecated_endpoints = [link for link in endpoints["links"] if link["deprecated"]]

    state = {
        "timestamp": datetime.now().isoformat(),
        "version": version,
        "endpoints": endpoints,
        "deprecated_count": len(deprecated_endpoints),
        "deprecated_endpoints": deprecated_endpoints,
        "total_links": len(endpoints["links"]),
        "total_queries": len(endpoints["queries"]),
        "total_commands": len(endpoints["commands"]),
    }

    return state


def save_snapshot(state, filename=None):
    """
    Save API state to a snapshot file

    Args:
        state: API state dictionary
        filename: Optional filename (default: uses timestamp)
    """
    SNAPSHOTS_DIR.mkdir(exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = SNAPSHOTS_DIR / f"snapshot_{timestamp}.json"
    else:
        filename = SNAPSHOTS_DIR / filename

    with open(filename, "w") as f:
        json.dump(state, f, indent=2)

    # Also save as latest
    with open(LATEST_SNAPSHOT, "w") as f:
        json.dump(state, f, indent=2)

    print(f"✓ Snapshot saved to: {filename}")


def load_snapshot(filename=LATEST_SNAPSHOT):
    """
    Load API state from a snapshot file

    Args:
        filename: Path to snapshot file

    Returns:
        API state dictionary or None if file doesn't exist
    """
    if not Path(filename).exists():
        return None

    with open(filename, "r") as f:
        return json.load(f)


def compare_states(old_state, new_state):
    """
    Compare two API states and report differences

    Args:
        old_state: Previous API state
        new_state: Current API state

    Returns:
        Dictionary of changes
    """
    changes = {
        "version_changed": old_state["version"] != new_state["version"],
        "old_version": old_state["version"],
        "new_version": new_state["version"],
        "new_endpoints": [],
        "removed_endpoints": [],
        "new_deprecations": [],
        "deprecated_count_changed": old_state["deprecated_count"]
        != new_state["deprecated_count"],
    }

    # Compare endpoints
    old_rels = {link["rel"] for link in old_state["endpoints"]["links"]}
    new_rels = {link["rel"] for link in new_state["endpoints"]["links"]}

    changes["new_endpoints"] = list(new_rels - old_rels)
    changes["removed_endpoints"] = list(old_rels - new_rels)

    # Compare deprecations
    old_deprecated = {link["rel"] for link in old_state["deprecated_endpoints"]}
    new_deprecated = {link["rel"] for link in new_state["deprecated_endpoints"]}

    changes["new_deprecations"] = list(new_deprecated - old_deprecated)

    return changes


def print_current_state(state):
    """Print current API state"""
    print_section("TeamSnap API Current State")

    print(f"\n📅 Timestamp: {state['timestamp']}")
    print(f"🔢 API Version: {state['version']}")
    print("\n📊 Endpoint Counts:")
    print(f"   Links: {state['total_links']}")
    print(f"   Queries: {state['total_queries']}")
    print(f"   Commands: {state['total_commands']}")
    print(f"\n⚠️  Deprecated Endpoints: {state['deprecated_count']}")

    if state["deprecated_endpoints"]:
        print("\n🔻 Currently Deprecated:")
        for endpoint in state["deprecated_endpoints"]:
            print(f"   - {endpoint['rel']}: {endpoint['href']}")


def print_comparison(changes):
    """Print comparison results"""
    print_section("API Change Detection", symbol="-")

    has_changes = False

    if changes["version_changed"]:
        has_changes = True
        print("\n🔄 VERSION CHANGE DETECTED!")
        print(f"   Old: {changes['old_version']}")
        print(f"   New: {changes['new_version']}")

    if changes["new_endpoints"]:
        has_changes = True
        print(f"\n✨ NEW ENDPOINTS ({len(changes['new_endpoints'])}):")
        for endpoint in changes["new_endpoints"]:
            print(f"   + {endpoint}")

    if changes["removed_endpoints"]:
        has_changes = True
        print(f"\n🗑️  REMOVED ENDPOINTS ({len(changes['removed_endpoints'])}):")
        for endpoint in changes["removed_endpoints"]:
            print(f"   - {endpoint}")

    if changes["new_deprecations"]:
        has_changes = True
        print(f"\n⚠️  NEWLY DEPRECATED ({len(changes['new_deprecations'])}):")
        for endpoint in changes["new_deprecations"]:
            print(f"   ⚠️  {endpoint}")

    if changes["deprecated_count_changed"] and not changes["new_deprecations"]:
        has_changes = True
        print("\n📊 Deprecation count changed (may indicate removals)")

    if not has_changes:
        print("\n✅ No API changes detected")
        print("   The API appears stable since the last snapshot.")

    return has_changes


def main():
    parser = argparse.ArgumentParser(description="Monitor TeamSnap API for changes")
    parser.add_argument(
        "--save", action="store_true", help="Save current API state as snapshot"
    )
    parser.add_argument(
        "--compare", action="store_true", help="Compare with previous snapshot"
    )
    parser.add_argument(
        "--show-deprecations", action="store_true", help="Show all deprecated endpoints"
    )
    args = parser.parse_args()

    try:
        # Initialize client
        print("🚀 TeamSnap API Monitor")
        print("   Initializing client...\n")

        client = TeamSnapClient()

        # Get current state
        current_state = get_current_api_state(client)

        if args.save:
            # Just save and exit
            print_section("Saving API Snapshot")
            save_snapshot(current_state)
            print("\n✓ Snapshot saved successfully")
            return

        # Always show current state
        print_current_state(current_state)

        if args.show_deprecations:
            # Show deprecation details
            print_section("Deprecation Details")
            deprecated = client.check_for_deprecations("/")
            if deprecated:
                for item in deprecated:
                    print(f"\n⚠️  {item['rel']}")
                    print(f"   Description: {item['prompt']}")
                    print(f"   URL: {item['href']}")
            else:
                print("\n✅ No deprecated endpoints found")

        if args.compare:
            # Load previous snapshot and compare
            print_section("Comparing with Previous Snapshot")

            previous_state = load_snapshot()
            if previous_state is None:
                print("\n⚠️  No previous snapshot found")
                print("   Run with --save to create the first snapshot")
            else:
                print(f"\nPrevious snapshot: {previous_state['timestamp']}")
                print(f"Current check: {current_state['timestamp']}")

                changes = compare_states(previous_state, current_state)
                has_changes = print_comparison(changes)

                if has_changes:
                    print(
                        "\n💡 Tip: Review changes and update your integration if needed"
                    )

        # Auto-save latest state
        save_snapshot(current_state)

        print_section("✓ Monitoring Complete")
        print(f"\n📁 Snapshots stored in: {SNAPSHOTS_DIR.absolute()}")
        print("\nUsage:")
        print("  uv run python monitor_api.py              # Check current state")
        print("  uv run python monitor_api.py --compare    # Compare with previous")
        print("  uv run python monitor_api.py --show-deprecations  # Show details")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
