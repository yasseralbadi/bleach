"""Central configuration for AkatsukiAssistant (Discord edition).

Secrets and deployment-specific values come from environment variables
(or a local .env file, see .env.example). Everything else lives here.
"""
import os
from datetime import date, time
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def _id_set(name: str) -> set[int]:
    raw = os.getenv(name, "")
    try:
        return {int(p) for p in raw.replace(";", ",").split(",") if p.strip()}
    except ValueError:
        raise RuntimeError(f"{name} must be a comma-separated list of numeric IDs") from None


def _clock(name: str, default: str) -> time:
    raw = (os.getenv(name) or default).strip()
    try:
        return time.fromisoformat(raw)
    except ValueError:
        raise RuntimeError(f"{name} must look like HH:MM, e.g. 05:00") from None


def _optional_int(name: str) -> int | None:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(f"{name} must be a number") from None


# --- Deployment -------------------------------------------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Optional: sync slash commands to one server only (appears instantly).
# Leave empty to register them globally (can take up to an hour to show up).
GUILD_ID = _optional_int("GUILD_ID")

# Who may use /admin commands. Server administrators always can.
ADMIN_USER_IDS = _id_set("ADMIN_USER_IDS")
ADMIN_ROLE_IDS = _id_set("ADMIN_ROLE_IDS")

# Put this on a persistent disk in production, otherwise scores reset on redeploy.
DATABASE_PATH = Path(os.getenv("DATABASE_PATH") or BASE_DIR / "akatsuki.db")

# Timezone used for the /dailyquestion day (midnight to midnight).
TIMEZONE = ZoneInfo(os.getenv("BOT_TIMEZONE") or "Europe/Istanbul")

# When does a new banner day start on YOUR GAME SERVER?
# BANNER_TIMEZONE is the server's clock, BANNER_RESET_TIME the moment the day flips there.
# Tip: prefer "UTC" or a fixed offset such as "Etc/GMT+5" (= UTC-5, sign is inverted) over
# zones like "America/New_York", because game servers usually do not follow daylight saving.
BANNER_TIMEZONE = ZoneInfo(os.getenv("BANNER_TIMEZONE") or "Etc/GMT+4")  # = UTC-4
BANNER_RESET_TIME = _clock("BANNER_RESET_TIME", "00:00")

# --- Banner schedule --------------------------------------------------------
# The list in data/banners.py covers days 1..BANNER_LAST_DAY. It is NOT assumed to repeat:
# past this day the bot says the list needs an update instead of guessing.
BANNER_LAST_DAY = 403
# Calibrated from the live game: 18 Oct 2026 (server date) = list day 257
# (Toshiro Hitsugaya limited, 2nd day of its run, preceded by Nel Tu & Soi Fon).
BANNER_REFERENCE_DAY = 257
BANNER_REFERENCE_DATE = date(2026, 10, 18)

# --- Scoring ----------------------------------------------------------------
QUIZ_CORRECT = 5
QUIZ_WRONG = -3
DAILY_CORRECT = 15
DAILY_WRONG = -5

QUIZ_TIMEOUT = 45      # seconds to answer /quiz
DAILY_TIMEOUT = 60     # seconds to answer /dailyquestion
