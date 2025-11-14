"""
TeamSnap MCP Server

Model Context Protocol server for TeamSnap API integration.
Provides read and write tools for managing teams, events, members, and more.
"""

import os
from datetime import datetime
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from dotenv import load_dotenv

from client import TeamSnapAsyncClient

# Load environment variables
load_dotenv()

# Create MCP server
mcp = FastMCP("TeamSnap")

# Global client instance (will be initialized per request)
def get_client() -> TeamSnapAsyncClient:
    """Get TeamSnap client instance"""
    return TeamSnapAsyncClient()


def is_readonly() -> bool:
    """
    Check if server is in read-only mode

    Returns:
        True if readonly mode is enabled (default), False if writes are allowed
    """
    readonly_env = os.getenv('TEAMSNAP_READONLY', 'true').lower()
    return readonly_env in ('true', '1', 'yes', 'on')


def check_readonly() -> Optional[list[TextContent]]:
    """
    Check if readonly mode is enabled and return error message if so

    Returns:
        Error message if readonly, None if writes are allowed
    """
    if is_readonly():
        return [TextContent(
            type="text",
            text="❌ Write operation blocked: Server is in READ-ONLY mode\n\n"
                 "To enable write operations:\n"
                 "1. Edit your .env file (or Claude Desktop config)\n"
                 "2. Set: TEAMSNAP_READONLY=false\n"
                 "3. Restart Claude Desktop\n\n"
                 "⚠️  SECURITY: Only enable writes if you trust this integration and "
                 "understand the risks of modifying your TeamSnap data."
        )]
    return None


# ============================================================================
# READ TOOLS
# ============================================================================

@mcp.tool()
async def list_teams(user_id: Optional[int] = None) -> list[TextContent]:
    """
    List all teams accessible to the authenticated user.

    Args:
        user_id: Optional user ID to filter teams

    Returns:
        List of teams with their details
    """
    async with get_client() as client:
        teams = await client.search_teams(user_id=user_id)

        if not teams:
            return [TextContent(type="text", text="No teams found.")]

        result = f"Found {len(teams)} team(s):\n\n"

        for team_item in teams:
            team_data = client.extract_item_data(team_item)
            result += f"**{team_data.get('name', 'Unnamed Team')}** (ID: {team_data.get('id')})\n"
            result += f"  - Sport: {team_data.get('sport_name', 'N/A')}\n"
            result += f"  - Season: {team_data.get('season_name', 'N/A')}\n"
            result += f"  - Division: {team_data.get('division_name', 'N/A')}\n"
            result += f"  - Location: {team_data.get('location_country', 'N/A')}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]


@mcp.tool()
async def get_team_details(team_id: int) -> list[TextContent]:
    """
    Get detailed information about a specific team.

    Args:
        team_id: The team ID

    Returns:
        Detailed team information
    """
    async with get_client() as client:
        response = await client.get_team(team_id)

        # Extract team data from Collection+JSON format
        items = response.get('collection', {}).get('items', [])
        if not items:
            return [TextContent(type="text", text=f"Team {team_id} not found.")]

        team_data = client.extract_item_data(items[0])

        result = f"**Team: {team_data.get('name', 'Unnamed')}**\n\n"
        result += f"ID: {team_data.get('id')}\n"
        result += f"Sport: {team_data.get('sport_name', 'N/A')}\n"
        result += f"Season: {team_data.get('season_name', 'N/A')}\n"
        result += f"Division: {team_data.get('division_name', 'N/A')}\n"
        result += f"Location: {team_data.get('location_country', 'N/A')}\n"
        result += f"Time Zone: {team_data.get('time_zone', 'N/A')}\n"

        return [TextContent(type="text", text=result)]


@mcp.tool()
async def list_events(team_id: int) -> list[TextContent]:
    """
    List all events for a team.

    Args:
        team_id: The team ID

    Returns:
        List of events with their details
    """
    async with get_client() as client:
        events = await client.search_events(team_id=team_id)

        if not events:
            return [TextContent(type="text", text=f"No events found for team {team_id}.")]

        result = f"Found {len(events)} event(s) for team {team_id}:\n\n"

        for event_item in events:
            event_data = client.extract_item_data(event_item)
            event_type = "Game" if event_data.get('is_game') else "Practice/Event"

            result += f"**{event_data.get('name', 'Unnamed Event')}** (ID: {event_data.get('id')})\n"
            result += f"  - Type: {event_type}\n"
            result += f"  - Start: {event_data.get('start_date', 'N/A')}\n"
            result += f"  - Location: {event_data.get('location_name', 'TBD')}\n"

            if event_data.get('opponent_name'):
                result += f"  - Opponent: {event_data.get('opponent_name')}\n"

            notes = event_data.get('notes')
            if notes:
                notes_preview = notes[:60] + '...' if len(notes) > 60 else notes
                result += f"  - Notes: {notes_preview}\n"

            result += "\n"

        return [TextContent(type="text", text=result)]


@mcp.tool()
async def get_event_details(event_id: int) -> list[TextContent]:
    """
    Get detailed information about a specific event.

    Args:
        event_id: The event ID

    Returns:
        Detailed event information
    """
    async with get_client() as client:
        response = await client.get_event(event_id)

        items = response.get('collection', {}).get('items', [])
        if not items:
            return [TextContent(type="text", text=f"Event {event_id} not found.")]

        event_data = client.extract_item_data(items[0])
        event_type = "Game" if event_data.get('is_game') else "Practice/Event"

        result = f"**Event: {event_data.get('name', 'Unnamed')}**\n\n"
        result += f"ID: {event_data.get('id')}\n"
        result += f"Type: {event_type}\n"
        result += f"Start: {event_data.get('start_date', 'N/A')}\n"
        result += f"End: {event_data.get('end_date', 'N/A')}\n"
        result += f"Location: {event_data.get('location_name', 'TBD')}\n"

        if event_data.get('opponent_name'):
            result += f"Opponent: {event_data.get('opponent_name')}\n"

        if event_data.get('notes'):
            result += f"\nNotes:\n{event_data.get('notes')}\n"

        return [TextContent(type="text", text=result)]


@mcp.tool()
async def list_members(team_id: int) -> list[TextContent]:
    """
    List all members of a team.

    Args:
        team_id: The team ID

    Returns:
        List of team members with their details
    """
    async with get_client() as client:
        members = await client.search_members(team_id=team_id)

        if not members:
            return [TextContent(type="text", text=f"No members found for team {team_id}.")]

        result = f"Found {len(members)} member(s) in team {team_id}:\n\n"

        for member_item in members:
            member_data = client.extract_item_data(member_item)

            name = f"{member_data.get('first_name', '')} {member_data.get('last_name', '')}".strip()
            if not name:
                name = "Unnamed Member"

            result += f"**{name}** (ID: {member_data.get('id')})\n"

            if member_data.get('email'):
                result += f"  - Email: {member_data.get('email')}\n"
            if member_data.get('phone'):
                result += f"  - Phone: {member_data.get('phone')}\n"

            result += f"  - Is Manager: {member_data.get('is_manager', False)}\n"
            result += f"  - Is Non Player: {member_data.get('is_non_player', False)}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]


@mcp.tool()
async def get_event_availability(event_id: int) -> list[TextContent]:
    """
    Get member availability responses for a specific event.

    Args:
        event_id: The event ID

    Returns:
        List of member availability responses
    """
    async with get_client() as client:
        availabilities = await client.search_availabilities(event_id=event_id)

        if not availabilities:
            return [TextContent(type="text", text=f"No availability responses for event {event_id}.")]

        result = f"Availability for event {event_id}:\n\n"

        # Group by status
        by_status = {'yes': [], 'no': [], 'maybe': [], 'unknown': []}

        for avail_item in availabilities:
            avail_data = client.extract_item_data(avail_item)
            status = avail_data.get('status_code', 'unknown').lower()
            member_name = avail_data.get('member_name', 'Unknown Member')

            if status in by_status:
                by_status[status].append(member_name)
            else:
                by_status['unknown'].append(member_name)

        # Display results
        result += f"✅ Available ({len(by_status['yes'])}):\n"
        for name in by_status['yes']:
            result += f"  - {name}\n"
        result += "\n"

        result += f"❌ Not Available ({len(by_status['no'])}):\n"
        for name in by_status['no']:
            result += f"  - {name}\n"
        result += "\n"

        result += f"❓ Maybe ({len(by_status['maybe'])}):\n"
        for name in by_status['maybe']:
            result += f"  - {name}\n"
        result += "\n"

        result += f"⚪ No Response ({len(by_status['unknown'])}):\n"
        for name in by_status['unknown']:
            result += f"  - {name}\n"

        return [TextContent(type="text", text=result)]


@mcp.tool()
async def list_assignments(event_id: int) -> list[TextContent]:
    """
    List assignments (tasks) for an event.

    Args:
        event_id: The event ID

    Returns:
        List of assignments for the event
    """
    async with get_client() as client:
        assignments = await client.search_assignments(event_id=event_id)

        if not assignments:
            return [TextContent(type="text", text=f"No assignments found for event {event_id}.")]

        result = f"Found {len(assignments)} assignment(s) for event {event_id}:\n\n"

        for assignment_item in assignments:
            assignment_data = client.extract_item_data(assignment_item)

            result += f"**{assignment_data.get('description', 'Unnamed Assignment')}** (ID: {assignment_data.get('id')})\n"
            result += f"  - Assigned to: {assignment_data.get('member_name', 'N/A')}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]


@mcp.tool()
async def list_locations(team_id: int) -> list[TextContent]:
    """
    List all locations for a team.

    Args:
        team_id: The team ID

    Returns:
        List of locations
    """
    async with get_client() as client:
        locations = await client.search_locations(team_id=team_id)

        if not locations:
            return [TextContent(type="text", text=f"No locations found for team {team_id}.")]

        result = f"Found {len(locations)} location(s) for team {team_id}:\n\n"

        for location_item in locations:
            location_data = client.extract_item_data(location_item)

            result += f"**{location_data.get('name', 'Unnamed Location')}** (ID: {location_data.get('id')})\n"

            if location_data.get('address'):
                result += f"  - Address: {location_data.get('address')}\n"
            if location_data.get('url'):
                result += f"  - URL: {location_data.get('url')}\n"

            result += "\n"

        return [TextContent(type="text", text=result)]


# ============================================================================
# WRITE TOOLS
# ============================================================================

@mcp.tool()
async def create_event(
    team_id: int,
    name: str,
    start_date: str,
    is_game: bool = False,
    location_id: Optional[int] = None,
    opponent_id: Optional[int] = None,
    notes: Optional[str] = None
) -> list[TextContent]:
    """
    Create a new event for a team.

    Args:
        team_id: The team ID
        name: Event name
        start_date: Start date/time in ISO format (e.g., "2025-01-15T14:00:00Z")
        is_game: Whether this is a game (true) or practice/other (false)
        location_id: Optional location ID
        opponent_id: Optional opponent ID (for games)
        notes: Optional notes/description

    Returns:
        Created event details
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            response = await client.create_event(
                team_id=team_id,
                name=name,
                start_date=start_date,
                is_game=is_game,
                location_id=location_id,
                opponent_id=opponent_id,
                notes=notes
            )

            items = response.get('collection', {}).get('items', [])
            if items:
                event_data = client.extract_item_data(items[0])
                event_id = event_data.get('id')
                event_type = "game" if is_game else "event"

                result = f"✅ Successfully created {event_type}: {name}\n\n"
                result += f"Event ID: {event_id}\n"
                result += f"Start: {start_date}\n"
                if location_id:
                    result += f"Location ID: {location_id}\n"
                if notes:
                    result += f"Notes: {notes}\n"

                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text="Event created but unable to retrieve details.")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error creating event: {str(e)}")]


@mcp.tool()
async def update_event(
    event_id: int,
    name: Optional[str] = None,
    start_date: Optional[str] = None,
    location_id: Optional[int] = None,
    notes: Optional[str] = None
) -> list[TextContent]:
    """
    Update an existing event.

    Args:
        event_id: The event ID to update
        name: Optional new event name
        start_date: Optional new start date/time in ISO format
        location_id: Optional new location ID
        notes: Optional new notes

    Returns:
        Updated event details
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            # Build update fields
            fields = {}
            if name is not None:
                fields['name'] = name
            if start_date is not None:
                fields['start_date'] = start_date
            if location_id is not None:
                fields['location_id'] = location_id
            if notes is not None:
                fields['notes'] = notes

            if not fields:
                return [TextContent(type="text", text="No fields provided to update.")]

            response = await client.update_event(event_id, **fields)

            result = f"✅ Successfully updated event {event_id}\n\n"
            result += "Updated fields:\n"
            for key, value in fields.items():
                result += f"  - {key}: {value}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error updating event: {str(e)}")]


@mcp.tool()
async def delete_event(event_id: int) -> list[TextContent]:
    """
    Delete an event.

    Args:
        event_id: The event ID to delete

    Returns:
        Confirmation message
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            await client.delete_event(event_id)
            return [TextContent(type="text", text=f"✅ Successfully deleted event {event_id}")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error deleting event: {str(e)}")]


@mcp.tool()
async def create_member(
    team_id: int,
    first_name: str,
    last_name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> list[TextContent]:
    """
    Add a new member to a team.

    Args:
        team_id: The team ID
        first_name: Member's first name
        last_name: Member's last name
        email: Optional email address
        phone: Optional phone number

    Returns:
        Created member details
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            response = await client.create_member(
                team_id=team_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )

            items = response.get('collection', {}).get('items', [])
            if items:
                member_data = client.extract_item_data(items[0])
                member_id = member_data.get('id')

                result = f"✅ Successfully added member: {first_name} {last_name}\n\n"
                result += f"Member ID: {member_id}\n"
                if email:
                    result += f"Email: {email}\n"
                if phone:
                    result += f"Phone: {phone}\n"

                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text="Member created but unable to retrieve details.")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error creating member: {str(e)}")]


@mcp.tool()
async def update_member(
    member_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> list[TextContent]:
    """
    Update an existing team member.

    Args:
        member_id: The member ID to update
        first_name: Optional new first name
        last_name: Optional new last name
        email: Optional new email
        phone: Optional new phone number

    Returns:
        Updated member details
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            fields = {}
            if first_name is not None:
                fields['first_name'] = first_name
            if last_name is not None:
                fields['last_name'] = last_name
            if email is not None:
                fields['email'] = email
            if phone is not None:
                fields['phone'] = phone

            if not fields:
                return [TextContent(type="text", text="No fields provided to update.")]

            response = await client.update_member(member_id, **fields)

            result = f"✅ Successfully updated member {member_id}\n\n"
            result += "Updated fields:\n"
            for key, value in fields.items():
                result += f"  - {key}: {value}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error updating member: {str(e)}")]


@mcp.tool()
async def delete_member(member_id: int) -> list[TextContent]:
    """
    Remove a member from a team.

    Args:
        member_id: The member ID to delete

    Returns:
        Confirmation message
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            await client.delete_member(member_id)
            return [TextContent(type="text", text=f"✅ Successfully removed member {member_id}")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error deleting member: {str(e)}")]


@mcp.tool()
async def update_availability(
    availability_id: int,
    status: str
) -> list[TextContent]:
    """
    Update a member's availability for an event.

    Args:
        availability_id: The availability ID to update
        status: New status ("yes", "no", "maybe", or "unknown")

    Returns:
        Updated availability details
    """
    async with get_client() as client:
        try:
            # Validate status
            valid_statuses = ["yes", "no", "maybe", "unknown"]
            if status.lower() not in valid_statuses:
                return [TextContent(type="text", text=f"❌ Invalid status. Must be one of: {', '.join(valid_statuses)}")]

            response = await client.update_availability(availability_id, status.lower())

            result = f"✅ Successfully updated availability {availability_id}\n"
            result += f"New status: {status}\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error updating availability: {str(e)}")]


@mcp.tool()
async def create_assignment(
    event_id: int,
    member_id: int,
    description: str
) -> list[TextContent]:
    """
    Create a new assignment (task) for an event.

    Args:
        event_id: The event ID
        member_id: The member ID to assign to
        description: Description of the assignment

    Returns:
        Created assignment details
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            response = await client.create_assignment(
                event_id=event_id,
                member_id=member_id,
                description=description
            )

            items = response.get('collection', {}).get('items', [])
            if items:
                assignment_data = client.extract_item_data(items[0])
                assignment_id = assignment_data.get('id')

                result = f"✅ Successfully created assignment\n\n"
                result += f"Assignment ID: {assignment_id}\n"
                result += f"Description: {description}\n"
                result += f"Assigned to Member ID: {member_id}\n"
                result += f"For Event ID: {event_id}\n"

                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text="Assignment created but unable to retrieve details.")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error creating assignment: {str(e)}")]


@mcp.tool()
async def delete_assignment(assignment_id: int) -> list[TextContent]:
    """
    Delete an assignment.

    Args:
        assignment_id: The assignment ID to delete

    Returns:
        Confirmation message
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            await client.delete_assignment(assignment_id)
            return [TextContent(type="text", text=f"✅ Successfully deleted assignment {assignment_id}")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error deleting assignment: {str(e)}")]


@mcp.tool()
async def create_location(
    team_id: int,
    name: str,
    address: Optional[str] = None
) -> list[TextContent]:
    """
    Create a new location for a team.

    Args:
        team_id: The team ID
        name: Location name
        address: Optional address

    Returns:
        Created location details
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            response = await client.create_location(
                team_id=team_id,
                name=name,
                address=address
            )

            items = response.get('collection', {}).get('items', [])
            if items:
                location_data = client.extract_item_data(items[0])
                location_id = location_data.get('id')

                result = f"✅ Successfully created location: {name}\n\n"
                result += f"Location ID: {location_id}\n"
                if address:
                    result += f"Address: {address}\n"

                return [TextContent(type="text", text=result)]
            else:
                return [TextContent(type="text", text="Location created but unable to retrieve details.")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error creating location: {str(e)}")]


@mcp.tool()
async def delete_location(location_id: int) -> list[TextContent]:
    """
    Delete a location.

    Args:
        location_id: The location ID to delete

    Returns:
        Confirmation message
    """
    # Check if server is in read-only mode
    readonly_error = check_readonly()
    if readonly_error:
        return readonly_error

    async with get_client() as client:
        try:
            await client.delete_location(location_id)
            return [TextContent(type="text", text=f"✅ Successfully deleted location {location_id}")]

        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error deleting location: {str(e)}")]


# ============================================================================
# SERVER MAIN
# ============================================================================

if __name__ == "__main__":
    mcp.run()
