import discord
from discord import app_commands
from discord.ext import commands
import math
from typing import Literal

class CritCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="crit",
        description="Calculate the critical strike damage of a move."
    )
    async def crit(
        self,
        interaction: discord.Interaction,
        damage: int,
        stab: Literal["yes", "no"] = "no",
        bonus: int = 0,
        item_bonus: int = 0,
        effective: Literal[
            "neutral",
            "super_effective",
            "double_effective",
            "not_effective",
            "double_not_effective",
        ] = "neutral",
    ):
        # Base damage calculation
        total_damage = damage

        # Apply STAB if applicable
        if stab == "yes":
            total_damage += 1  # Add 1 for STAB

        # Apply item bonus
        total_damage += item_bonus  # Add item bonus

        # Apply generic bonus
        total_damage += bonus  # Add any additional bonuses

        # Apply critical multiplier
        total_damage = math.ceil(total_damage * 1.5)  # Multiply by 1.5 and round up

        # Apply effectiveness modifier AFTER critical multiplier
        if effective == "super_effective":
            total_damage += 1  # Add 1 for super effective
        elif effective == "double_effective":
            total_damage += 2  # Add 2 for double effective
        elif effective == "not_effective":
            total_damage -= 1  # Subtract 1 for not very effective
        elif effective == "double_not_effective":
            total_damage -= 2  # Subtract 2 for double not effective
        # Neutral effectiveness doesn't change damage

        # Ensure that damage doesn't drop below zero
        total_damage = max(total_damage, 0)

        # Respond with the final damage
        await interaction.response.send_message(f"Base damage: {total_damage}")

async def setup(bot):
    await bot.add_cog(CritCommand(bot))
