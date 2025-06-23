intent_keywords = {

   # --- Spotify intents (cleaned and disambiguated) ---

    "play_liked": [
        "play liked songs", 
    "play my liked songs", 
    "play liked", 
    "play like songs"
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

"volume_up": [
    "increase volume", 
    "volume up", 
    "make it louder", 
    "raise the volume"
],

"volume_down": [
    "decrease volume", 
    "volume down", 
    "make it quieter", 
    "lower the volume"
],

"set_volume": [
    "set volume to", 
    "volume to", 
    "set it to"
],

"mute": [
    "mute", 
    "mute audio", 
    "silence music"
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
    ]
}
