import spotify_control as sc
from app_manager.app_control import open_app, close_app
from memory import remember, recall, list_memory, clear_memory
from style_learning import teach_command
from gpt_conversation import generate_response

import re

def handle_intent(intent, user_input):
    # ----- SPOTIFY INTENTS ----------
    if intent == "play_music":
        return sc.play_song(user_input.replace("play", "").strip())

    elif intent == "play_playlist":
        return sc.play_playlist_by_name(user_input.replace("play", "").strip())

    elif intent == "play_album":
        return sc.play_album(user_input.replace("play songs from", "").strip())

    elif intent == "play_artist":
        return sc.play_by_artist(user_input.replace("play songs by", "").strip())

    elif intent == "play_liked":
        return sc.play_liked()

    elif intent == "prev_song":
        return sc.prev_song()

    elif intent == "next_song" or intent == "next_music":
        return sc.next_song()

    elif intent == "pause_music":
        return sc.pause_song()

    elif intent == "resume_music":
        return sc.resume_song()

    elif intent == "volume_up":
        return sc.increase_volume()

    elif intent == "volume_down":
        return sc.decrease_volume()

    elif intent == "set_volume":
        match = re.search(r'\b(\d+)\b', user_input)
        if match:
            volume = int(match.group(1))
            return sc.set_volume(volume)
        return "Please say a number between 0 and 100."

    elif intent == "mute":
        return sc.mute()

    elif intent == "shuffle":
        return sc.shuffle()

    elif intent == "whats_playing":
        return sc.whats_playing()

    # --------- MEMORY INTENTS -------------
    elif intent == "remember_fact":
        parts = user_input.lower().replace("remember that", "").replace("remember", "").strip().split(" is ")
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            return remember(key, value)
        return "Please say something like 'remember my name is Rusty'."

    elif intent == "recall_fact":
    # avoid misfired math questions etc.
        if any(char.isdigit() for char in user_input) and "what is" in user_input:
            return generate_response(user_input)  # treat as chat
        key = user_input.lower().replace("what is", "").strip()
        return recall(key)


    elif intent == "list_memory":
        return list_memory()

    elif intent == "clear_memory":
        return clear_memory()

    # --------- INTENT TEACHING ----------
    # elif intent == "teach_command":
    #     try:
    #         parts = user_input.lower().split(" it means ")
    #         if len(parts) == 2:
    #             user_phrase, actual_intent = parts
    #             return teach_command(user_phrase.strip())
    #         else:
    #             return "Please say it like: 'when I say open DC, it means open Discord'."
    #     except:
    #         return "Something went wrong while learning that command."
    elif intent == "teach_command":
        try:
            return teach_command(user_input)
        except:
            return "Something went wrong while learning that command."

    # --------- APP CONTROL ----------
    elif intent == "open_app":
        return open_app(user_input.replace("open", "").strip())

    elif intent == "close_app":
        return close_app(user_input.replace("close", "").strip())
    elif intent == "chat":
        return generate_response(user_input)
    else:
        return "Sorry, I don't know how to handle that yet."
