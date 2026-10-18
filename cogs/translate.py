import asyncio
import logging

import discord
from deep_translator import GoogleTranslator
from discord import app_commands
from discord.ext import commands

from utils.embeds import make_embed

log = logging.getLogger(__name__)

LANGUAGES = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "zh": "Chinese (Simplified)",
}
_GOOGLE_CODES = {"zh": "zh-CN"}


def _translate(text: str, code: str) -> str | None:
    return GoogleTranslator(source="auto", target=_GOOGLE_CODES.get(code, code)).translate(text)


class Translate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="translate", description="Translate text into another language")
    @app_commands.describe(language="Target language", text="The text to translate")
    @app_commands.choices(
        language=[app_commands.Choice(name=name, value=code) for code, name in LANGUAGES.items()]
    )
    @app_commands.checks.cooldown(1, 3.0)
    async def translate(
        self,
        interaction: discord.Interaction,
        language: app_commands.Choice[str],
        text: app_commands.Range[str, 1, 1500],
    ):
        await interaction.response.defer()
        try:
            # deep-translator is blocking; run it off the event loop.
            result = await asyncio.to_thread(_translate, text, language.value)
        except Exception:
            log.exception("Translation failed")
            result = None

        if not result:
            await interaction.edit_original_response(content="❌ Translation failed, please try again later.")
            return

        embed = make_embed(f"🌍 {language.name}", result)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.edit_original_response(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Translate(bot))
