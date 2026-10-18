from datetime import date, timedelta

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt

import config
from utils import banner_logic
from utils.embeds import BLUE, GOLD, GREY, make_embed
from utils.timeutil import banner_day_start, banner_today


def _stamp(d: date) -> str:
    """Moment the banner day begins, shown in each viewer's own timezone."""
    return format_dt(banner_day_start(d), "f")


def _banner_embed(title: str, day: int, banner: dict, extra: str | None = None) -> discord.Embed:
    color = GOLD if banner["type"] == "Limited" else BLUE
    embed = make_embed(title, color=color)
    embed.add_field(name="📅 Day", value=str(day))
    embed.add_field(name="🎴 Type", value=banner["type"])
    embed.add_field(name="Banner", value=f"**{banner['name']}**", inline=False)
    if extra:
        embed.set_footer(text=extra)
    return embed


def _ended_message() -> str:
    return (f"📅 The banner list only covers up to day {config.BANNER_LAST_DAY}, so I can't tell "
            "what is running now. An admin needs to update `data/banners.py`.")


class Banners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="banner", description="Show today's banner")
    async def banner(self, interaction: discord.Interaction):
        today = banner_today()
        day = banner_logic.day_for_date(today)
        if not banner_logic.in_schedule(day):
            await interaction.response.send_message(_ended_message(), ephemeral=True)
            return
        data = banner_logic.get_banner(day)
        if not data:
            embed = make_embed(f"📅 Day {day}", "No active banner today.", color=GREY)
        else:
            embed = _banner_embed(f"📅 Day {day}", day, data)
        embed.add_field(
            name="🔄 Next day starts",
            value=format_dt(banner_day_start(today + timedelta(days=1)), "R"),
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nextbanner", description="Show the next banner")
    async def nextbanner(self, interaction: discord.Interaction):
        today = banner_today()
        day = banner_logic.day_for_date(today)
        if not banner_logic.in_schedule(day):
            await interaction.response.send_message(_ended_message(), ephemeral=True)
            return
        found = banner_logic.find_banner(day, +1)
        if found is None:
            await interaction.response.send_message("No more banners in the list after today (it may need an update).", ephemeral=True)
            return
        starts = today + timedelta(days=found.offset)
        embed = _banner_embed("➡️ Next Banner", found.day, found.banner)
        embed.add_field(
            name="Starts",
            value=f"{_stamp(starts)} (in {found.offset} day{'s' if found.offset != 1 else ''})",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pastbanner", description="Show the previous banner")
    async def pastbanner(self, interaction: discord.Interaction):
        today = banner_today()
        day = banner_logic.day_for_date(today)
        if not banner_logic.in_schedule(day):
            await interaction.response.send_message(_ended_message(), ephemeral=True)
            return
        found = banner_logic.find_banner(day, -1)
        if found is None:
            await interaction.response.send_message("No previous banner found in the schedule.", ephemeral=True)
            return
        ended = today + timedelta(days=found.offset)
        ago = -found.offset
        embed = _banner_embed("⬅️ Previous Banner", found.day, found.banner)
        embed.add_field(
            name="Ended",
            value=f"{_stamp(ended)} ({ago} day{'s' if ago != 1 else ''} ago)",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Banners(bot))
