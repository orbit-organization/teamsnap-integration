"""
Tests for TeamSnap MCP Server
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestMCPServerTools:
    """Test MCP server tool functions"""

    @pytest.mark.asyncio
    async def test_list_teams_import(self):
        """Test that list_teams tool can be imported"""
        from server import list_teams
        assert callable(list_teams)

    @pytest.mark.asyncio
    async def test_get_team_details_import(self):
        """Test that get_team_details tool can be imported"""
        from server import get_team_details
        assert callable(get_team_details)

    @pytest.mark.asyncio
    async def test_list_events_import(self):
        """Test that list_events tool can be imported"""
        from server import list_events
        assert callable(list_events)

    @pytest.mark.asyncio
    async def test_create_event_import(self):
        """Test that create_event tool can be imported"""
        from server import create_event
        assert callable(create_event)

    @pytest.mark.asyncio
    async def test_update_event_import(self):
        """Test that update_event tool can be imported"""
        from server import update_event
        assert callable(update_event)

    @pytest.mark.asyncio
    async def test_delete_event_import(self):
        """Test that delete_event tool can be imported"""
        from server import delete_event
        assert callable(delete_event)

    @pytest.mark.asyncio
    async def test_create_member_import(self):
        """Test that create_member tool can be imported"""
        from server import create_member
        assert callable(create_member)

    @pytest.mark.asyncio
    async def test_update_availability_import(self):
        """Test that update_availability tool can be imported"""
        from server import update_availability
        assert callable(update_availability)

    @pytest.mark.asyncio
    async def test_create_assignment_import(self):
        """Test that create_assignment tool can be imported"""
        from server import create_assignment
        assert callable(create_assignment)

    @pytest.mark.asyncio
    async def test_create_location_import(self):
        """Test that create_location tool can be imported"""
        from server import create_location
        assert callable(create_location)


class TestToolOutput:
    """Test that tools return proper MCP TextContent format"""

    @pytest.mark.asyncio
    async def test_list_teams_output_format(self, mock_env, sample_search_results):
        """Test list_teams returns TextContent"""
        from server import list_teams
        from client import TeamSnapAsyncClient

        with patch.object(TeamSnapAsyncClient, 'search_teams', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = sample_search_results['collection']['items']

            result = await list_teams()

            assert isinstance(result, list)
            assert len(result) > 0
            assert hasattr(result[0], 'type')
            assert result[0].type == "text"
            assert hasattr(result[0], 'text')
            assert isinstance(result[0].text, str)

    @pytest.mark.asyncio
    async def test_list_events_output_format(self, mock_env, sample_search_results):
        """Test list_events returns TextContent"""
        from server import list_events
        from client import TeamSnapAsyncClient

        with patch.object(TeamSnapAsyncClient, 'search_events', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = sample_search_results['collection']['items']

            result = await list_events(team_id=12345)

            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0].type == "text"
            assert isinstance(result[0].text, str)

    @pytest.mark.asyncio
    async def test_create_event_success_format(self, mock_env, sample_event_data):
        """Test create_event returns success message"""
        from server import create_event
        from client import TeamSnapAsyncClient

        # Disable readonly mode for this test
        with patch('os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'TEAMSNAP_ACCESS_TOKEN': 'test_token',
                'TEAMSNAP_READONLY': 'false'
            }.get(key, default)

            with patch.object(TeamSnapAsyncClient, 'create_event', new_callable=AsyncMock) as mock_create:
                mock_create.return_value = sample_event_data

                result = await create_event(
                    team_id=12345,
                    name="Practice",
                    start_date="2025-01-15T14:00:00Z"
                )

                assert isinstance(result, list)
                assert len(result) > 0
                assert result[0].type == "text"
                assert "Successfully created" in result[0].text or "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_create_event_error_format(self, mock_env):
        """Test create_event returns error message on failure"""
        from server import create_event
        from client import TeamSnapAsyncClient

        with patch.object(TeamSnapAsyncClient, 'create_event', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("API Error")

            result = await create_event(
                team_id=12345,
                name="Practice",
                start_date="2025-01-15T14:00:00Z"
            )

            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0].type == "text"
            assert "Error" in result[0].text or "❌" in result[0].text

    @pytest.mark.asyncio
    async def test_update_availability_valid_status(self, mock_env):
        """Test update_availability accepts valid status"""
        from server import update_availability
        from client import TeamSnapAsyncClient

        with patch.object(TeamSnapAsyncClient, 'update_availability', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {"status": "yes"}

            result = await update_availability(availability_id=999, status="yes")

            assert isinstance(result, list)
            assert "Successfully" in result[0].text or "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_update_availability_invalid_status(self, mock_env):
        """Test update_availability rejects invalid status"""
        from server import update_availability

        result = await update_availability(availability_id=999, status="invalid_status")

        assert isinstance(result, list)
        assert "Invalid status" in result[0].text or "❌" in result[0].text

    @pytest.mark.asyncio
    async def test_update_event_no_fields(self, mock_env):
        """Test update_event handles no fields provided"""
        from server import update_event

        # Disable readonly mode for this test
        with patch('os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                'TEAMSNAP_ACCESS_TOKEN': 'test_token',
                'TEAMSNAP_READONLY': 'false'
            }.get(key, default)

            result = await update_event(event_id=12345)

            assert isinstance(result, list)
            assert "No fields provided" in result[0].text


class TestServerInitialization:
    """Test MCP server initialization"""

    def test_server_app_exists(self):
        """Test that server mcp instance exists"""
        from server import mcp
        assert mcp is not None

    def test_get_client_function_exists(self):
        """Test that get_client function exists"""
        from server import get_client
        assert callable(get_client)

    def test_get_client_returns_client(self, mock_env):
        """Test that get_client returns a TeamSnapAsyncClient"""
        from server import get_client
        from client import TeamSnapAsyncClient

        client = get_client()
        assert isinstance(client, TeamSnapAsyncClient)
