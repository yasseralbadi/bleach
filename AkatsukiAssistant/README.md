# AkatsukiAssistant

Discord clan assistant for the **Bleach Mobile 3D EU** clan Akatsuki.

## Commands

| Command | What it does |
| --- | --- |
| `/banner`, `/nextbanner`, `/pastbanner` | Today's / next / previous banner (community banner list, days 1-403) |
| `/events` | Clan War, Inner, Top Vs and Las Noches times (Istanbul, GMT and *your own* time) |
| `/leader` | Clan staff |
| `/rules` | Clan rules (fill in `RULES` in `data/clan.py`) |
| `/translate` | Translate text into 12 languages |
| `/quiz` | Random Bleach question, +5 / -3 pts, each question once per player |
| `/dailyquestion` | One question per day, +15 / -5 pts |
| `/leaderboard`, `/score` | Top 10 and personal stats |
| `/admin addpoints / removepoints / setpoints / resetleaderboard / announce` | Admin tools |
| `/help` | Lists the commands |

## Setup

1. Create an application at <https://discord.com/developers/applications>, add a **Bot** and copy its token.
   No privileged intents are required.
2. Invite it with the `bot` and `applications.commands` scopes and the permissions
   *View Channels*, *Send Messages*, *Embed Links*.
3. `cp .env.example .env` and fill in `DISCORD_TOKEN` (and `GUILD_ID` / `ADMIN_USER_IDS`).
4. Install and run (Python 3.11+):

```bash
pip install -r requirements.txt
python bot.py
```

Enable *Developer Mode* in Discord (Settings -> Advanced) to copy user, role and server IDs.

## Matching the game server's banner time

The banner day flips at `BANNER_RESET_TIME` on the `BANNER_TIMEZONE` clock (defaults: `Etc/GMT+4` i.e. UTC-4, 00:00 - measured from the live game).
To match your server:

1. In the game, note the exact moment a new banner / daily reset happens and what the in-game
   server clock says then.
2. Set `BANNER_TIMEZONE` to the server's zone (prefer `UTC` or a fixed offset like `Etc/GMT+5`,
   which means UTC-5) and `BANNER_RESET_TIME` to the flip time, e.g. `05:00`.
3. Check `/banner`: it shows when the next day starts in your own timezone. It must equal the
   moment the game actually switches. Also compare the banner name and day number with the game.

## Deploying

`render.yaml` / `Procfile` run it as a background **worker** (no web port). Set `DISCORD_TOKEN`
as an environment variable and keep `DATABASE_PATH` on a persistent disk, otherwise scores
are lost on every redeploy.

## Editing content

- Banners: `data/banners.py` (`SCHEDULE`: first day, last day, type, name). The list ends at day 403; after that the bot tells you it needs updating instead of guessing. Raise `BANNER_LAST_DAY` in `config.py` when you extend it.
- Staff, events, rules: `data/clan.py`
- Quiz / daily questions: `data/questions.py` (starter set - add your own)
- Points, timeouts, banner reference day: `config.py`

Admin permission is decided by Discord user ID / role ID / the Administrator permission,
never by display name.

## Tests

```bash
python -m unittest discover -s tests -t .
```
