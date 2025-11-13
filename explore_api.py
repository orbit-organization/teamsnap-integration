"""
Explore TeamSnap API to discover all available endpoints
"""

from teamsnap_client import TeamSnapClient
import json


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def explore_links(links, indent=0):
    """Recursively explore links in the API"""
    prefix = "  " * indent
    for link in links:
        rel = link.get('rel', 'unknown')
        href = link.get('href', '')
        print(f"{prefix}- {rel}: {href}")


def main():
    print("\n🔍 TeamSnap API Explorer")
    print("   Discovering all available endpoints...\n")

    try:
        client = TeamSnapClient()

        # Get API root
        print_section("1. API Root - Available Endpoints")
        root = client.get_root()

        # Show structure
        print("\nRoot response structure:")
        print(f"  Keys: {list(root.keys())}")

        if 'collection' in root:
            collection = root['collection']
            print(f"\n  Collection keys: {list(collection.keys())}")

            # Show links (available endpoints)
            if 'links' in collection:
                print("\n📋 Available API Endpoints (links):")
                explore_links(collection['links'], indent=1)

            # Show queries (search endpoints)
            if 'queries' in collection:
                print("\n🔍 Available Search Queries:")
                for query in collection['queries']:
                    rel = query.get('rel', 'unknown')
                    href = query.get('href', '')
                    print(f"  - {rel}: {href}")

            # Show commands (actions)
            if 'commands' in collection:
                print("\n⚡ Available Commands (actions):")
                for command in collection['commands']:
                    rel = command.get('rel', 'unknown')
                    href = command.get('href', '')
                    method = command.get('method', 'unknown')
                    print(f"  - {rel} ({method}): {href}")

        # Get user info to find team ID
        print_section("2. Getting User and Team Info")
        me = client.get_me()
        items = me.get('collection', {}).get('items', [])
        if items:
            user_data = items[0].get('data', [])
            user_id = None
            for item in user_data:
                if item.get('name') == 'id':
                    user_id = item.get('value')
                    print(f"  User ID: {user_id}")
                    break

            # Get teams
            teams_response = client.search_teams(user_id=int(user_id))
            if teams_response:
                team_data = teams_response[0].get('data', [])
                team_id = None
                team_name = None
                for item in team_data:
                    if item.get('name') == 'id':
                        team_id = item.get('value')
                    if item.get('name') == 'name':
                        team_name = item.get('value')

                print(f"  Team ID: {team_id}")
                print(f"  Team Name: {team_name}")

                # Explore team-specific endpoints
                print_section("3. Testing Additional Endpoints")

                endpoints_to_test = [
                    ('broadcast_emails', f'/broadcast_emails/search?team_id={team_id}'),
                    ('broadcast_email_attachments', f'/broadcast_email_attachments/search?team_id={team_id}'),
                    ('messages', f'/messages/search?team_id={team_id}'),
                    ('forum_posts', f'/forum_posts/search?team_id={team_id}'),
                    ('forum_topics', f'/forum_topics/search?team_id={team_id}'),
                    ('assignments', f'/assignments/search?team_id={team_id}'),
                    ('availabilities', f'/availabilities/search?team_id={team_id}'),
                    ('contacts', f'/contacts/search?team_id={team_id}'),
                    ('custom_fields', f'/custom_fields/search?team_id={team_id}'),
                    ('invoices', f'/invoices/search?team_id={team_id}'),
                    ('payments', f'/payments/search?team_id={team_id}'),
                ]

                for name, endpoint in endpoints_to_test:
                    try:
                        print(f"\n  Testing {name}...")
                        response = client.get(endpoint)
                        items = response.get('collection', {}).get('items', [])
                        print(f"    ✓ Found {len(items)} {name}")

                        # Show first item if exists
                        if items:
                            print(f"    First item data fields:")
                            first_item = items[0].get('data', [])
                            field_names = [field.get('name') for field in first_item[:10]]
                            print(f"      {', '.join(field_names)}")
                    except Exception as e:
                        print(f"    ✗ Error: {str(e)[:50]}")

        print_section("✓ API Exploration Complete!")
        print("\nCheck the output above to see what data is available.\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
