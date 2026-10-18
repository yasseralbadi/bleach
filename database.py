"""Async SQLite storage for the leaderboard and quiz history."""
import asyncio
from pathlib import Path
from typing import Any

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS leaderboard (
    user_id      INTEGER PRIMARY KEY,
    username     TEXT    NOT NULL,
    points       INTEGER NOT NULL DEFAULT 0,
    correct      INTEGER NOT NULL DEFAULT 0,
    wrong        INTEGER NOT NULL DEFAULT 0,
    daily_played TEXT    NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS quiz_history (
    user_id     INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, question_id)
);
"""


class Database:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self._conn: aiosqlite.Connection | None = None
        self._lock = asyncio.Lock()  # serialises writes so multi-step updates stay atomic

    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database is not connected")
        return self._conn

    # --- writes ---------------------------------------------------------------
    async def add_points(
        self,
        user_id: int,
        username: str,
        delta: int,
        *,
        correct: bool | None = None,
        question_id: int | None = None,
    ) -> None:
        """Add (or subtract) points. If `correct` is given the right/wrong counters
        are updated; if `question_id` is given it is recorded as answered."""
        async with self._lock:
            await self.conn.execute(
                """
                INSERT INTO leaderboard (user_id, username, points, correct, wrong)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    points   = points  + excluded.points,
                    correct  = correct + excluded.correct,
                    wrong    = wrong   + excluded.wrong
                """,
                (user_id, username, delta, int(correct is True), int(correct is False)),
            )
            if question_id is not None:
                await self.conn.execute(
                    "INSERT OR IGNORE INTO quiz_history (user_id, question_id) VALUES (?, ?)",
                    (user_id, question_id),
                )
            await self.conn.commit()

    async def set_points(self, user_id: int, username: str, points: int) -> None:
        async with self._lock:
            await self.conn.execute(
                """
                INSERT INTO leaderboard (user_id, username, points) VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET username = excluded.username,
                                                   points   = excluded.points
                """,
                (user_id, username, points),
            )
            await self.conn.commit()

    async def claim_daily(self, user_id: int, username: str, day: str) -> bool:
        """Atomically mark today's daily question as played.
        Returns False if the user already played on `day`."""
        async with self._lock:
            await self.conn.execute(
                """
                INSERT INTO leaderboard (user_id, username) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET username = excluded.username
                """,
                (user_id, username),
            )
            cur = await self.conn.execute(
                "UPDATE leaderboard SET daily_played = ? WHERE user_id = ? AND daily_played <> ?",
                (day, user_id, day),
            )
            await self.conn.commit()
            return cur.rowcount == 1

    async def reset(self) -> None:
        async with self._lock:
            await self.conn.execute("DELETE FROM leaderboard")
            await self.conn.execute("DELETE FROM quiz_history")
            await self.conn.commit()

    # --- reads ----------------------------------------------------------------
    async def get_top(self, limit: int = 10) -> list[dict[str, Any]]:
        cur = await self.conn.execute(
            """
            SELECT user_id, username, points, correct, wrong FROM leaderboard
            WHERE points <> 0 OR correct + wrong > 0
            ORDER BY points DESC, correct DESC, username COLLATE NOCASE
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in await cur.fetchall()]

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        cur = await self.conn.execute(
            "SELECT user_id, username, points, correct, wrong FROM leaderboard WHERE user_id = ?",
            (user_id,),
        )
        row = await cur.fetchone()
        if row is None:
            return None
        user = dict(row)
        cur = await self.conn.execute(
            "SELECT COUNT(*) + 1 FROM leaderboard WHERE points > ?", (user["points"],)
        )
        user["rank"] = (await cur.fetchone())[0]
        return user

    async def seen_questions(self, user_id: int) -> set[int]:
        cur = await self.conn.execute(
            "SELECT question_id FROM quiz_history WHERE user_id = ?", (user_id,)
        )
        return {r[0] for r in await cur.fetchall()}
