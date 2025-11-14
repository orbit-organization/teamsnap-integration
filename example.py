"""
TeamSnap Integration Example

This script demonstrates how to use the TeamSnap API client to:
1. Authenticate with TeamSnap
2. Get user information
3. List teams
4. Get team details and members
5. List events
"""

import json
from teamsnap_client import TeamSnapClient


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent))


def safe_get(data, *keys, default="N/A"):
    """Safely get nested dictionary values"""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result if result != "" else default


def main():
    """Main example function"""

    print("\n🚀 TeamSnap Integration Example")
    print("   This will authenticate and fetch data from TeamSnap API")

    try:
        # Initialize client (will auto-authenticate if needed)
        print_section("1. Initializing TeamSnap Client")
        client = TeamSnapClient()
        print("✓ Client initialized successfully!")

        # Get current user information
        print_section("2. Getting Current User Information")
        me_response = client.get_me()

        # TeamSnap uses Collection+JSON format
        items = safe_get(me_response, "collection", "items", default=[])

        if items:
            user_data = items[0].get("data", [])

            # Extract user information from data array
            user_info = {}
            for item in user_data:
                name = item.get("name")
                value = item.get("value")
                if name and value:
                    user_info[name] = value

            print("\n📋 User Information:")
            print(f"   ID: {user_info.get('id', 'N/A')}")
            print(f"   First Name: {user_info.get('first_name', 'N/A')}")
            print(f"   Last Name: {user_info.get('last_name', 'N/A')}")
            print(f"   Email: {user_info.get('email', 'N/A')}")
            print(f"   Birthday: {user_info.get('birthday', 'N/A')}")

            user_id = user_info.get("id")

            # Get teams for this user
            if user_id:
                print_section("3. Getting User's Teams")
                teams_response = client.search_teams(user_id=int(user_id))

                print(f"\n✓ Found {len(teams_response)} team(s)")

                if teams_response:
                    for idx, team_item in enumerate(
                        teams_response[:5], 1
                    ):  # Show first 5 teams
                        team_data = team_item.get("data", [])
                        team_info = {}
                        for item in team_data:
                            name = item.get("name")
                            value = item.get("value")
                            if name:
                                team_info[name] = value

                        print(f"\n   Team #{idx}:")
                        print(f"      ID: {team_info.get('id', 'N/A')}")
                        print(f"      Name: {team_info.get('name', 'N/A')}")
                        print(f"      Sport: {team_info.get('sport_name', 'N/A')}")
                        print(
                            f"      Location: {team_info.get('location_country', 'N/A')}"
                        )
                        print(
                            f"      Division: {team_info.get('division_name', 'N/A')}"
                        )

                        # Get details for first team
                        if idx == 1 and team_info.get("id"):
                            team_id = int(team_info["id"])

                            # Get team members
                            print_section(
                                f"4. Getting Members for Team: {team_info.get('name')}"
                            )
                            members_response = client.search_members(team_id=team_id)

                            print(f"\n✓ Found {len(members_response)} member(s)")

                            for member_idx, member_item in enumerate(
                                members_response[:5], 1
                            ):  # Show first 5
                                member_data = member_item.get("data", [])
                                member_info = {}
                                for item in member_data:
                                    name = item.get("name")
                                    value = item.get("value")
                                    if name:
                                        member_info[name] = value

                                print(f"\n   Member #{member_idx}:")
                                print(f"      ID: {member_info.get('id', 'N/A')}")
                                print(
                                    f"      First Name: {member_info.get('first_name', 'N/A')}"
                                )
                                print(
                                    f"      Last Name: {member_info.get('last_name', 'N/A')}"
                                )
                                print(
                                    f"      Position: {member_info.get('position', 'N/A')}"
                                )
                                print(
                                    f"      Jersey Number: {member_info.get('jersey_number', 'N/A')}"
                                )

                            # Get team events
                            print_section(
                                f"5. Getting Events for Team: {team_info.get('name')}"
                            )
                            events_response = client.search_events(team_id=team_id)

                            print(f"\n✓ Found {len(events_response)} event(s)")

                            for event_idx, event_item in enumerate(
                                events_response[:5], 1
                            ):  # Show first 5
                                event_data = event_item.get("data", [])
                                event_info = {}
                                for item in event_data:
                                    name = item.get("name")
                                    value = item.get("value")
                                    if name:
                                        event_info[name] = value

                                print(f"\n   Event #{event_idx}:")
                                print(f"      ID: {event_info.get('id', 'N/A')}")
                                print(f"      Name: {event_info.get('name', 'N/A')}")
                                print(f"      Type: {event_info.get('type', 'N/A')}")
                                print(
                                    f"      Start: {event_info.get('start_date', 'N/A')}"
                                )
                                print(
                                    f"      Location: {event_info.get('location_name', 'N/A')}"
                                )
                                notes = event_info.get("notes") or "N/A"
                                notes_display = (
                                    notes[:50] + "..." if len(notes) > 50 else notes
                                )
                                print(f"      Notes: {notes_display}")

                else:
                    print("\n⚠️  No teams found for this user")
                    print("   This might be because:")
                    print("   - Your account doesn't manage any teams")
                    print("   - You need additional permissions")
                    print("   - You're not a member of any teams")
        else:
            print("\n⚠️  Could not extract user information from response")
            print("\nRaw response structure:")
            print_json(me_response)

        # Success!
        print_section("✓ Example Complete!")
        print("\n🎉 Successfully demonstrated TeamSnap API integration!")
        print("\nYou can now:")
        print("   - Modify this script to access other endpoints")
        print("   - Use the TeamSnapClient class in your own applications")
        print("   - Explore the full API at: https://api.teamsnap.com/v3/")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
