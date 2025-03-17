import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from helpers import load_move

# Directory where move JSON files are stored.
MOVES_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/moves")

def get_field_value(move: dict, keys: list, default):
    """
    Searches the move dictionary for any key matching one of the provided keys (case-insensitive).
    Returns the corresponding value if found; otherwise returns the default.
    """
    for key in keys:
        for k, value in move.items():
            if k.lower() == key.lower():
                return value
    return default

class MTemplateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def move_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # List move names by stripping the .json extension.
        move_names = [f[:-5] for f in os.listdir(MOVES_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in move_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    @app_commands.command(
        name="mtemplate",
        description="Display a standardized move template for editing."
    )
    @app_commands.autocomplete(move=move_autocomplete)
    async def mtemplate(self, interaction: discord.Interaction, move: str):
        loaded_move = load_move(move)
        if loaded_move is None:
            await interaction.response.send_message(f"Move '{move}' not found.", ephemeral=True)
            return

        # Build a standardized dictionary using version 2 keys.
        standardized_move = {
            "name": get_field_value(loaded_move, ["name", "Name"], "Template"),
            "type": get_field_value(loaded_move, ["type", "Type"], "Typeless/any Type"),
            "power": get_field_value(loaded_move, ["power", "Power"], 0),
            "damage": get_field_value(loaded_move, ["damage", "damage1", "Damage1"], "Strength/Special etc."),
            "accuracy": get_field_value(loaded_move, ["accuracy", "accuracy1", "Accuracy1"], "Dexterity/Insight etc."),
            "target": get_field_value(loaded_move, ["target", "Target"], "Foe/User/etc"),
            "effect": get_field_value(loaded_move, ["effect", "Effect"], "Effect Description"),
            "description": get_field_value(loaded_move, ["description", "Description"], "Some roleplay description"),
            "category": get_field_value(loaded_move, ["category", "Category"], "Physical/Special/Support")
        }

        # Format the standardized move as indented JSON.
        formatted_json = json.dumps(standardized_move, indent=4)
        # Send the formatted JSON inside a code block with JSON syntax highlighting.
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

async def setup(bot):
    await bot.add_cog(MTemplateCommand(bot))
