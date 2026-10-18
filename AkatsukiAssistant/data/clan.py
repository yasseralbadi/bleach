"""Static clan information. Edit this file to update staff, events or rules."""
from zoneinfo import ZoneInfo

# All event times below are written in Istanbul time (GMT+3).
EVENT_TZ = ZoneInfo("Europe/Istanbul")

STAFF = {
    "👑 Leader": ["Klaus"],
    "⚔️ Vice Leaders": ["Asta", "YurtSever"],
    "🛡️ Admins": ["Baba Yaga", "Jaco Tenma", "Mutoh"],
}

# Weekly Clan War: weekday 0=Monday ... 5=Saturday
CLAN_WAR = {"weekday": 5, "time": "10:00"}

# Daily events. Each slot is (start, end); use end=None for a single point in time.
EVENTS = [
    {"emoji": "🔮", "name": "Inner", "slots": [("12:30", "13:00"), ("20:30", "21:00")]},
    {"emoji": "🏆", "name": "Top Vs", "slots": [("12:00", "14:00"), ("20:00", "22:00")]},
    {
        "emoji": "🏰",
        "name": "Las Noches",
        "slots": [("14:00", None), ("16:00", None), ("18:00", None), ("22:00", None), ("23:00", None)],
    },
]

# Clan rules shown by /rules. Add one string per rule, e.g.:
# RULES = ["Be respectful to every member.", "Take part in Clan War."]
RULES: list[str] = []
