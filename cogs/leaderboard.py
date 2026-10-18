from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import escape_markdown

from utils.embeds import make_embed

MEDALS = ["🥇", "🥈", "🥉"]


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show the top 10 players")
    async def leaderboard(self, interaction: discord.Interaction):
        ranking = await self.bot.db.get_top(10)
        if not ranking:
            await interaction.response.send_message("🏆 The leaderboard is empty. Try `/quiz`!")
            return
        lines = []
        for i, p in enumerate(ranking):
            medal = MEDALS[i] if i < 3 else f"**{i + 1}.**"
            lines.append(f"{medal} {escape_markdown(p['username'])} • {p['points']} pts")
        await interaction.response.send_message(
            embed=make_embed("🏆 AKATSUKI LEADERBOARD", "\n".join(lines))
        )

    @app_commands.command(name="score", description="Show your score (or another member's)")
    @app_commands.describe(member="Member to look up (default: you)")
    async def score(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        target = member or interaction.user
        user = await self.bot.db.get_user(target.id)
        if user is None:
            await interaction.response.send_message(f"{target.display_name} has no score yet.", ephemeral=True)
            return
        embed = make_embed(f"📊 {target.display_name}")
        embed.add_field(name="Points", value=str(user["points"]))
        embed.add_field(name="Rank", value=f"#{user['rank']}")
        embed.add_field(name="Answers", value=f"✅ {user['correct']}  ❌ {user['wrong']}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))
