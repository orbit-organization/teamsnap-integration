"""
TeamSnap OAuth 2.0 Authentication Module

This module handles the OAuth 2.0 authentication flow with TeamSnap
using the out-of-band (OOB) flow for local testing.
"""

import configparser
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
import requests


class TeamSnapAuth:
    """TeamSnap OAuth 2.0 Authentication Handler"""

    AUTH_URL = "https://auth.teamsnap.com/oauth/authorize"
    TOKEN_URL = "https://auth.teamsnap.com/oauth/token"

    def __init__(self, config_file='config.ini'):
        """
        Initialize TeamSnap authentication

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Validate required configuration
        if 'teamsnap' not in self.config:
            raise ValueError(f"Missing [teamsnap] section in {config_file}")

        self.client_id = self.config['teamsnap'].get('client_id')
        self.client_secret = self.config['teamsnap'].get('client_secret')
        self.redirect_uri = self.config['teamsnap'].get('redirect_uri', 'urn:ietf:wg:oauth:2.0:oob')

        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret must be set in config file")

        if self.client_id == 'YOUR_CLIENT_ID_HERE' or self.client_secret == 'YOUR_CLIENT_SECRET_HERE':
            raise ValueError("Please replace placeholder values in config file with your actual credentials")

    def get_authorization_url(self, scope='read write'):
        """
        Generate the OAuth authorization URL

        Args:
            scope: OAuth scopes (default: 'read write')

        Returns:
            Authorization URL string
        """
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope
        }

        query_string = urllib.parse.urlencode(params)
        return f"{self.AUTH_URL}?{query_string}"

    def exchange_code_for_token(self, authorization_code):
        """
        Exchange authorization code for access token

        Args:
            authorization_code: Code received from TeamSnap

        Returns:
            Token response dictionary
        """
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }

        print("\n🔄 Exchanging authorization code for access token...")

        response = requests.post(self.TOKEN_URL, data=data)

        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.status_code} - {response.text}")

        token_data = response.json()

        # Save tokens to config file
        self.config['teamsnap']['access_token'] = token_data.get('access_token', '')
        self.config['teamsnap']['refresh_token'] = token_data.get('refresh_token', '')

        # Calculate token expiration
        expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        self.config['teamsnap']['token_expires_at'] = expires_at.isoformat()

        # Write updated config
        with open(self.config_file, 'w') as f:
            self.config.write(f)

        print("✓ Access token obtained and saved!")
        return token_data

    def authenticate(self):
        """
        Run complete OAuth authentication flow using out-of-band (OOB) method

        Returns:
            Access token string
        """
        print("\n" + "="*70)
        print("TeamSnap OAuth 2.0 Authentication (Out-of-Band)")
        print("="*70)

        # Generate authorization URL
        auth_url = self.get_authorization_url()

        print(f"\n📋 Using redirect URI: {self.redirect_uri}")
        print("\n🔐 Opening browser for authorization...")
        print("    TeamSnap will display an authorization code in your browser.")
        print(f"\n    If browser doesn't open automatically, visit this URL:")
        print(f"    {auth_url}\n")

        # Open browser
        try:
            webbrowser.open(auth_url)
        except:
            print("⚠️  Could not open browser automatically")

        # Prompt user to enter the code
        print("="*70)
        print("After authorizing the application in your browser:")
        print("1. TeamSnap will display an authorization code")
        print("2. Copy the code from the browser")
        print("3. Paste it below")
        print("="*70)

        # Get authorization code from user
        authorization_code = input("\n📝 Enter the authorization code: ").strip()

        if not authorization_code:
            raise Exception("No authorization code provided")

        # Exchange code for token
        token_data = self.exchange_code_for_token(authorization_code)

        print("\n" + "="*70)
        print("✓ Authentication Complete!")
        print("="*70)
        print(f"\nAccess token saved to: {self.config_file}")
        print("You can now use the TeamSnap API client.\n")

        return token_data['access_token']

    def get_access_token(self):
        """
        Get current access token from config

        Returns:
            Access token string or None
        """
        return self.config['teamsnap'].get('access_token')

    def is_token_valid(self):
        """
        Check if current access token is still valid

        Returns:
            Boolean indicating token validity
        """
        token = self.get_access_token()
        if not token:
            return False

        expires_at_str = self.config['teamsnap'].get('token_expires_at')
        if not expires_at_str:
            # No expiration info, assume valid
            return True

        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            return datetime.now() < expires_at
        except:
            return True


if __name__ == '__main__':
    """Standalone authentication script"""
    try:
        auth = TeamSnapAuth()
        auth.authenticate()
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        exit(1)
