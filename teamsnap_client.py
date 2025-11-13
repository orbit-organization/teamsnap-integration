"""
TeamSnap API Client

A Python client for interacting with the TeamSnap API v3.
Handles authentication and provides methods for common API operations.
"""

import requests
import logging
from typing import Optional, Dict, List, Any
from teamsnap_auth import TeamSnapAuth

# Set up logging
logger = logging.getLogger(__name__)


class TeamSnapClient:
    """Client for TeamSnap API v3"""

    BASE_URL = "https://api.teamsnap.com/v3"

    def __init__(self, config_file='config.ini', auto_authenticate=True, monitor_deprecations=True):
        """
        Initialize TeamSnap API client

        Args:
            config_file: Path to configuration file
            auto_authenticate: Automatically authenticate if no valid token exists
            monitor_deprecations: Log deprecation warnings from API responses
        """
        self.auth = TeamSnapAuth(config_file)
        self.session = requests.Session()
        self.api_version = None
        self.monitor_deprecations = monitor_deprecations

        # Check if we need to authenticate
        if not self.auth.is_token_valid():
            if auto_authenticate:
                print("⚠️  No valid access token found. Starting authentication...")
                self.auth.authenticate()
            else:
                raise Exception("No valid access token. Please authenticate first.")

        # Set up session headers
        access_token = self.auth.get_access_token()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

        # Check and log API version
        self._check_api_version()

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an API request

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"❌ API Error: {e}")
            print(f"   Response: {response.text}")
            raise

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a GET request

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        response = self._request('GET', endpoint, params=params)
        json_response = response.json()

        # Check for deprecations if monitoring is enabled
        if self.monitor_deprecations:
            self._check_deprecations(json_response)

        return json_response

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a POST request

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            JSON response as dictionary
        """
        response = self._request('POST', endpoint, json=data)
        return response.json()

    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a PUT request

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            JSON response as dictionary
        """
        response = self._request('PUT', endpoint, json=data)
        return response.json()

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a DELETE request

        Args:
            endpoint: API endpoint

        Returns:
            JSON response as dictionary
        """
        response = self._request('DELETE', endpoint)
        return response.json() if response.text else {}

    # API Monitoring Methods

    def _check_api_version(self):
        """
        Check current API version and log if changed

        This method is called automatically on client initialization.
        """
        try:
            root = self.get_root()
            current_version = root.get('collection', {}).get('version')

            if current_version:
                if self.api_version and current_version != self.api_version:
                    logger.warning(f"🔄 API version changed: {self.api_version} -> {current_version}")
                    print(f"⚠️  TeamSnap API version changed: {self.api_version} -> {current_version}")

                self.api_version = current_version
                logger.info(f"TeamSnap API version: {self.api_version}")
            else:
                logger.warning("Could not determine API version from root endpoint")
        except Exception as e:
            logger.error(f"Failed to check API version: {e}")

    def _check_deprecations(self, response: Dict[str, Any]):
        """
        Monitor API responses for deprecation warnings

        Args:
            response: JSON response from API

        This method automatically checks for deprecated endpoints and logs warnings.
        """
        if not isinstance(response, dict) or 'collection' not in response:
            return

        links = response.get('collection', {}).get('links', [])
        for link in links:
            if link.get('deprecated'):
                rel = link.get('rel', 'unknown')
                prompt = link.get('prompt', 'No description provided')
                logger.warning(f"⚠️  DEPRECATED: {rel} - {prompt}")

    def get_api_version(self) -> Optional[str]:
        """
        Get the current API version

        Returns:
            API version string (e.g., "3.867.0") or None if unavailable
        """
        return self.api_version

    def check_for_deprecations(self, endpoint: str = '/') -> List[Dict[str, Any]]:
        """
        Manually check a specific endpoint for deprecation warnings

        Args:
            endpoint: API endpoint to check (default: root)

        Returns:
            List of deprecated items with their details
        """
        try:
            response = self.get(endpoint)
            deprecated_items = []

            if isinstance(response, dict) and 'collection' in response:
                links = response.get('collection', {}).get('links', [])
                for link in links:
                    if link.get('deprecated'):
                        deprecated_items.append({
                            'rel': link.get('rel'),
                            'prompt': link.get('prompt'),
                            'href': link.get('href')
                        })

            return deprecated_items
        except Exception as e:
            logger.error(f"Error checking for deprecations: {e}")
            return []

    # Convenience methods for common operations

    def get_me(self) -> Dict[str, Any]:
        """
        Get information about the authenticated user

        Returns:
            User data dictionary
        """
        return self.get('/me')

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get information about a specific user

        Args:
            user_id: User ID

        Returns:
            User data dictionary
        """
        return self.get(f'/users/{user_id}')

    def search_teams(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for teams

        Args:
            user_id: Filter teams by user ID

        Returns:
            List of team dictionaries
        """
        params = {}
        if user_id:
            params['user_id'] = user_id

        response = self.get('/teams/search', params=params)
        return response.get('collection', {}).get('items', [])

    def get_team(self, team_id: int) -> Dict[str, Any]:
        """
        Get information about a specific team

        Args:
            team_id: Team ID

        Returns:
            Team data dictionary
        """
        return self.get(f'/teams/{team_id}')

    def search_members(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for team members

        Args:
            team_id: Filter members by team ID

        Returns:
            List of member dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id

        response = self.get('/members/search', params=params)
        return response.get('collection', {}).get('items', [])

    def search_events(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for events

        Args:
            team_id: Filter events by team ID

        Returns:
            List of event dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id

        response = self.get('/events/search', params=params)
        return response.get('collection', {}).get('items', [])

    def get_event(self, event_id: int) -> Dict[str, Any]:
        """
        Get information about a specific event

        Args:
            event_id: Event ID

        Returns:
            Event data dictionary
        """
        return self.get(f'/events/{event_id}')

    def search_opponents(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for opponents

        Args:
            team_id: Filter opponents by team ID

        Returns:
            List of opponent dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id

        response = self.get('/opponents/search', params=params)
        return response.get('collection', {}).get('items', [])

    def search_locations(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for locations

        Args:
            team_id: Filter locations by team ID

        Returns:
            List of location dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id

        response = self.get('/locations/search', params=params)
        return response.get('collection', {}).get('items', [])

    def search_forum_topics(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for forum topics (message board topics)

        Args:
            team_id: Filter topics by team ID

        Returns:
            List of forum topic dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id

        response = self.get('/forum_topics/search', params=params)
        return response.get('collection', {}).get('items', [])

    def search_forum_posts(self, team_id: Optional[int] = None, forum_topic_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for forum posts (message board posts/replies)

        Args:
            team_id: Filter posts by team ID
            forum_topic_id: Filter posts by topic ID

        Returns:
            List of forum post dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id
        if forum_topic_id:
            params['forum_topic_id'] = forum_topic_id

        response = self.get('/forum_posts/search', params=params)
        return response.get('collection', {}).get('items', [])

    def search_broadcast_emails(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for broadcast emails sent to the team

        Args:
            team_id: Filter emails by team ID

        Returns:
            List of broadcast email dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id

        response = self.get('/broadcast_emails/search', params=params)
        return response.get('collection', {}).get('items', [])

    def search_messages(self, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for messages

        Args:
            team_id: Filter messages by team ID

        Returns:
            List of message dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id

        response = self.get('/messages/search', params=params)
        return response.get('collection', {}).get('items', [])

    def search_assignments(self, team_id: Optional[int] = None, event_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for assignments (tasks assigned to members)

        Args:
            team_id: Filter assignments by team ID
            event_id: Filter assignments by event ID

        Returns:
            List of assignment dictionaries
        """
        params = {}
        if team_id:
            params['team_id'] = team_id
        if event_id:
            params['event_id'] = event_id

        response = self.get('/assignments/search', params=params)
        return response.get('collection', {}).get('items', [])

    def get_root(self) -> Dict[str, Any]:
        """
        Get API root information (available endpoints and links)

        Returns:
            Root API data with links to available resources
        """
        return self.get('/')

    def custom_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a custom API request for endpoints not covered by convenience methods

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments

        Returns:
            JSON response as dictionary
        """
        response = self._request(method, endpoint, **kwargs)
        return response.json() if response.text else {}


if __name__ == '__main__':
    """Simple test of the client"""
    try:
        # Initialize client
        client = TeamSnapClient()

        # Get current user info
        print("\n📋 Getting user information...")
        me = client.get_me()

        print(f"\n✓ Successfully connected to TeamSnap API!")
        print(f"   User data keys: {list(me.keys())}")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        exit(1)
