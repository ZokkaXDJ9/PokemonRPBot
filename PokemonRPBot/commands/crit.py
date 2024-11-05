import discord
from discord import app_commands
from discord.ext import commands
import math

class CritCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="crit", description="Calculate the critical strike damage of a move.")
    async def crit(
        self, 
        interaction: discord.Interaction, 
        damage: int, 
        stab: str = "no", 
        effective: str = "neutral",
        bonus: int = 0, 
        item_bonus: int = 0
    ):
        # Validate inputs for STAB and effectiveness
        if stab.lower() not in ["yes", "no"]:
            await interaction.response.send_message("Invalid STAB option. Please select 'yes' or 'no'.")
            return

        if effective.lower() not in ["neutral", "super_effective", "double_effective", "not_effective", "double_not_effective"]:
            await interaction.response.send_message("Invalid effectiveness option. Choose from 'neutral', 'super_effective', 'double_effective', 'not_effective', or 'double_not_effective'.")
            return

        # Base critical damage
        crit_damage = damage

        # Apply STAB if applicable
        if stab.lower() == "yes":
            crit_damage += 1  # Add 1 for STAB

        # Apply effectiveness modifier
        if effective.lower() == "super_effective":
            crit_damage += 1  # Add 1 for super effective
        elif effective.lower() == "double_effective":
            crit_damage += 2  # Add 2 for double effective
        elif effective.lower() == "not_effective":
            crit_damage -= 1  # Subtract 1 for not very effective
        elif effective.lower() == "double_not_effective":
            crit_damage -= 2  # Subtract 2 for double ineffective

        # Apply generic bonus (e.g., environmental, situational, etc.)
        crit_damage += bonus  # Directly add the bonus to the damage

        # Apply item bonus (fixed integer)
        crit_damage += item_bonus  # Directly add item bonus to damage

        # Apply critical multiplier
        crit_damage = math.ceil(crit_damage * 1.5)  # Multiply by 1.5 for critical and round up

        # Respond with the final damage
        await interaction.response.send_message(f"The critical strike damage is: {crit_damage}")

async def setup(bot):
    await bot.add_cog(CritCommand(bot))
