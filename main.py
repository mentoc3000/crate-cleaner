import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Authenticate with the necessary permissions
scopes = [
    "user-read-recently-played",
    "playlist-read-private",
    "playlist-modify-private",
    "playlist-modify-public",
]
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scopes,
)
sp = spotipy.Spotify(auth_manager=auth_manager)

PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID")

# 1. Get recently played track IDs (limit 50)
recent = sp.current_user_recently_played(limit=50)
if recent is None:
    print("No recently played tracks found")
    exit(0)
recent_ids = {item['track']['id'] for item in recent['items']}

# 2. Get playlist track IDs
playlist_tracks = sp.playlist_items(PLAYLIST_ID)
if playlist_tracks is None:
    print("No playlist tracks found")
    exit(0)
playlist_ids = [item['item']['id'] for item in playlist_tracks['items']]

# 3. Find intersection (songs to remove)
tracks_to_remove = [tid for tid in playlist_ids if tid in recent_ids]

# 4. Remove them if any match
if tracks_to_remove:
    sp.playlist_remove_all_occurrences_of_items(PLAYLIST_ID, tracks_to_remove)
    print(f"Removed {len(tracks_to_remove)} tracks.")
