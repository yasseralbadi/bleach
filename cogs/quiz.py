import random

import discord
from discord import app_commands
from discord.ext import commands

import config
from data.questions import DAILY_QUESTIONS, QUIZ_QUESTIONS
from utils.embeds import GREEN, GREY, RED, make_embed, format_points
from utils.timeutil import local_today


class AnswerButton(discord.ui.Button):
    def __init__(self, index: int, label: str):
        super().__init__(label=label[:80], style=discord.ButtonStyle.secondary)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        await self.view.submit(interaction, self.index)


class AnswerView(discord.ui.View):
    """One question, one attempt, only the asker can answer."""

    def __init__(self, *, owner_id, options, correct_index, resolver, base_embed, timeout):
        super().__init__(timeout=timeout)
        self.owner_id = owner_id
        self.correct_index = correct_index
        self.resolver = resolver          # async (correct: bool) -> points delta
        self.base_embed = base_embed
        self.answered = False
        self.message = None
        for i, text in enumerate(options):
            self.add_item(AnswerButton(i, text))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "This question belongs to someone else — use the command to get your own.", ephemeral=True
            )
            return False
        return True

    async def submit(self, interaction: discord.Interaction, index: int):
        if self.answered:
            await interaction.response.defer()
            return
        self.answered = True
        self.stop()

        correct = index == self.correct_index
        for item in self.children:
            item.disabled = True
            if item.index == self.correct_index:
                item.style = discord.ButtonStyle.success
            elif item.index == index:
                item.style = discord.ButtonStyle.danger

        delta = await self.resolver(correct)
        embed = self.base_embed.copy()
        embed.colour = GREEN if correct else RED
        embed.add_field(
            name="✅ Correct!" if correct else "❌ Wrong!",
            value=f"{format_points(delta)} pts",
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        if self.answered:
            return
        for item in self.children:
            item.disabled = True
        if self.message is not None:
            embed = self.base_embed.copy()
            embed.colour = GREY
            embed.add_field(name="⏰ Time's up", value="No points awarded.")
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.HTTPException:
                pass


def _shuffled(question: dict) -> tuple[list[str], int]:
    order = list(range(len(question["options"])))
    random.shuffle(order)
    return [question["options"][i] for i in order], order.index(question["answer"])


class Quiz(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _ask(self, interaction, title, question, resolver, timeout):
        options, correct_index = _shuffled(question)
        embed = make_embed(title, f"**{question['question']}**")
        view = AnswerView(
            owner_id=interaction.user.id,
            options=options,
            correct_index=correct_index,
            resolver=resolver,
            base_embed=embed,
            timeout=timeout,
        )
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @app_commands.command(
        name="quiz",
        description=f"Answer a random Bleach question ({format_points(config.QUIZ_CORRECT)} / {config.QUIZ_WRONG} pts)",
    )
    @app_commands.checks.cooldown(1, 5.0)
    async def quiz(self, interaction: discord.Interaction):
        user = interaction.user
        seen = await self.bot.db.seen_questions(user.id)
        pool = [q for q in QUIZ_QUESTIONS if q["id"] not in seen]
        if not pool:
            await interaction.response.send_message(
                "🎉 You've answered every quiz question! New ones are coming soon.", ephemeral=True
            )
            return
        question = random.choice(pool)

        async def resolve(correct: bool) -> int:
            delta = config.QUIZ_CORRECT if correct else config.QUIZ_WRONG
            await self.bot.db.add_points(
                user.id, user.display_name, delta, correct=correct, question_id=question["id"]
            )
            return delta

        await self._ask(interaction, "🧠 Bleach Quiz", question, resolve, config.QUIZ_TIMEOUT)

    @app_commands.command(
        name="dailyquestion",
        description=f"Today's question, once per day ({format_points(config.DAILY_CORRECT)} / {config.DAILY_WRONG} pts)",
    )
    async def dailyquestion(self, interaction: discord.Interaction):
        if not DAILY_QUESTIONS:
            await interaction.response.send_message("No daily questions are available yet.", ephemeral=True)
            return
        user = interaction.user
        today = local_today()
        if not await self.bot.db.claim_daily(user.id, user.display_name, today.isoformat()):
            await interaction.response.send_message(
                "📆 You've already played today's question. Come back tomorrow!", ephemeral=True
            )
            return
        question = DAILY_QUESTIONS[today.toordinal() % len(DAILY_QUESTIONS)]

        async def resolve(correct: bool) -> int:
            delta = config.DAILY_CORRECT if correct else config.DAILY_WRONG
            await self.bot.db.add_points(user.id, user.display_name, delta, correct=correct)
            return delta

        await self._ask(interaction, "📆 Daily Question", question, resolve, config.DAILY_TIMEOUT)


async def setup(bot: commands.Bot):
    await bot.add_cog(Quiz(bot))
