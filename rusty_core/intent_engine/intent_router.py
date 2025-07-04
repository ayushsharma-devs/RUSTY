import re
import spotify_control as sc
from app_manager.app_control import open_app, close_app, extract_app_name
from memory import  list_memory, recent_mention, clear_memory,store_fact as remember, query_fact as recall, query_episode, store_episode, delete_fact, get_memory
from style_learning import teach_command
from gpt_conversation import generate_response
from system_control import handle_system_command

def handle_intent(intent, user_input):
    lowered = user_input.lower().strip()
    if intent in ["set_volume", "battery", "mute", "unmute","screenshot", "lock", "shutdown", "sleep", "restart"]:
        return handle_system_command(lowered)
    # --------- SPOTIFY INTENTS ----------
    if intent == "play_music":
        song_query = lowered.replace("play", "").strip()
        if len(song_query.split()) < 2:
            return generate_response(user_input)  # vague "play" fallback
        return sc.play_song(song_query)

    elif intent == "play_playlist":
        return sc.play_playlist_by_name(lowered.replace("play playlist", "").strip())

    elif intent == "play_album":
        return sc.play_album(lowered.replace("play album", "").strip())

    elif intent == "play_artist":
        return sc.play_by_artist(lowered.replace("play songs by", "").strip())

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

    elif intent == "unmute music":
        return sc.unmute()

    elif intent == "mute music":
        return sc.mute()

    elif intent == "shuffle":
        return sc.shuffle()

    elif intent == "whats_playing":
        return sc.whats_playing()

    # --- Memory Core Intents ---

    elif intent == "remember_fact":
        match = re.search(r"(?:remember(?: that)?|can you remember(?: that)?) (.*?) is (.*)", lowered)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            return remember(key, value)
        return "Please say something like 'remember my birthday is June 1st'."

    elif intent == "recall_fact":
        if any(char.isdigit() for char in lowered) and "what is" in lowered:
            return generate_response(user_input)

        key = (
        lowered.replace("what is", "")
        .replace("what do you remember about", "")
        .replace("what do you know about", "")
        .replace("do you remember", "")
        .replace("what's my", "")
        .strip()
    )
        return recall(key)

    elif intent == "forget_fact":
        match = re.search(r"(?:forget(?: about)?|delete memory of) (.+)", user_input)
        if match:
            key = match.group(1).strip()
            return delete_fact(key)
        return "Say something like 'forget my birthday' or 'delete memory of my dog's name'."

    elif intent == "list_memory":
        return list_memory()

    elif intent == "clear_memory":
        return clear_memory()

    elif intent == "recall_recent":
        if "what did i say about" in lowered:
            topic = lowered.split("what did i say about", 1)[1].strip()
            response = recent_mention(topic)
            return f"You said: '{response}'" if response else f"I don’t remember you mentioning {topic} recently."
        elif "did i mention" in lowered:
            topic = lowered.split("did i mention", 1)[1].strip()
            response = recent_mention(topic)
            return f"You mentioned: '{response}'" if response else f"I don’t remember you mentioning {topic} recently."
        elif "what was i saying about" in lowered:
            topic = lowered.split("what was i saying about", 1)[1].strip()
            response = recent_mention(topic)
            return f"You were saying: '{response}'" if response else f"I don’t recall what you said about {topic}."
        return "Try saying something like 'what did I say about football?'"

# --- Episodic Memory ---

    elif intent == "recall_episode":
        topic = ""
        for phrase in ["what happened when", "what did we talk about", "remind me what i said about"]:
            if phrase in lowered:
                topic = lowered.split(phrase)[-1].strip()
                break
        return query_episode(topic) if topic else "Try saying something like 'what happened when we talked about the gym?'"

    elif intent == "store_episode":
        match = re.search(r"(?:remember|store) (?:this )?(?:conversation|chat|as)?(?: our )?(?:talk|chat|conversation)?(?: about)? (.+)", lowered)
        if match:
            topic = match.group(1).strip()
            context = get_memory()
            if len(context) >= 2:
                user_line = context[-2]["parts"][0]
                assistant_line = context[-1]["parts"][0]
                store_episode(topic, user_line, assistant_line)
                return f"Stored this as our talk about '{topic}'."
            else:
                return "Not enough context to save a conversation."
        return "Say something like 'remember this as our chat about productivity'."

    # --------- APP CONTROL ----------
    elif intent == "open_app":
        app_name = extract_app_name(user_input)
        return open_app(app_name) if app_name else "⚠️ Sorry, I couldn't understand which app to open."

    elif intent == "close_app":
        app_name = extract_app_name(user_input)
        return close_app(app_name) if app_name else "⚠️ Sorry, I couldn't understand which app to close."

    # --------- DEFAULT FALLBACK ----------
    elif intent == "chat":
        return generate_response(user_input)

    return "⚠️ I don’t know how to handle that yet."
