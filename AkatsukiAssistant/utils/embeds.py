import discord

RED = discord.Color.from_rgb(179, 0, 0)  # Akatsuki red
GOLD = discord.Color.gold()
BLUE = discord.Color.blue()
GREEN = discord.Color.green()
GREY = discord.Color.greyple()


def make_embed(title: str, description: str | None = None, *, color: discord.Color = RED) -> discord.Embed:
    return discord.Embed(title=title, description=description, color=color)


def format_points(points: int) -> str:
    return f"+{points}" if points > 0 else str(points)
