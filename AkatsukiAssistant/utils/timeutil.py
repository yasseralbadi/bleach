from datetime import date, datetime, timedelta

import config


def local_now() -> datetime:
    return datetime.now(config.TIMEZONE)


def local_today() -> date:
    return local_now().date()


def _reset_delta() -> timedelta:
    r = config.BANNER_RESET_TIME
    return timedelta(hours=r.hour, minutes=r.minute)


def banner_today(now: datetime | None = None) -> date:
    """The game server's current banner date (the day flips at BANNER_RESET_TIME)."""
    now = (now or datetime.now(config.BANNER_TIMEZONE)).astimezone(config.BANNER_TIMEZONE)
    return (now - _reset_delta()).date()


def banner_day_start(d: date) -> datetime:
    """The exact moment banner date `d` begins on the game server."""
    return datetime.combine(d, config.BANNER_RESET_TIME, tzinfo=config.BANNER_TIMEZONE)
