"""
Shared test fixtures for TeamSnap MCP Server tests
"""

import pytest


@pytest.fixture
def mock_access_token():
    """Mock access token for testing"""
    return "test_token_12345"


@pytest.fixture
def mock_env(mock_access_token, monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv("TEAMSNAP_ACCESS_TOKEN", mock_access_token)


@pytest.fixture
def sample_team_data():
    """Sample team data in Collection+JSON format"""
    return {
        "collection": {
            "version": "3.867.0",
            "items": [
                {
                    "data": [
                        {"name": "id", "value": 12345},
                        {"name": "name", "value": "Test Team"},
                        {"name": "sport_name", "value": "Soccer"},
                        {"name": "season_name", "value": "Fall 2025"},
                        {"name": "division_name", "value": "Division 1"},
                        {"name": "location_country", "value": "US"},
                    ]
                }
            ],
        }
    }


@pytest.fixture
def sample_event_data():
    """Sample event data in Collection+JSON format"""
    return {
        "collection": {
            "items": [
                {
                    "data": [
                        {"name": "id", "value": 67890},
                        {"name": "name", "value": "Practice"},
                        {"name": "start_date", "value": "2025-01-15T14:00:00Z"},
                        {"name": "is_game", "value": False},
                        {"name": "location_name", "value": "Home Field"},
                        {"name": "notes", "value": "Bring water"},
                    ]
                }
            ]
        }
    }


@pytest.fixture
def sample_member_data():
    """Sample member data in Collection+JSON format"""
    return {
        "collection": {
            "items": [
                {
                    "data": [
                        {"name": "id", "value": 11111},
                        {"name": "first_name", "value": "John"},
                        {"name": "last_name", "value": "Doe"},
                        {"name": "email", "value": "john@example.com"},
                        {"name": "phone", "value": "555-1234"},
                        {"name": "is_manager", "value": False},
                        {"name": "is_non_player", "value": False},
                    ]
                }
            ]
        }
    }


@pytest.fixture
def sample_search_results():
    """Sample search results with multiple items"""
    return {
        "collection": {
            "items": [
                {
                    "data": [
                        {"name": "id", "value": 1},
                        {"name": "name", "value": "Item 1"},
                    ]
                },
                {
                    "data": [
                        {"name": "id", "value": 2},
                        {"name": "name", "value": "Item 2"},
                    ]
                },
                {
                    "data": [
                        {"name": "id", "value": 3},
                        {"name": "name", "value": "Item 3"},
                    ]
                },
            ]
        }
    }
