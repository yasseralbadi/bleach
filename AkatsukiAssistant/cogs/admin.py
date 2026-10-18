import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.checks import is_admin
from utils.embeds import make_embed

log = logging.getLogger(__name__)


class ConfirmView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=30)
        self.owner_id = owner_id
        self.confirmed = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Not for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Yes, reset everything", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.defer()


@app_commands.guild_only()
class Admin(commands.GroupCog, group_name="admin", group_description="Clan admin tools"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        # Returning False raises CheckFailure, handled globally ("not authorized").
        return is_admin(interaction)

    async def _guard_member(self, interaction: discord.Interaction, member: discord.Member) -> bool:
        if member.bot:
            await interaction.response.send_message("Bots can't have points.", ephemeral=True)
            return False
        return True

    @app_commands.command(name="addpoints", description="Add points to a member")
    @app_commands.describe(member="Member", amount="Points to add")
    async def addpoints(
        self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1, 100000]
    ):
        if not await self._guard_member(interaction, member):
            return
        await self.bot.db.add_points(member.id, member.display_name, amount)
        total = (await self.bot.db.get_user(member.id))["points"]
        log.info("%s added %s points to %s", interaction.user, amount, member)
        await interaction.response.send_message(f"✅ Added **{amount}** pts to {member.mention} (now **{total}**).")

    @app_commands.command(name="removepoints", description="Remove points from a member")
    @app_commands.describe(member="Member", amount="Points to remove")
    async def removepoints(
        self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1, 100000]
    ):
        if not await self._guard_member(interaction, member):
            return
        await self.bot.db.add_points(member.id, member.display_name, -amount)
        total = (await self.bot.db.get_user(member.id))["points"]
        log.info("%s removed %s points from %s", interaction.user, amount, member)
        await interaction.response.send_message(f"✅ Removed **{amount}** pts from {member.mention} (now **{total}**).")

    @app_commands.command(name="setpoints", description="Set a member's points to an exact value")
    @app_commands.describe(member="Member", points="New total")
    async def setpoints(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        points: app_commands.Range[int, -1000000, 1000000],
    ):
        if not await self._guard_member(interaction, member):
            return
        await self.bot.db.set_points(member.id, member.display_name, points)
        log.info("%s set %s points to %s", interaction.user, member, points)
        await interaction.response.send_message(f"✅ {member.mention} now has **{points}** pts.")

    @app_commands.command(name="resetleaderboard", description="Wipe all scores and quiz history")
    async def resetleaderboard(self, interaction: discord.Interaction):
        view = ConfirmView(interaction.user.id)
        await interaction.response.send_message(
            "⚠️ This deletes **all** scores and quiz history and cannot be undone. Continue?",
            view=view,
            ephemeral=True,
        )
        await view.wait()
        if view.confirmed:
            await self.bot.db.reset()
            log.warning("%s reset the leaderboard", interaction.user)
            await interaction.edit_original_response(content="✅ Leaderboard reset.", view=None)
        else:
            await interaction.edit_original_response(content="Cancelled.", view=None)

    @app_commands.command(name="announce", description="Post an announcement embed in a channel")
    @app_commands.describe(
        message="Announcement text (write \\n for a new line)",
        title="Embed title",
        channel="Channel to post in (default: this one)",
        ping="Role to ping",
    )
    async def announce(
        self,
        interaction: discord.Interaction,
        message: app_commands.Range[str, 1, 4000],
        title: app_commands.Range[str, 1, 200] = "📢 Announcement",
        channel: Optional[discord.TextChannel] = None,
        ping: Optional[discord.Role] = None,
    ):
        target = channel or interaction.channel
        embed = make_embed(title, message.replace("\\n", "\n"))
        embed.set_footer(text=f"— {interaction.user.display_name}")
        mentions = discord.AllowedMentions(roles=[ping]) if ping else discord.AllowedMentions.none()
        try:
            await target.send(content=ping.mention if ping else None, embed=embed, allowed_mentions=mentions)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ I don't have permission to post in {target.mention}. "
                "I need **View Channel**, **Send Messages** and **Embed Links**.",
                ephemeral=True,
            )
            return
        log.info("%s announced in %s", interaction.user, target)
        await interaction.response.send_message(f"✅ Announcement sent to {target.mention}.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
