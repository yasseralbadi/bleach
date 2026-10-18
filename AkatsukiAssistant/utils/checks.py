import discord

import config


def is_admin(interaction: discord.Interaction) -> bool:
    """Admin = listed user ID, member of a listed role, or server administrator.

    Authorisation is based on immutable Discord IDs / permissions, never on
    display names (which anyone can change to impersonate an admin)."""
    user = interaction.user
    if user.id in config.ADMIN_USER_IDS:
        return True
    if isinstance(user, discord.Member):
        if user.guild_permissions.administrator:
            return True
        if any(role.id in config.ADMIN_ROLE_IDS for role in user.roles):
            return True
    return False
