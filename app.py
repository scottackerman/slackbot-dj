import os
import sqlite3
import re
from flask import Flask, jsonify, request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

# --- Load env vars ---
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI']
SPOTIFY_PLAYLIST_ID = os.environ['SPOTIFY_PLAYLIST_ID']

slack_client = WebClient(token=SLACK_BOT_TOKEN)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope='playlist-modify-public playlist-modify-private'))

app = Flask(__name__)
conn = sqlite3.connect('added_tracks.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tracks (id TEXT PRIMARY KEY)')
conn.commit()

def extract_track_ids(text):
    return re.findall(r'open\.spotify\.com/track/([a-zA-Z0-9]+)', text)

def track_already_added(track_id):
    c.execute('SELECT 1 FROM tracks WHERE id = ?', (track_id,))
    return c.fetchone() is not None

def mark_track_as_added(track_id):
    c.execute('INSERT OR IGNORE INTO tracks (id) VALUES (?)', (track_id,))
    conn.commit()

def add_tracks_to_playlist(track_ids):
    for track_id in track_ids:
        if not track_already_added(track_id):
            try:
                sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, [track_id])
                mark_track_as_added(track_id)
            except Exception as e:
                print(f"Error adding track {track_id}: {e}")

@app.route('/slack/events', methods=['POST'])
def slack_events():
    try:
        raw_data = request.data
        print("RAW data received:", raw_data)

        data = request.get_json(force=True)
        print("Parsed JSON:", data)

        if data.get('type') == 'url_verification':
            print("Returning Slack challenge:", data['challenge'])
            return jsonify({'challenge': data['challenge']})

        if 'event' in data:
            event = data['event']
            print("Incoming event:", event)
            if event.get('type') == 'message' and 'text' in event:
                track_ids = extract_track_ids(event['text'])
                print("Track IDs:", track_ids)
                add_tracks_to_playlist(track_ids)

    except Exception as e:
        print("ERROR in /slack/events:", str(e))

    return '', 200

def scrape_channel(channel_id):
    try:
        response = slack_client.conversations_history(channel=channel_id)
        messages = response['messages']
        for msg in messages:
            if 'text' in msg:
                track_ids = extract_track_ids(msg['text'])
                add_tracks_to_playlist(track_ids)
            if msg.get('thread_ts'):
                thread = slack_client.conversations_replies(channel=channel_id, ts=msg['ts'])
                for reply in thread['messages']:
                    if 'text' in reply:
                        track_ids = extract_track_ids(reply['text'])
                        add_tracks_to_playlist(track_ids)
    except SlackApiError as e:
        print(f"Slack error: {e.response['error']}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)