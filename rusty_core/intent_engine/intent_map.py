intent_keywords = {

   # --- Spotify intents (cleaned and disambiguated) ---

    "play_liked": [
        "play liked songs", 
    "play my liked songs", 
    "play liked", 
    "play like songs",
    "play like music",
    "play liked music"
    ],

"play_playlist": [
    "play playlist", 
    "start playlist", 
    "listen to playlist", 
    "play my playlist"
],

"play_album": [
    "play album", 
    "play the album", 
    "start the album"
],

"play_artist": [
    "play songs by", 
    "play music by", 
    "play artist", 
    "listen to artist"
    # ❌ Removed just "artist"
],

"play_music": [
    "play music", 
    "play some music", 
    "start playing music", 
    "put on music", 
    "start song"
    # ❌ Removed just "play"
    # ❌ Removed "put on" (too vague)
],

"pause_music": [
    "pause music", 
    "stop music", 
    "shut up", 
    "pause the song"
],

"resume_music": [
    "resume music", 
    "continue song", 
    "unpause"
],

"next_music": [
    "next song", 
    "skip this", 
    "next track", 
    "play next"
    # ❌ Removed just "next"
],


"mute music": [ 
    "mute music", 
    "silence music",
    "mute spotify"
],

"unmute music": [
    "unmute music", 
    "unmute spotify"
],

"shuffle": [
    "shuffle", 
    "shuffle songs", 
    "put it on shuffle"
],

"prev_song": [
    "previous song", 
    "play previous", 
    "go back", 
    "last song"
],

"whats_playing": [
    "what is playing", 
    "what is the song", 
    "what song is this", 
    "what's playing"
],

# --- System control intents ---
"set_volume": [
    "set volume to", 
    "volume to", 
    "set it to"
],

"battery": [
    "battery",
    "battery level",
    "battery percentage",
    "battery status",
],
"screenshot": [
    "screenshot",
    "take a screenshot",
    "capture screen",
    "screenshot of",
],

"lock": [
    "lock",
    "lock screen",
    "lock the screen",
    "lock the computer",
],
"shutdown": [
    "shutdown",
    "shut down",
    "turn off",
    "power off",
],
"sleep": [
    "sleep",
    "sleep mode",
    "sleep the computer",
    "sleep the laptop",
],
"restart": [
    "restart",
    "restart the computer",
    "restart the laptop",
],

"mute": [
    "mute",
    "mute audio"
],
"unmute": [
    "unmute",
    "unmute audio"
],



    #app manager intent
    "open_app": ["open ", "launch", "start", "run"],
    "close_app": ["close", "exit", "stop", "terminate"],

    #memory intent
    "teach_command": ["when i say", "teach rusty", "means"],
    "recall_fact": [
        "what is",
        "what do you remember about",
        "what do you know about",
        "do you remember",
        "what's my",
    ],
    "remember_fact": [
        "remember that",
        "remember",
        "remember my name is",
        "remember my birthday is",
        "can you remember that",
        "note that",
    ],

    

    "recall_recent": [
        "what did i say about",
        "did i mention",
        "what was i saying about",
    ],

    "forget_fact": [
        "forget",
        "forget what i told you about",
        "forget about",
        "delete memory of",
    ],

    "list_memory": [
        "list memory",
        "what do you remember",
        "show memory",
        "what have i told you",
    ],

    "clear_memory": [
        "clear memory",
        "reset memory",
        "forget everything",
        "wipe memory",
    ],
    "recall_episode": [
    "what happened when",
    "what did we talk about",
    "remind me what i said about",
],

"store_episode": [
    "remember this conversation",
    "remember this as our talk about",
    "save this as",
    "store this conversation"
]
}
