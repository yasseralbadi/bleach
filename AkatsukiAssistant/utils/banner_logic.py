"""Banner-schedule maths. Pure functions, no Discord imports."""
from datetime import date
from typing import NamedTuple

import config
from data.banners import BANNERS


class Found(NamedTuple):
    day: int      # day number in the banner list
    offset: int   # days from the starting day (negative = in the past)
    banner: dict


def day_for_date(d: date) -> int:
    """Banner-list day for a calendar date (may fall outside 1..BANNER_LAST_DAY)."""
    return config.BANNER_REFERENCE_DAY + (d - config.BANNER_REFERENCE_DATE).days


def in_schedule(day: int) -> bool:
    return 1 <= day <= config.BANNER_LAST_DAY


def get_banner(day: int) -> dict | None:
    return BANNERS.get(day)


def find_banner(day: int, direction: int) -> Found | None:
    """Nearest banner after (direction=+1) or before (direction=-1) `day` whose name
    differs from the banner running on `day`. The list is not wrapped: returns None
    when the list has nothing further in that direction."""
    current = BANNERS.get(day)
    check = day + direction
    while in_schedule(check):
        banner = BANNERS.get(check)
        if banner and (current is None or banner["name"] != current["name"]):
            return Found(check, check - day, banner)
        check += direction
    return None
