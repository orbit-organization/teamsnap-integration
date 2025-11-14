"""
Tests for TeamSnap Async Client
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from client import TeamSnapAsyncClient


class TestTeamSnapAsyncClient:
    """Test the async TeamSnap client"""

    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_env, mock_access_token):
        """Test client initializes with access token from environment"""
        client = TeamSnapAsyncClient()
        assert client.access_token == mock_access_token

    @pytest.mark.asyncio
    async def test_client_initialization_with_token(self):
        """Test client initializes with provided token"""
        token = "provided_token"
        client = TeamSnapAsyncClient(access_token=token)
        assert client.access_token == token

    def test_client_initialization_no_token(self, monkeypatch):
        """Test client raises error without token"""
        monkeypatch.delenv("TEAMSNAP_ACCESS_TOKEN", raising=False)

        with pytest.raises(ValueError, match="No access token provided"):
            TeamSnapAsyncClient()

    @pytest.mark.asyncio
    async def test_extract_item_data(self, mock_env, sample_team_data):
        """Test extracting data from Collection+JSON format"""
        client = TeamSnapAsyncClient()

        item = sample_team_data["collection"]["items"][0]
        extracted = client.extract_item_data(item)

        assert extracted["id"] == 12345
        assert extracted["name"] == "Test Team"
        assert extracted["sport_name"] == "Soccer"

    @pytest.mark.asyncio
    async def test_search_teams(self, mock_env, sample_search_results):
        """Test searching teams"""
        with patch.object(
            TeamSnapAsyncClient, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = sample_search_results

            async with TeamSnapAsyncClient() as client:
                teams = await client.search_teams()

                mock_get.assert_called_once_with("/teams/search", params={})
                assert len(teams) == 3

    @pytest.mark.asyncio
    async def test_search_teams_with_user_id(self, mock_env, sample_search_results):
        """Test searching teams with user_id filter"""
        with patch.object(
            TeamSnapAsyncClient, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = sample_search_results

            async with TeamSnapAsyncClient() as client:
                await client.search_teams(user_id=123)

                mock_get.assert_called_once_with(
                    "/teams/search", params={"user_id": 123}
                )

    @pytest.mark.asyncio
    async def test_get_team(self, mock_env, sample_team_data):
        """Test getting specific team"""
        with patch.object(
            TeamSnapAsyncClient, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = sample_team_data

            async with TeamSnapAsyncClient() as client:
                team = await client.get_team(12345)

                mock_get.assert_called_once_with("/teams/12345")
                assert team == sample_team_data

    @pytest.mark.asyncio
    async def test_search_events(self, mock_env, sample_search_results):
        """Test searching events"""
        with patch.object(
            TeamSnapAsyncClient, "get", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = sample_search_results

            async with TeamSnapAsyncClient() as client:
                events = await client.search_events(team_id=12345)

                mock_get.assert_called_once_with(
                    "/events/search", params={"team_id": 12345}
                )
                assert len(events) == 3

    @pytest.mark.asyncio
    async def test_create_event(self, mock_env, sample_event_data):
        """Test creating an event"""
        with patch.object(
            TeamSnapAsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = sample_event_data

            async with TeamSnapAsyncClient() as client:
                await client.create_event(
                    team_id=12345,
                    name="Practice",
                    start_date="2025-01-15T14:00:00Z",
                    notes="Bring water",
                )

                mock_post.assert_called_once()
                args = mock_post.call_args
                assert args[0][0] == "/events"
                assert args[1]["data"]["team_id"] == 12345
                assert args[1]["data"]["name"] == "Practice"

    @pytest.mark.asyncio
    async def test_update_event(self, mock_env, sample_event_data):
        """Test updating an event"""
        with patch.object(
            TeamSnapAsyncClient, "patch", new_callable=AsyncMock
        ) as mock_patch:
            mock_patch.return_value = sample_event_data

            async with TeamSnapAsyncClient() as client:
                await client.update_event(
                    67890, name="Updated Practice", notes="New notes"
                )

                mock_patch.assert_called_once()
                args = mock_patch.call_args
                assert args[0][0] == "/events/67890"
                assert args[1]["data"]["name"] == "Updated Practice"

    @pytest.mark.asyncio
    async def test_delete_event(self, mock_env):
        """Test deleting an event"""
        with patch.object(
            TeamSnapAsyncClient, "delete", new_callable=AsyncMock
        ) as mock_delete:
            mock_delete.return_value = {}

            async with TeamSnapAsyncClient() as client:
                await client.delete_event(67890)

                mock_delete.assert_called_once_with("/events/67890")

    @pytest.mark.asyncio
    async def test_create_member(self, mock_env, sample_member_data):
        """Test creating a member"""
        with patch.object(
            TeamSnapAsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = sample_member_data

            async with TeamSnapAsyncClient() as client:
                await client.create_member(
                    team_id=12345,
                    first_name="John",
                    last_name="Doe",
                    email="john@example.com",
                )

                mock_post.assert_called_once()
                args = mock_post.call_args
                assert args[0][0] == "/members"
                assert args[1]["data"]["first_name"] == "John"
                assert args[1]["data"]["last_name"] == "Doe"

    @pytest.mark.asyncio
    async def test_update_availability(self, mock_env):
        """Test updating availability status"""
        with patch.object(
            TeamSnapAsyncClient, "patch", new_callable=AsyncMock
        ) as mock_patch:
            mock_patch.return_value = {"status": "yes"}

            async with TeamSnapAsyncClient() as client:
                await client.update_availability(999, "yes")

                mock_patch.assert_called_once()
                args = mock_patch.call_args
                assert args[0][0] == "/availabilities/999"
                assert args[1]["data"]["status"] == "yes"

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_env):
        """Test client works as async context manager"""
        async with TeamSnapAsyncClient() as client:
            assert client.access_token is not None

        # Client should be closed after context
        # (httpx client would be closed)

    @pytest.mark.asyncio
    async def test_get_api_version(self, mock_env):
        """Test getting API version"""
        root_response = {"collection": {"version": "3.867.0"}}

        with patch.object(
            TeamSnapAsyncClient, "get_root", new_callable=AsyncMock
        ) as mock_root:
            mock_root.return_value = root_response

            async with TeamSnapAsyncClient() as client:
                version = await client.get_api_version()

                assert version == "3.867.0"
                assert client.api_version == "3.867.0"

    @pytest.mark.asyncio
    async def test_http_error_handling(self, mock_env):
        """Test HTTP error handling"""
        import httpx

        with patch.object(
            TeamSnapAsyncClient, "_request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError(
                "404 Not Found",
                request=MagicMock(),
                response=MagicMock(status_code=404, text="Not found"),
            )

            async with TeamSnapAsyncClient() as client:
                with pytest.raises(httpx.HTTPStatusError):
                    await client.get("/invalid/endpoint")
