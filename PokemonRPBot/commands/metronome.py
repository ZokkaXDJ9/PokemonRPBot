import discord
from discord import app_commands
from discord.ext import commands
import os
import random
from helpers import load_move
from emojis import get_type_emoji, get_category_emoji

# Directory where move files are stored
MOVES_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/moves")

class MetronomeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="metronome", description="Use the most randomest of moves!")
    async def metronome(self, interaction: discord.Interaction):
        """
        Randomly selects and displays a Pokémon move.
        """
        # List all JSON files in the moves directory
        move_names = [
            f[:-5] for f in os.listdir(MOVES_DIRECTORY) if f.endswith(".json")
        ]

        # Choose a random move
        if not move_names:
            await interaction.response.send_message(
                "No moves found in the data directory.", ephemeral=True
            )
            return

        random_move_name = random.choice(move_names)
        move = load_move(random_move_name)

        if move is None:
            await interaction.response.send_message(
                f"Error: Randomly selected move '{random_move_name}' could not be loaded. This should never happen.",
                ephemeral=True
            )
            return

        # Get emojis for the move's type and category
        type_icon = get_type_emoji(move["Type"])
        category_icon = get_category_emoji(move["Category"])

        # Construct a plain text message with Discord Markdown formatting
        response = f"""
### {move['Name']}
*{move['Description']}*
**Type**: {type_icon} {move['Type']} — **{category_icon} {move['Category']}**
**Target**: {move["Target"]}
"""
        # Add Damage Dice line if "Damage1" is not empty
        if move["Damage1"]:
            response += f"**Damage Dice**: {move['Damage1']} + {move['Power']}\n"
        
        # Add Accuracy Dice and Effect lines
        response += f"""**Accuracy Dice**: {move["Accuracy1"]} + Rank
**Effect**: {move["Effect"]}
"""

        # Send the random move information as a response
        await interaction.response.send_message(response)

async def setup(bot):
    """
    Sets up the MetronomeCommand cog for the bot.
    """
    await bot.add_cog(MetronomeCommand(bot))
