# TeamSnap Integration - Quick Start Guide

## What You Need

1. Your TeamSnap Client ID and Client Secret from https://auth.teamsnap.com/oauth/applications/8481
2. Python 3.8+ installed on your computer
3. `uv` package manager (recommended) or `pip`

## Setup (3 Steps)

### Step 1: Install Dependencies

**Using uv (recommended - fast!):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -r requirements.txt
```

### Step 2: Configure TeamSnap OAuth Application

Go to: https://auth.teamsnap.com/oauth/applications/8481

Set the **Redirect URI** to exactly:
```
urn:ietf:wg:oauth:2.0:oob
```

### Step 3: Add Your Credentials

Edit `config.ini` and replace:

```ini
[teamsnap]
client_id = YOUR_ACTUAL_CLIENT_ID_HERE
client_secret = YOUR_ACTUAL_CLIENT_SECRET_HERE
redirect_uri = urn:ietf:wg:oauth:2.0:oob
```

## Run It!

**Using uv:**
```bash
uv run python example.py
```

**Using pip/regular Python:**
```bash
python example.py
```

## What Happens

1. Browser opens to TeamSnap login
2. You approve the application
3. TeamSnap shows you an authorization code
4. Copy the code
5. Paste it in the terminal when prompted
6. Done! Your token is saved and the example runs

## Troubleshooting

**Can't add the redirect URI?**
- Make sure you're using exactly: `urn:ietf:wg:oauth:2.0:oob`
- TeamSnap doesn't allow `localhost` URLs

**Code doesn't show in browser?**
- Check that your redirect URI in TeamSnap settings is correct
- Try the URL printed in the terminal manually

**Invalid client error?**
- Double-check your Client ID and Secret in `config.ini`
- Make sure there are no extra spaces

## Next Steps

Once you have it working, check out:
- `teamsnap_client.py` - API client with all available methods
- `README.md` - Full documentation
- Customize `example.py` for your needs

## Need Help?

See the full README.md for detailed documentation and troubleshooting.
