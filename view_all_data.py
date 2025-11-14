"""
View All TeamSnap Data

Comprehensive viewer to see all data in your TeamSnap account including:
- User info
- Teams
- Members
- Events
- Forum topics and posts
- Broadcast emails
- Messages
- Assignments
- And more!
"""

from teamsnap_client import TeamSnapClient


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def extract_data(item):
    """Extract data from Collection+JSON format"""
    data_array = item.get("data", [])
    result = {}
    for field in data_array:
        name = field.get("name")
        value = field.get("value")
        if name:
            result[name] = value
    return result


def main():
    print("\n📊 TeamSnap Complete Data Viewer")
    print("   Fetching all available data from your account...\n")

    try:
        client = TeamSnapClient()

        # Get user info
        print_section("👤 Current User")
        me = client.get_me()
        user_items = me.get("collection", {}).get("items", [])

        if user_items:
            user_data = extract_data(user_items[0])
            print(
                f"\n  Name: {user_data.get('first_name')} {user_data.get('last_name')}"
            )
            print(f"  Email: {user_data.get('email')}")
            print(f"  User ID: {user_data.get('id')}")

            user_id = int(user_data.get("id"))

            # Get teams
            print_section("🏆 Teams")
            teams = client.search_teams(user_id=user_id)
            print(f"\n  Total teams: {len(teams)}")

            for idx, team_item in enumerate(teams, 1):
                team_data = extract_data(team_item)
                team_id = int(team_data.get("id"))
                team_name = team_data.get("name")

                print(f"\n  Team #{idx}: {team_name} (ID: {team_id})")
                print(f"    Sport: {team_data.get('sport_name', 'N/A')}")
                print(f"    Season: {team_data.get('season_name', 'N/A')}")

                # Get members for this team
                print_section(f"👥 Members - {team_name}")
                members = client.search_members(team_id=team_id)
                print(f"\n  Total members: {len(members)}")

                for member_item in members[:10]:  # Show first 10
                    member_data = extract_data(member_item)
                    print(
                        f"    • {member_data.get('first_name')} {member_data.get('last_name')}"
                    )
                    if member_data.get("position"):
                        print(f"      Position: {member_data.get('position')}")

                # Get events
                print_section(f"📅 Events - {team_name}")
                events = client.search_events(team_id=team_id)
                print(f"\n  Total events: {len(events)}")

                for event_item in events[:10]:  # Show first 10
                    event_data = extract_data(event_item)
                    print(f"\n    • {event_data.get('name')}")
                    print(f"      Type: {event_data.get('type', 'N/A')}")
                    print(f"      Date: {event_data.get('start_date', 'N/A')}")
                    print(f"      Location: {event_data.get('location_name', 'N/A')}")
                    if event_data.get("notes"):
                        notes = event_data.get("notes")
                        print(
                            f"      Notes: {notes[:50]}{'...' if len(notes) > 50 else ''}"
                        )

                # Get forum topics
                print_section(f"💬 Forum Topics / Message Board - {team_name}")
                forum_topics = client.search_forum_topics(team_id=team_id)
                print(f"\n  Total topics: {len(forum_topics)}")

                for topic_item in forum_topics:
                    topic_data = extract_data(topic_item)
                    topic_id = int(topic_data.get("id"))
                    is_announcement = topic_data.get("is_announcement")
                    announcement_badge = " 📢 ANNOUNCEMENT" if is_announcement else ""

                    print(f"\n    📌 {topic_data.get('title')}{announcement_badge}")
                    print(f"       Topic ID: {topic_id}")
                    print(f"       Created: {topic_data.get('created_at', 'N/A')}")

                    # Get posts for this topic
                    forum_posts = client.search_forum_posts(
                        team_id=team_id, forum_topic_id=topic_id
                    )
                    print(f"       Replies: {len(forum_posts)}")

                    for post_item in forum_posts[:5]:  # Show first 5 posts
                        post_data = extract_data(post_item)
                        message = post_data.get("message", "")
                        poster = post_data.get("poster_name", "Unknown")
                        print(f"\n         💬 {poster}:")
                        print(
                            f"            {message[:100]}{'...' if len(message) > 100 else ''}"
                        )

                # Get broadcast emails
                print_section(f"📧 Broadcast Emails - {team_name}")
                emails = client.search_broadcast_emails(team_id=team_id)
                print(f"\n  Total emails: {len(emails)}")

                for email_item in emails[:10]:
                    email_data = extract_data(email_item)
                    print(f"\n    📨 {email_data.get('subject', 'No Subject')}")
                    print(f"       From: {email_data.get('sender_email', 'N/A')}")
                    print(f"       Sent: {email_data.get('sent_at', 'Not sent yet')}")
                    if email_data.get("body"):
                        body = email_data.get("body", "")
                        print(
                            f"       Body: {body[:100]}{'...' if len(body) > 100 else ''}"
                        )

                # Get messages
                print_section(f"💌 Messages - {team_name}")
                messages = client.search_messages(team_id=team_id)
                print(f"\n  Total messages: {len(messages)}")

                for msg_item in messages[:10]:
                    msg_data = extract_data(msg_item)
                    print(f"\n    • {msg_data.get('title', 'No Title')}")
                    print(f"      From: {msg_data.get('sender_name', 'N/A')}")
                    print(f"      Sent: {msg_data.get('created_at', 'N/A')}")

                # Get assignments
                print_section(f"✅ Assignments - {team_name}")
                assignments = client.search_assignments(team_id=team_id)
                print(f"\n  Total assignments: {len(assignments)}")

                for assignment_item in assignments[:10]:
                    assignment_data = extract_data(assignment_item)
                    print(
                        f"\n    ✓ {assignment_data.get('description', 'No description')}"
                    )
                    print(f"      Position: {assignment_data.get('position', 'N/A')}")
                    print(f"      Event ID: {assignment_data.get('event_id', 'N/A')}")
                    print(f"      Member ID: {assignment_data.get('member_id', 'N/A')}")

        print_section("✅ Complete!")
        print("\n  All available data has been displayed above.")
        print("  To access more endpoints, check out explore_api.py\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
