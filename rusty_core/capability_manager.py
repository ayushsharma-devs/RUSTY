import re

class CapabilityManager:
    def __init__(self):
        self.capabilities = {
            "shortcuts": {
                "desc": "Learn your custom shortcuts (e.g., 'open dc' → Discord).",
                "example": "Say: 'remember that open dc means open discord'."
            },
            "reminder": {
                "desc": "Set reminders and alarms.",
                "example": "Say: 'remind me to drink water in 10 minutes'."
            },
            "spotify": {
                "desc": "Control Spotify (play, pause, skip, etc.).",
                "example": "Say: 'play lo-fi beats on Spotify'."
            },
            "open_app": {
                "desc": "Open apps with shortcuts.",
                "example": "Say: 'open dc' to launch Discord."
            }
        }
        self.state = {"last_intent": None, "last_capability": None}

    def handle(self, user_input: str) -> str:
        text = user_input.lower().strip()

        # 1. Check if user asks for overall capabilities
        if "what can you do" in text or "what all can you do" in text:
            self.state["last_intent"] = "capability_list"
            return "I can do things like:\n" + "\n".join(
                f"- {c['desc']}" for c in self.capabilities.values()
            ) + "\n\nWant me to show you how to use one?"

        # 2. If user said "yeah/yes" after capability list
        if text in ["yeah", "yes", "sure", "ok", "okay"]:
            if self.state["last_intent"] == "capability_list":
                # pick one capability to demo (rotate or always start with shortcuts)
                cap_name, cap = next(iter(self.capabilities.items()))
                self.state["last_intent"] = "capability_demo"
                self.state["last_capability"] = cap_name
                return f"Cool, let’s start with {cap['desc']}\nExample: {cap['example']}\nWant me to explain another one?"

            elif self.state["last_intent"] == "capability_demo":
                # move to next capability
                caps = list(self.capabilities.items())
                last_index = [c[0] for c in caps].index(self.state["last_capability"])
                next_index = (last_index + 1) % len(caps)
                cap_name, cap = caps[next_index]
                self.state["last_capability"] = cap_name
                return f"Here’s another: {cap['desc']}\nExample: {cap['example']}\nWant me to keep going?"

        # 3. If user asks "how do I ..."
        match = re.search(r"how do i (.+)", text)
        if match:
            query = match.group(1)
            # simple keyword matching to find best capability
            for name, cap in self.capabilities.items():
                if name in query or any(word in query for word in cap["desc"].split()):
                    self.state["last_intent"] = "howto"
                    self.state["last_capability"] = name
                    return f"To {query}, {cap['example']}"
            return "Hmm, I’m not sure yet — but you can usually try: 'remind me to ...' or 'open ...'."

        # fallback → return unchanged
        return user_input
