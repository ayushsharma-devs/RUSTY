import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
import subprocess
from app_manager.app_control import open_app
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

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
        time.sleep(5)
        devices = sp.devices().get("devices", [])
    if not devices:
        return None
    return devices[0]["id"]


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
    
def play_liked():

    device_id = ensure_active_device()
    if not device_id:
        return "No active Spotify device found."

    tracks = sp.current_user_saved_tracks(limit=1)['items']
    if not tracks:
        return "Your Liked Songs list is empty."

    track_uri = tracks[0]['track']['uri']
    sp.start_playback(device_id=device_id, uris=[track_uri])
    return "Playing your liked songs."
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


def play_album(album_name):
    results = sp.search(q=album_name, type='album')
    if results['albums']['items']:
        album_uri = results['albums']['items'][0]['uri']

        device_id = ensure_active_device()
        if device_id:
            sp.start_playback(device_id=device_id, context_uri=album_uri)
            return f"🎵 Playing album {album_name}"
        else:
            return "Spotify is open, but no device is active. Try playing a song manually once."
    return f"⚠️ Couldn't find album '{album_name}'"




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

def set_volume(percent):
    if 0 <= percent <= 100:
        sp.volume(percent)
        return f"Volume set to {percent}%."
    return "Volume must be between 0 and 100."

def increase_volume(step=10):
    current = sp.current_playback()
    if current and current["device"]:
        current_volume = current["device"]["volume_percent"]
        new_volume = min(100, current_volume + step)
        sp.volume(new_volume)
        return f"Increased volume to {new_volume}%."
    return "Could not retrieve current volume."

def decrease_volume(step=10):
    current = sp.current_playback()
    if current and current["device"]:
        current_volume = current["device"]["volume_percent"]
        new_volume = max(0, current_volume - step)
        sp.volume(new_volume)
        return f"Decreased volume to {new_volume}%."
    return "Could not retrieve current volume."

def mute():
    current=sp.current_playback()
    if current and current["device"]:
        current_volume=current["device"]["volume_percent"]
        new_volume = 0
        sp.volume(new_volume)
        return f"Muted audio"
    return "Could not retrieve current volume."





