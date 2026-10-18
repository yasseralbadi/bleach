"""Offline tests (no Discord connection needed).

Run from the project root:  python -m unittest discover -s tests -t .
"""
import asyncio
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import config
from bot import EXTENSIONS, AkatsukiBot
from cogs.info import build_events_embed
from cogs.quiz import AnswerView
from data.banners import BANNERS, SCHEDULE
from data.clan import EVENT_TZ
from data.questions import DAILY_QUESTIONS, QUIZ_QUESTIONS
from database import Database
from utils import banner_logic
from utils.timeutil import banner_day_start, banner_today


class BannerTests(unittest.TestCase):
    def test_reference_date_is_reference_day(self):
        self.assertEqual(banner_logic.day_for_date(config.BANNER_REFERENCE_DATE), config.BANNER_REFERENCE_DAY)

    def test_days_advance_with_dates_and_do_not_wrap(self):
        ref = config.BANNER_REFERENCE_DATE
        last_offset = config.BANNER_LAST_DAY - config.BANNER_REFERENCE_DAY
        self.assertEqual(banner_logic.day_for_date(ref + timedelta(days=last_offset)), config.BANNER_LAST_DAY)
        beyond = banner_logic.day_for_date(ref + timedelta(days=last_offset + 1))
        self.assertEqual(beyond, config.BANNER_LAST_DAY + 1)
        self.assertFalse(banner_logic.in_schedule(beyond))
        self.assertIsNone(banner_logic.get_banner(beyond))
        self.assertIsNone(banner_logic.find_banner(config.BANNER_LAST_DAY, +1))

    def test_schedule_pattern(self):
        self.assertEqual(len(BANNERS), sum(last - first + 1 for first, last, _, _ in SCHEDULE))
        self.assertTrue(all(1 <= d <= config.BANNER_LAST_DAY for d in BANNERS))
        self.assertEqual(BANNERS[4], {"type": "Limited", "name": "Ulquiorra"})
        # every banner runs exactly 4 days, runs never overlap
        self.assertTrue(all(last - first == 3 for first, last, _, _ in SCHEDULE))
        days = [d for first, last, _, _ in SCHEDULE for d in range(first, last + 1)]
        self.assertEqual(len(days), len(set(days)))
        # the Limited rotation repeats every 198 days (the list itself says "the banner recycles")
        for d, b in BANNERS.items():
            if b["type"] == "Limited" and d + 198 <= config.BANNER_LAST_DAY:
                self.assertEqual(BANNERS.get(d + 198), b, f"day {d}")

    def test_next_and_previous_for_every_day(self):
        for day in range(1, config.BANNER_LAST_DAY + 1):
            current = BANNERS.get(day)
            for direction in (1, -1):
                found = banner_logic.find_banner(day, direction)
                if found is None:
                    continue
                self.assertEqual(day + found.offset, found.day)
                self.assertEqual(found.offset > 0, direction > 0)
                self.assertEqual(BANNERS[found.day], found.banner)
                if current:
                    self.assertNotEqual(found.banner["name"], current["name"])
        self.assertIsNotNone(banner_logic.find_banner(257, +1))
        self.assertIsNotNone(banner_logic.find_banner(257, -1))


class BannerResetTests(unittest.TestCase):
    def test_day_flips_at_reset_time(self):
        from datetime import time, timezone
        from unittest.mock import patch
        tz = timezone.utc
        with patch.object(config, "BANNER_TIMEZONE", tz), patch.object(config, "BANNER_RESET_TIME", time(5, 0)):
            before = datetime(2026, 10, 18, 4, 59, tzinfo=tz)
            after = datetime(2026, 10, 18, 5, 0, tzinfo=tz)
            self.assertEqual(banner_today(before).isoformat(), "2026-10-17")
            self.assertEqual(banner_today(after).isoformat(), "2026-10-18")
            self.assertEqual(banner_day_start(after.date()), after)

    def test_converts_between_timezones(self):
        from datetime import time, timezone
        from unittest.mock import patch
        with patch.object(config, "BANNER_TIMEZONE", timezone(timedelta(hours=-5))), \
             patch.object(config, "BANNER_RESET_TIME", time(0, 0)):
            now = datetime(2026, 10, 18, 4, 0, tzinfo=timezone.utc)   # 23:00 the day before at UTC-5
            self.assertEqual(banner_today(now).isoformat(), "2026-10-17")


class LiveCalibrationTests(unittest.TestCase):
    """Pinned to what the real game showed on 18 Oct 2026."""

    def test_calibration_matches_live_game(self):
        from datetime import date
        day = banner_logic.day_for_date(date(2026, 10, 18))
        self.assertEqual(day, 257)
        self.assertEqual(BANNERS[day]["name"], "Toshiro (RF)")
        self.assertEqual(banner_logic.day_for_date(date(2026, 10, 21)), 260)        # last Toshiro day
        self.assertNotIn(banner_logic.day_for_date(date(2026, 10, 22)), BANNERS)    # 3-day gap
        self.assertNotIn(banner_logic.day_for_date(date(2026, 10, 24)), BANNERS)
        self.assertEqual(BANNERS[banner_logic.day_for_date(date(2026, 10, 25))],
                         {"type": "Rate-Up", "name": "Grimmjow & Tosen"})
        self.assertEqual(BANNERS[256]["name"], "Nel Tu & Soi Fon")                  # banner before Toshiro

    def test_server_day_flips_at_midnight_utc_minus_4(self):
        from datetime import timezone
        self.assertEqual(banner_today(datetime(2026, 10, 22, 3, 59, tzinfo=timezone.utc)).isoformat(), "2026-10-21")
        self.assertEqual(banner_today(datetime(2026, 10, 22, 4, 0, tzinfo=timezone.utc)).isoformat(), "2026-10-22")


class QuestionTests(unittest.TestCase):
    def test_question_banks_are_valid(self):
        for bank in (QUIZ_QUESTIONS, DAILY_QUESTIONS):
            ids = [q["id"] for q in bank]
            self.assertEqual(len(ids), len(set(ids)), "duplicate ids")
            for q in bank:
                self.assertTrue(2 <= len(q["options"]) <= 5)
                self.assertTrue(0 <= q["answer"] < len(q["options"]))
                self.assertTrue(all(len(o) <= 80 for o in q["options"]))
                self.assertEqual(len(q["options"]), len(set(q["options"])))


class DatabaseTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "sub" / "t.db")
        await self.db.connect()

    async def asyncTearDown(self):
        await self.db.close()
        self.tmp.cleanup()

    async def test_points_and_ranking(self):
        await self.db.add_points(1, "a", 10, correct=True, question_id=1)
        await self.db.add_points(2, "b", 20)
        await self.db.add_points(1, "a", -3, correct=False, question_id=2)
        top = await self.db.get_top()
        self.assertEqual([p["user_id"] for p in top], [2, 1])
        user = await self.db.get_user(1)
        self.assertEqual((user["points"], user["correct"], user["wrong"], user["rank"]), (7, 1, 1, 2))
        self.assertEqual(await self.db.seen_questions(1), {1, 2})

    async def test_set_and_reset(self):
        await self.db.set_points(5, "x", 99)
        self.assertEqual((await self.db.get_user(5))["points"], 99)
        await self.db.add_points(5, "x", 1, question_id=3)
        await self.db.reset()
        self.assertEqual(await self.db.get_top(), [])
        self.assertEqual(await self.db.seen_questions(5), set())

    async def test_daily_claim_is_atomic(self):
        results = await asyncio.gather(*[self.db.claim_daily(7, "u", "2026-10-18") for _ in range(10)])
        self.assertEqual(results.count(True), 1)
        self.assertTrue(await self.db.claim_daily(7, "u", "2026-10-19"))

    async def test_user_without_activity_not_on_board(self):
        await self.db.claim_daily(9, "lurker", "2026-10-18")
        self.assertEqual(await self.db.get_top(), [])


class BotTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_cogs_load_and_register_commands(self):
        bot = AkatsukiBot()
        try:
            for ext in EXTENSIONS:
                await bot.load_extension(ext)
            names = {c.name for c in bot.tree.get_commands()}
            expected = {"help", "leader", "rules", "events", "banner", "nextbanner", "pastbanner",
                        "translate", "leaderboard", "score", "quiz", "dailyquestion", "admin"}
            self.assertEqual(names, expected)
            admin = bot.tree.get_command("admin")
            self.assertEqual({c.name for c in admin.commands},
                             {"addpoints", "removepoints", "setpoints", "resetleaderboard", "announce"})
        finally:
            await bot.close()

    def test_events_embed(self):
        embed = build_events_embed(datetime(2026, 10, 17, 12, 0, tzinfo=EVENT_TZ))  # a Saturday, after 10:00
        self.assertEqual([f.name for f in embed.fields], ["⚔️ Clan War", "🔮 Inner", "🏆 Top Vs", "🏰 Las Noches"])
        self.assertTrue(all(len(f.value) <= 1024 for f in embed.fields))
        self.assertIn("12:30–13:00", embed.fields[1].value)
        self.assertIn("09:30–10:00 GMT", embed.fields[1].value)


class AnswerViewTests(unittest.IsolatedAsyncioTestCase):
    def _view(self, resolver):
        import discord
        return AnswerView(owner_id=1, options=["a", "b", "c"], correct_index=1, resolver=resolver,
                          base_embed=discord.Embed(title="t"), timeout=5)

    async def test_correct_answer_once_only(self):
        resolver = AsyncMock(return_value=5)
        view = self._view(resolver)
        interaction = MagicMock()
        interaction.response.edit_message = AsyncMock()
        interaction.response.defer = AsyncMock()
        await view.submit(interaction, 1)
        await view.submit(interaction, 0)          # second click must be ignored
        resolver.assert_awaited_once_with(True)
        self.assertTrue(all(item.disabled for item in view.children))
        interaction.response.edit_message.assert_awaited_once()

    async def test_only_owner_can_answer(self):
        view = self._view(AsyncMock())
        interaction = MagicMock()
        interaction.user.id = 999
        interaction.response.send_message = AsyncMock()
        self.assertFalse(await view.interaction_check(interaction))
        interaction.user.id = 1
        self.assertTrue(await view.interaction_check(interaction))


if __name__ == "__main__":
    unittest.main()
