"""
Async TeamSnap API Client for MCP Server

An async Python client for the TeamSnap API v3 using httpx.
Includes both read and write operations.
"""

import httpx
import logging
import os
from typing import Optional, Dict, List, Any

# Set up logging
logger = logging.getLogger(__name__)


class TeamSnapAsyncClient:
    """Async client for TeamSnap API v3"""

    BASE_URL = "https://api.teamsnap.com/v3"

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize TeamSnap async API client

        Args:
            access_token: TeamSnap OAuth access token (if None, reads from TEAMSNAP_ACCESS_TOKEN env var)
        """
        self.access_token = access_token or os.getenv("TEAMSNAP_ACCESS_TOKEN")

        if not self.access_token:
            raise ValueError(
                "No access token provided. Set TEAMSNAP_ACCESS_TOKEN environment variable "
                "or pass access_token parameter."
            )

        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        self.api_version = None

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        Make an async API request

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to httpx

        Returns:
            Response object
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"API Error: {e}")
            logger.error(f"Response: {e.response.text}")
            raise

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an async GET request

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        response = await self._request("GET", endpoint, params=params)
        return response.json()

    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an async POST request

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            JSON response as dictionary
        """
        response = await self._request("POST", endpoint, json=data)
        return response.json()

    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an async PUT request

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            JSON response as dictionary
        """
        response = await self._request("PUT", endpoint, json=data)
        return response.json()

    async def patch(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an async PATCH request

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            JSON response as dictionary
        """
        response = await self._request("PATCH", endpoint, json=data)
        return response.json()

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make an async DELETE request

        Args:
            endpoint: API endpoint

        Returns:
            JSON response as dictionary (empty if no content)
        """
        response = await self._request("DELETE", endpoint)
        return response.json() if response.text else {}

    # Helper method to extract data from Collection+JSON format
    def extract_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from a Collection+JSON item

        Args:
            item: Collection+JSON item with 'data' array

        Returns:
            Dictionary of field names to values
        """
        data_array = item.get("data", [])
        result = {}
        for field in data_array:
            name = field.get("name")
            value = field.get("value")
            if name:
                result[name] = value
        return result

    # READ OPERATIONS

    async def get_me(self) -> Dict[str, Any]:
        """Get information about the authenticated user"""
        return await self.get("/me")

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get information about a specific user"""
        return await self.get(f"/users/{user_id}")

    async def search_teams(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search for teams"""
        params = {}
        if user_id:
            params["user_id"] = user_id

        response = await self.get("/teams/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def get_team(self, team_id: int) -> Dict[str, Any]:
        """Get information about a specific team"""
        return await self.get(f"/teams/{team_id}")

    async def search_members(
        self, team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for team members"""
        params = {}
        if team_id:
            params["team_id"] = team_id

        response = await self.get("/members/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def get_member(self, member_id: int) -> Dict[str, Any]:
        """Get information about a specific member"""
        return await self.get(f"/members/{member_id}")

    async def search_events(
        self, team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for events"""
        params = {}
        if team_id:
            params["team_id"] = team_id

        response = await self.get("/events/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def get_event(self, event_id: int) -> Dict[str, Any]:
        """Get information about a specific event"""
        return await self.get(f"/events/{event_id}")

    async def search_availabilities(
        self, event_id: Optional[int] = None, member_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for member availabilities for events"""
        params = {}
        if event_id:
            params["event_id"] = event_id
        if member_id:
            params["member_id"] = member_id

        response = await self.get("/availabilities/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def search_assignments(
        self, team_id: Optional[int] = None, event_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for assignments (tasks assigned to members)"""
        params = {}
        if team_id:
            params["team_id"] = team_id
        if event_id:
            params["event_id"] = event_id

        response = await self.get("/assignments/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def search_locations(
        self, team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for locations"""
        params = {}
        if team_id:
            params["team_id"] = team_id

        response = await self.get("/locations/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def search_opponents(
        self, team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for opponents"""
        params = {}
        if team_id:
            params["team_id"] = team_id

        response = await self.get("/opponents/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def search_forum_topics(
        self, team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for forum topics (message board)"""
        params = {}
        if team_id:
            params["team_id"] = team_id

        response = await self.get("/forum_topics/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def search_forum_posts(
        self, team_id: Optional[int] = None, forum_topic_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for forum posts"""
        params = {}
        if team_id:
            params["team_id"] = team_id
        if forum_topic_id:
            params["forum_topic_id"] = forum_topic_id

        response = await self.get("/forum_posts/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def search_broadcast_emails(
        self, team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for broadcast emails"""
        params = {}
        if team_id:
            params["team_id"] = team_id

        response = await self.get("/broadcast_emails/search", params=params)
        return response.get("collection", {}).get("items", [])

    async def search_messages(
        self, team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for messages"""
        params = {}
        if team_id:
            params["team_id"] = team_id

        response = await self.get("/messages/search", params=params)
        return response.get("collection", {}).get("items", [])

    # WRITE OPERATIONS

    async def create_event(
        self,
        team_id: int,
        name: str,
        start_date: str,
        location_id: Optional[int] = None,
        opponent_id: Optional[int] = None,
        notes: Optional[str] = None,
        is_game: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new event

        Args:
            team_id: Team ID
            name: Event name
            start_date: ISO format datetime string (e.g., "2025-01-15T14:00:00Z")
            location_id: Optional location ID
            opponent_id: Optional opponent ID (for games)
            notes: Optional notes
            is_game: Whether this is a game (vs practice/other)
            **kwargs: Additional event fields

        Returns:
            Created event data
        """
        data = {
            "team_id": team_id,
            "name": name,
            "start_date": start_date,
            "is_game": is_game,
            **kwargs,
        }

        if location_id:
            data["location_id"] = location_id
        if opponent_id:
            data["opponent_id"] = opponent_id
        if notes:
            data["notes"] = notes

        return await self.post("/events", data=data)

    async def update_event(self, event_id: int, **fields) -> Dict[str, Any]:
        """
        Update an event

        Args:
            event_id: Event ID
            **fields: Fields to update (name, start_date, location_id, etc.)

        Returns:
            Updated event data
        """
        return await self.patch(f"/events/{event_id}", data=fields)

    async def delete_event(self, event_id: int) -> Dict[str, Any]:
        """Delete an event"""
        return await self.delete(f"/events/{event_id}")

    async def create_member(
        self,
        team_id: int,
        first_name: str,
        last_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a new team member

        Args:
            team_id: Team ID
            first_name: First name
            last_name: Last name
            email: Optional email address
            phone: Optional phone number
            **kwargs: Additional member fields

        Returns:
            Created member data
        """
        data = {
            "team_id": team_id,
            "first_name": first_name,
            "last_name": last_name,
            **kwargs,
        }

        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone

        return await self.post("/members", data=data)

    async def update_member(self, member_id: int, **fields) -> Dict[str, Any]:
        """
        Update a team member

        Args:
            member_id: Member ID
            **fields: Fields to update (first_name, last_name, email, etc.)

        Returns:
            Updated member data
        """
        return await self.patch(f"/members/{member_id}", data=fields)

    async def delete_member(self, member_id: int) -> Dict[str, Any]:
        """Delete a team member"""
        return await self.delete(f"/members/{member_id}")

    async def update_availability(
        self, availability_id: int, status: str
    ) -> Dict[str, Any]:
        """
        Update a member's availability for an event

        Args:
            availability_id: Availability ID
            status: Availability status (e.g., "yes", "no", "maybe", "unknown")

        Returns:
            Updated availability data
        """
        return await self.patch(
            f"/availabilities/{availability_id}", data={"status": status}
        )

    async def create_assignment(
        self, event_id: int, member_id: int, description: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new assignment (task for an event)

        Args:
            event_id: Event ID
            member_id: Member ID to assign to
            description: Assignment description
            **kwargs: Additional assignment fields

        Returns:
            Created assignment data
        """
        data = {
            "event_id": event_id,
            "member_id": member_id,
            "description": description,
            **kwargs,
        }

        return await self.post("/assignments", data=data)

    async def update_assignment(self, assignment_id: int, **fields) -> Dict[str, Any]:
        """
        Update an assignment

        Args:
            assignment_id: Assignment ID
            **fields: Fields to update

        Returns:
            Updated assignment data
        """
        return await self.patch(f"/assignments/{assignment_id}", data=fields)

    async def delete_assignment(self, assignment_id: int) -> Dict[str, Any]:
        """Delete an assignment"""
        return await self.delete(f"/assignments/{assignment_id}")

    async def create_location(
        self, team_id: int, name: str, address: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new location

        Args:
            team_id: Team ID
            name: Location name
            address: Optional address
            **kwargs: Additional location fields

        Returns:
            Created location data
        """
        data = {"team_id": team_id, "name": name, **kwargs}

        if address:
            data["address"] = address

        return await self.post("/locations", data=data)

    async def update_location(self, location_id: int, **fields) -> Dict[str, Any]:
        """
        Update a location

        Args:
            location_id: Location ID
            **fields: Fields to update

        Returns:
            Updated location data
        """
        return await self.patch(f"/locations/{location_id}", data=fields)

    async def delete_location(self, location_id: int) -> Dict[str, Any]:
        """Delete a location"""
        return await self.delete(f"/locations/{location_id}")

    async def get_root(self) -> Dict[str, Any]:
        """Get API root information"""
        return await self.get("/")

    async def get_api_version(self) -> Optional[str]:
        """
        Get the current API version

        Returns:
            API version string (e.g., "3.867.0") or None
        """
        if not self.api_version:
            root = await self.get_root()
            self.api_version = root.get("collection", {}).get("version")

        return self.api_version
