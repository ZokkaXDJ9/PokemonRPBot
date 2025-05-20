import os
import json
import asyncio
import re
import logging
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from openai import OpenAI

logger = logging.getLogger(__name__)

class SuggestCommand(commands.Cog):
    DATA_FOLDER = Path("Data/questgiver/")
    MAX_MESSAGE_LENGTH = 2000

    # how many tokens you actually want visible after stripping <think>…
    VISIBLE_TOKEN_GOAL = 1000
    # how many times we'll let it retry with +1000 tokens
    MAX_ATTEMPTS = 5

    PROMPT_TEMPLATE = """You are an assistant that creates quest ideas for a Pokémon role-playing game using Pokerole.
Generate a creative and engaging quest idea for a Pokémon Mystery Dungeon role-playing discord server using a modified version of Pokerole.
Include details such as setting, characters, objectives, and challenges, but let the Game Master handle the technical details.
We have a Citadel called "Citadel of Lost Legends" and the characters are in an adventuring guild that has the citadel as its HQ.
The characters are all Pokémon. There are no humans in this world. The quest givers can be anyone you want.

NPC/Character List:
Characters associated with this quest:
- {character_text}
The following characters can be used by anyone at any time. Be creative with it:
- You are welcome to add new Pokémon the team might have to rescue or that might be involved with the quest.
- There is NO Guildmaster/Guild Leader right now. Please also DO NOT make one up.

Reward Guidelines:
Choose ONE Threat for the quest only and CHOOSE rewards from the table. Don't just list all of them, but choose a reward that is given from the per character list and then something from the Shared loot pool. Always make new bullet points with "-" for each reward.

This one should ALWAYS be given out:
Low Threat: 150 Poke per hour, 3 exp per hour
Moderate Threat: 225 Poke per hour, 4 exp per hour
High Threat: 300 Poke per hour, 5 exp per hour

These ones are the tables for the threats:
Low Threat
Per Character
ONE of the following:
- 2 consumables items (up to Uncommon),
- 1 Permanent item (Common),
- 1 Rare Candy and 1 Empty Bottle,

Shared Loot Pool (Multiplied by the amount of players)
ONE of the following:
- TM of choice up to value 2000,
- Fixed TM up to value 3000,
- 1 Permanent item (up to Uncommon),
- 2 consumables items (up to Uncommon),
- 1 Consumable item (up to Rare),
- 1 Rare Candy and 1 Empty Bottle,
- 4 Malleable Material,
- 2 Energetic Material,
- 2 Shiny Material,
- 1 Sturdy Material,

Moderate Threat
Per Character
ONE of the following:
- 2 consumable items of any rarity (except reviver seeds/orbs),
- 1 Reviver Seed,
- 1 permanent item of choice (up to Uncommon),
- TM of choice up to value 2000,

Shared Loot Pool (Multiplied by the amount of players)
ONE of the following:
- 2 consumable items of any rarity (except reviver seeds/orbs),
- 1 Reviver Seed,
- 1 permanent item of choice (up to rare),
- TM of choice up to value 4000,
- Fixed TM of any value,
- 1 Magnificent Material,
- 3 Energetic Material,
- 3 Shiny Material,
- 1 Sturdy Material + 1 Energetic or Shiny Material,

High Threat
Per Character
ONE of the following:
- 2 consumables of any rarity (except reviver seeds/orbs) + 1 Reviver Seed,
- 1 permanent item of choice (up to rare),
- 1 TM of choice up to value 4000,

Shared Loot Pool (Multiplied by the amount of players)
ONE of the following:
- 4 consumable items of any rarity (except reviver seeds/orbs),
- 1 Reviver Orb + another consumable item of any rarity,
- 1 permanent item of choice of any rarity,
- TM of choice of any value,
- 2 Fixed TMs of any value,
- 2 Magnificent Materials,
- 3 Energetic and 3 Shiny Material,
- 3 Sturdy Material

Additional rewards/exp/money may be given, if action on the quest justifies, just try not to go below the value of those rewards.

Generate a quest idea based on these parameters.
"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="lm-studio"
        )
        self.model = "your-model-identifier"

    def load_user_characters(self, user_id: int) -> list[dict]:
        path = self.DATA_FOLDER / f"{user_id}.json"
        if not path.exists():
            return []
        return json.loads(path.read_text("utf-8")).get("quest_givers", [])

    async def questgiver_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        qgs = self.load_user_characters(interaction.user.id)
        return [
            app_commands.Choice(name=qg["name"], value=qg["name"])
            for qg in qgs
            if current.lower() in qg["name"].lower()
        ][:25]

    def build_prompt(self, character: dict) -> str:
        text = f"{character['name']} - {character['role']}: {character['description']}"
        return self.PROMPT_TEMPLATE.format(character_text=text)

    def _strip_thinking(self, text: str) -> str:
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    def generate_response(self, prompt: str) -> str:
        """
        Single-shot call: budget VISIBLE_TOKEN_GOAL + THINK_BUFFER tokens,
        then strip out any <think>…</think>.
        """
        THINK_BUFFER = self.VISIBLE_TOKEN_GOAL  # or whatever buffer size you’re comfortable with
        max_tokens = self.VISIBLE_TOKEN_GOAL + THINK_BUFFER

        messages = [
            {"role": "system", "content": "You are an assistant that creates quest ideas for a Pokémon role-playing game using Pokerole."},
            {"role": "user",   "content": prompt}
        ]

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            timeout=None     # disables timeouts entirely
        )

        raw = resp.choices[0].message.content.strip()
        return self._strip_thinking(raw)


    def _split_text(self, text: str, prefix_len: int) -> list[str]:
        parts, buf = [], ""
        for line in text.splitlines(keepends=True):
            if len(buf) + len(line) <= self.MAX_MESSAGE_LENGTH - prefix_len:
                buf += line
            else:
                parts.append(buf)
                buf = line
        if buf:
            parts.append(buf)
        return parts

    @app_commands.command(name="suggest", description="Suggest a quest idea for Pokerole using AI.")
    @app_commands.autocomplete(name=questgiver_autocomplete)
    async def suggest(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        user_id = interaction.user.id

        qgs = self.load_user_characters(user_id)
        sel = next((q for q in qgs if q["name"].lower() == name.lower()), None)
        if not sel:
            return await interaction.followup.send(
                "Quest giver not found. Please make sure you've set them up with `/setup_questgiver`."
            )

        prompt = self.build_prompt(sel)
        try:
            loop = asyncio.get_event_loop()
            quest = await loop.run_in_executor(None, self.generate_response, prompt)
        except Exception as e:
            logger.error("Error generating quest idea", exc_info=e)
            return await interaction.followup.send(
                "Sorry, I couldn't generate a quest idea at this time."
            )

        prefix = "Here's a quest idea:\n\n"
        chunks = self._split_text(quest, len(prefix))

        # Send the first chunk by editing the original deferred response
        try:
            await interaction.edit_original_response(content=f"{prefix}{chunks[0]}")
        except discord.errors.HTTPException as e:
            logger.error("Failed to send initial response", exc_info=e)

        # Send any remaining chunks as follow-ups
        for part in chunks[1:]:
            try:
                await interaction.followup.send(part.strip())
            except discord.errors.HTTPException as e:
                logger.error("Failed to send follow-up chunk", exc_info=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(SuggestCommand(bot))
