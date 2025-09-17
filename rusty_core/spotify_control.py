import spotipy
from spotipy.oauth2 import SpotifyOAuth

import time

from app_manager.app_control import open_app
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
import random
import re
scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))




def ensure_active_device():
    devices = sp.devices().get("devices", [])
    if not devices:
        open_app("spotify")
        time.sleep(15)
        devices = sp.devices().get("devices", [])

    if not devices:
        return None

    # Try to find desktop client first
    desktop_device = None
    for d in devices:
        if d["type"] == "Computer" and d["is_active"]:
            return d["id"]  # already active desktop
        elif d["type"] == "Computer":
            desktop_device = d["id"]

    # If found a desktop device but not active, transfer playback
    if desktop_device:
        sp.transfer_playback(desktop_device, force_play=False)
        return desktop_device

    # Fallback to whatever device is active
    return devices[0]["id"]


def whats_playing():
    playback = sp.current_playback()
    if playback and playback['is_playing']:
        track = playback['item']
        name = track['name']
        artist = track['artists'][0]['name']
        return f"Now playing '{name}' by {artist}."
    return "Nothing is playing right now."

def play_playlist_by_name(name):
    try:
        results = sp.search(q=name, type="playlist", limit=1)
        playlists = results.get("playlists", {}).get("items", [])
        if playlists:
            playlist_uri = playlists[0]["uri"]

            device_id = ensure_active_device()
            if not device_id:
                return "No active device found. Please open Spotify."

            sp.start_playback(device_id=device_id, context_uri=playlist_uri)
            return f"Playing playlist: {playlists[0]['name']}"
        else:
            return "Couldn't find a playlist with that name."
    except Exception as e:
        print("Error playing playlist:", e)
        return "Something went wrong trying to play that playlist."



def play_song(name):
    try:
        results = sp.search(q=name, type="track", limit=1)
        track = results["tracks"]["items"][0]
        uri = track["uri"]

        device_id = ensure_active_device()
        if not device_id:
            return "No active device found. Please open Spotify."

        sp.start_playback(device_id=device_id, uris=[uri])
        return f"Playing: {track['name']} by {track['artists'][0]['name']}"
    except Exception as e:
        print("Error playing song:", e)
        return "Something went wrong trying to play that song."

def get_all_liked_tracks():
    all_tracks = []
    limit = 50
    offset = 0

    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results.get("items", [])
        if not items:
            break

        all_tracks.extend(items)
        offset += limit

    return all_tracks


def play_liked():
    device_id = ensure_active_device()
    if not device_id:
        return "No active Spotify device found."

    liked_tracks = get_all_liked_tracks()
    if not liked_tracks:
        return "Your Liked Songs list is empty."

    track_uris = [item['track']['uri'] for item in liked_tracks]
    random.shuffle(track_uris)

    # 🔑 Force transfer playback
    sp.transfer_playback(device_id, force_play=False)

    # ⏱️ Small delay to let Spotify switch sessions
    time.sleep(1.5)

    # ✅ Double-check active device
    playback = sp.current_playback()
    if not playback or playback["device"]["id"] != device_id:
        return f"Failed to switch playback to desktop (still on {playback['device']['name']})."

    # 🎵 Start playback
    sp.start_playback(device_id=device_id, uris=track_uris[:100])
    return f"Playing {len(track_uris)} of your liked songs on Desktop."

def play_by_artist(artist_name):
    results = sp.search(q=f"artist:{artist_name}", type='artist')
    if results['artists']['items']:
        artist_uri = results['artists']['items'][0]['uri']

        device_id = ensure_active_device()
        if device_id:
            sp.start_playback(device_id=device_id, context_uri=artist_uri)
            return f"🎶 Playing songs by {artist_name}"
        else:
            return "Spotify is open, but no device is active. Try playing a song manually once."
    return f"⚠️ Couldn't find artist '{artist_name}'"




def pause_song():
    sp.pause_playback()
    return "Playback paused."
def shuffle():
    sp.shuffle(state=True)
    return "Songs are on shuffle."
def resume_song():
    sp.start_playback()
    return "Resuming playback."
def prev_song():
    sp.previous_track()
    return("Playing previous song.")

def next_song():
    try:
        sp.next_track()
        return "Skipping to next track."
    except Exception as e:
        print("Skip error:", e)
        return "Couldn't skip the track."

def unmute():
    current=sp.current_playback()
    if current and current["device"]:
        current_volume=current["device"]["volume_percent"]
        sp.volume(current_volume)
        return f"Unmuted audio"
    return "Could not retrieve current volume."

def mute():
    current=sp.current_playback()
    if current and current["device"]:
        current_volume=current["device"]["volume_percent"]
        new_volume = 0
        sp.volume(new_volume)
        return f"Muted audio"
    return "Could not retrieve current volume."





