import discord
from discord import app_commands
from discord.ext import commands
import os
import json

def normalize_keys(obj):
    """Recursively convert all dictionary keys to lowercase."""
    if isinstance(obj, dict):
        return {k.lower(): normalize_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_keys(i) for i in obj]
    return obj

def load_item(item_name: str):
    """
    Load an item JSON file from the items directory,
    normalize all keys to lowercase,
    and return the data as a dictionary.
    """
    ITEM_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/items")
    file_path = os.path.join(ITEM_DIRECTORY, f"{item_name}.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return normalize_keys(data)
    except FileNotFoundError:
        return None

class ItemCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def autocomplete_item(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """
        List item filenames (without the .json extension) for autocompletion.
        """
        ITEM_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/items")
        item_names = [f[:-5] for f in os.listdir(ITEM_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=item, value=item)
            for item in item_names
            if current.lower() in item.lower()
        ]
        return suggestions[:25]

    @app_commands.command(name="item", description="Display details of an item")
    @app_commands.autocomplete(name=autocomplete_item)
    async def item(self, interaction: discord.Interaction, name: str):
        # Load the item data (with normalized keys)
        item = load_item(name)
        if item is None:
            await interaction.response.send_message(
                content=f"Unable to find an item named **{name}**, sorry!",
                ephemeral=True,
            )
            return

        # Retrieve keys—after normalization, the keys will be lower-case.
        name_text = item.get("name", "Unnamed Item")
        # effect may not exist in all versions; it will be printed if provided.
        effect_text = item.get("effect", "").strip()
        description_text = item.get("description", "No description provided")
        # Some files have a "category" key; otherwise default to "unknown".
        category_text = item.get("category", "unknown")

        # Construct the output using Markdown formatting:
        # - Item name as a level-3 header.
        # - (Optionally) the effect on a separate line.
        # - The description italicized.
        # - The category, on a new line in bold.
        response = f"### {name_text}\n"
        if effect_text:
            response += f"{effect_text}\n"
        response += f"{description_text}\n"
        response += f"**Category:** {category_text}"

        await interaction.response.send_message(response)

async def setup(bot: commands.Bot):
    await bot.add_cog(ItemCommand(bot))
