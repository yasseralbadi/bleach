"""AkatsukiAssistant - Discord clan bot for Bleach Mobile 3D (EU)."""
import os
import logging
import sys
from flask import Flask
from threading import Thread

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import Database

# ----------------------------------------------------
# [خادم ويب وهمي مدمج لتخطي فحص المنافذ في Render مجاناً]
# ----------------------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "✅ Akatsuki Assistant Web Service is Running!"

def run_web():
    # استخدام المنفذ 8080 المتوافق تماماً مع تحديثات الاستضافة الحالية
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run_web).start()

# تشغيل خادم الويب فوراً قبل إقلاع البوت
keep_alive()
# ----------------------------------------------------

log = logging.getLogger("akatsuki")

EXTENSIONS = [
    "cogs.info",
    "cogs.banners",
    "cogs.translate",
    "cogs.leaderboard",
    "cogs.quiz",
    "cogs.admin",
]


async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        message = f"⏳ Slow down — try again in {error.retry_after:.0f}s."
    elif isinstance(error, app_commands.CheckFailure):
        message = "❌ You are not authorized."
    else:
        log.error("Unhandled error in /%s", interaction.command.qualified_name if interaction.command else "?",
                  exc_info=error)
        message = "⚠️ Something went wrong. Please try again later."

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
        pass


class AkatsukiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=discord.Intents.default(),           # no privileged intents needed
            allowed_mentions=discord.AllowedMentions.none(),  # user text can never ping anyone
            help_command=None,
        )
        self.db = Database(config.DATABASE_PATH)
        self.tree.error(on_app_command_error)

    async def setup_hook(self):
        await self.db.connect()
        for ext in EXTENSIONS:
            await self.load_extension(ext)

        if config.GUILD_ID:
            guild = discord.Object(id=config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self):
        log.info("✅ Akatsuki Assistant started as %s (%d servers)", self.user, len(self.guilds))

    async def close(self):
        await self.db.close()
        await super().close()


def main():
    if not config.DISCORD_TOKEN:
        sys.exit("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    AkatsukiBot().run(config.DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
