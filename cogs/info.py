from datetime import datetime, time, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt

from data.clan import CLAN_WAR, EVENT_TZ, EVENTS, RULES, STAFF
from utils.checks import is_admin
from utils.embeds import make_embed


def _slot_line(day, start: str, end: str | None) -> str:
    s = datetime.combine(day, time.fromisoformat(start), tzinfo=EVENT_TZ)
    e = datetime.combine(day, time.fromisoformat(end), tzinfo=EVENT_TZ) if end else None

    istanbul = f"{start}–{end}" if e else start
    gmt = s.astimezone(timezone.utc).strftime("%H:%M")
    local = format_dt(s, "t")
    if e:
        gmt += "–" + e.astimezone(timezone.utc).strftime("%H:%M")
        local += "–" + format_dt(e, "t")
    return f"• **{istanbul}** Istanbul · {gmt} GMT · {local} *(your time)*"


def _next_clan_war(now: datetime) -> datetime:
    at = time.fromisoformat(CLAN_WAR["time"])
    ist = now.astimezone(EVENT_TZ)
    days = (CLAN_WAR["weekday"] - ist.weekday()) % 7
    when = datetime.combine(ist.date() + timedelta(days=days), at, tzinfo=EVENT_TZ)
    if when <= ist:
        when += timedelta(days=7)
    return when


def build_events_embed(now: datetime | None = None) -> discord.Embed:
    now = (now or datetime.now(EVENT_TZ)).astimezone(EVENT_TZ)
    embed = make_embed("📅 Clan Events Schedule")

    war = _next_clan_war(now)
    embed.add_field(
        name="⚔️ Clan War",
        value=(
            f"Every Saturday **{CLAN_WAR['time']}** Istanbul · "
            f"{war.astimezone(timezone.utc).strftime('%H:%M')} GMT\n"
            f"Next: {format_dt(war, 'F')} ({format_dt(war, 'R')})"
        ),
        inline=False,
    )
    for event in EVENTS:
        lines = [_slot_line(now.date(), start, end) for start, end in event["slots"]]
        embed.add_field(name=f"{event['emoji']} {event['name']}", value="\n".join(lines), inline=False)
    embed.set_footer(text="Daily events repeat every day. 'Your time' adapts to your own timezone.")
    return embed


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="List all commands")
    async def help(self, interaction: discord.Interaction):
        show_admin = is_admin(interaction)
        lines = []
        for cmd in sorted(self.bot.tree.get_commands(), key=lambda c: c.name):
            if isinstance(cmd, app_commands.Group):
                if cmd.name == "admin" and not show_admin:
                    continue
                for sub in sorted(cmd.commands, key=lambda c: c.name):
                    lines.append(f"`/{cmd.name} {sub.name}` — {sub.description}")
            elif isinstance(cmd, app_commands.Command):
                lines.append(f"`/{cmd.name}` — {cmd.description}")
        embed = make_embed("🤖 Akatsuki Assistant", "\n".join(lines))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="leader", description="Show the clan staff")
    async def leader(self, interaction: discord.Interaction):
        embed = make_embed("👑 Akatsuki Clan Staff")
        for role, names in STAFF.items():
            embed.add_field(name=role, value="\n".join(f"• {n}" for n in names), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rules", description="Show the clan rules")
    async def rules(self, interaction: discord.Interaction):
        if not RULES:
            await interaction.response.send_message(
                "📜 The clan rules haven't been set yet. (Admins: add them to `RULES` in `data/clan.py`.)",
                ephemeral=True,
            )
            return
        text = "\n".join(f"**{i}.** {rule}" for i, rule in enumerate(RULES, 1))
        await interaction.response.send_message(embed=make_embed("📜 Clan Rules", text))

    @app_commands.command(name="events", description="Show the clan events schedule")
    async def events(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=build_events_embed())


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
