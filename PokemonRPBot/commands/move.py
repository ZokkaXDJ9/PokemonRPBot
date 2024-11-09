import discord
from discord import app_commands
from discord.ext import commands
import os
from helpers import load_move
from emojis import get_type_emoji, get_category_emoji

# Directory where move files are stored
MOVES_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/moves")

class MoveCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest move names
    async def move_name_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # List all JSON files in the moves directory and strip the '.json' extension
        move_names = [
            f[:-5] for f in os.listdir(MOVES_DIRECTORY) if f.endswith(".json")
        ]
        
        # Filter moves to those that contain the current input as a substring (case insensitive)
        suggestions = [
            app_commands.Choice(name=move, value=move)
            for move in move_names
            if current.lower() in move.lower()
        ]

        # Limit to 25 choices as per Discord's restriction
        return suggestions[:25]

    @app_commands.command(name="move", description="Display details of a Pokémon move.")
    @app_commands.autocomplete(move_name=move_name_autocomplete)
    async def move(self, interaction: discord.Interaction, move_name: str):
        move = load_move(move_name)  # Load move data from the JSON file
        if move is None:
            await interaction.response.send_message(f"Move '{move_name}' not found.", ephemeral=True)
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

        # If the move is "Metronome," add a button
        if move_name.lower() == "metronome":
            import random
            # Create a button
            class MetronomeView(discord.ui.View):
                @discord.ui.button(label="Roll Metronome", style=discord.ButtonStyle.primary)
                async def roll_metronome(self, interaction: discord.Interaction, button: discord.ui.Button):
                    # Randomly choose a move
                    move_names = [
                        f[:-5] for f in os.listdir(MOVES_DIRECTORY) if f.endswith(".json")
                    ]
                    random_move_name = random.choice(move_names)
                    random_move = load_move(random_move_name)

                    if random_move is None:
                        await interaction.response.send_message(
                            f"Error: Randomly selected move '{random_move_name}' could not be loaded.",
                            ephemeral=True
                        )
                        return

                    # Get emojis for the randomly selected move
                    type_icon = get_type_emoji(random_move["Type"])
                    category_icon = get_category_emoji(random_move["Category"])

                    # Construct the response for the random move
                    metronome_response = f"""
### {random_move['Name']}
*{random_move['Description']}*
**Type**: {type_icon} {random_move['Type']} — **{category_icon} {random_move['Category']}**
**Target**: {random_move["Target"]}
"""
                    if random_move["Damage1"]:
                        metronome_response += f"**Damage Dice**: {random_move['Damage1']} + {random_move['Power']}\n"
                    metronome_response += f"""**Accuracy Dice**: {random_move["Accuracy1"]} + Rank
**Effect**: {random_move["Effect"]}
"""
                    await interaction.response.send_message(metronome_response)

            # Send the initial move response with the button
            await interaction.response.send_message(response, view=MetronomeView())
        else:
            # Send the move response without a button
            await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(MoveCommand(bot))
