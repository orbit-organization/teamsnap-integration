"""
Basic tests to ensure modules can be imported and have expected structure.

These tests don't require authentication and can run in CI.
"""

import pytest


def test_import_teamsnap_client():
    """Test that TeamSnapClient can be imported"""
    from teamsnap_client import TeamSnapClient

    assert TeamSnapClient is not None


def test_import_teamsnap_auth():
    """Test that TeamSnapAuth can be imported"""
    from teamsnap_auth import TeamSnapAuth

    assert TeamSnapAuth is not None


def test_client_has_methods():
    """Test that TeamSnapClient has expected methods"""
    from teamsnap_client import TeamSnapClient

    expected_methods = [
        "get_me",
        "search_teams",
        "search_members",
        "search_events",
        "search_forum_topics",
        "search_forum_posts",
        "search_broadcast_emails",
        "search_messages",
        "search_assignments",
        "get_root",
        "custom_request",
    ]

    for method in expected_methods:
        assert hasattr(TeamSnapClient, method), (
            f"TeamSnapClient missing {method} method"
        )


def test_client_constants():
    """Test that TeamSnapClient has correct API constants"""
    from teamsnap_client import TeamSnapClient

    assert hasattr(TeamSnapClient, "BASE_URL")
    assert TeamSnapClient.BASE_URL == "https://api.teamsnap.com/v3"


def test_auth_constants():
    """Test that TeamSnapAuth has correct OAuth constants"""
    from teamsnap_auth import TeamSnapAuth

    assert hasattr(TeamSnapAuth, "AUTH_URL")
    assert hasattr(TeamSnapAuth, "TOKEN_URL")
    assert TeamSnapAuth.AUTH_URL == "https://auth.teamsnap.com/oauth/authorize"
    assert TeamSnapAuth.TOKEN_URL == "https://auth.teamsnap.com/oauth/token"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
