# Slack to Spotify Playlist Bot

This bot listens to a Slack channel for Spotify links and automatically adds them to a Spotify playlist.

## Features
- Scrapes existing messages (including threads)
- Listens for new messages
- Avoids duplicate songs using SQLite

## Setup

1. Clone this repo and install dependencies:

```bash
pip install flask slack_sdk spotipy
```

2. Create a `.env` file or export these environment variables:

```bash
SLACK_BOT_TOKEN=your-token
SPOTIPY_CLIENT_ID=your-client-id
SPOTIPY_CLIENT_SECRET=your-client-secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_PLAYLIST_ID=your-playlist-id
```

3. Run the bot:

```bash
python app.py
```

4. Expose it to the web for Slack (e.g., using `ngrok`):

```bash
ngrok http 3000
```

Set the Slack Event URL to: `https://<ngrok-url>/slack/events`

## Manually Scrape a Channel

In `app.py`, call:

```python
scrape_channel('your-channel-id')
```

Happy listening 🎶