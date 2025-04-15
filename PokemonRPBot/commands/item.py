import discord
from discord import app_commands
from discord.ext import commands
import os
from helpers import load_item  # Function to load item data

# Directory where item files are stored
ITEM_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/items")

class ItemCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest item names
    async def autocomplete_item(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # List all item files and strip the '.json' extension
        item_names = [
            f[:-5] for f in os.listdir(ITEM_DIRECTORY) if f.endswith(".json")
        ]
        
        # Filter items to those that contain the current input as a substring (case insensitive)
        suggestions = [
            app_commands.Choice(name=item, value=item)
            for item in item_names
            if current.lower() in item.lower()
        ]

        # Limit to 25 choices as per Discord's restriction
        return suggestions[:25]

    @app_commands.command(name="item", description="Display details of an item")
    @app_commands.autocomplete(name=autocomplete_item)
    async def item(self, interaction: discord.Interaction, name: str):
        # Load the item data from JSON file or data source
        item = load_item(name)  # Use a helper function to load item data
        if item is None:
            await interaction.response.send_message(
                content=f"Unable to find an item named **{name}**, sorry! If that wasn't a typo, maybe it isn't implemented yet?",
                ephemeral=True
            )
            return

        # Construct a plain text message with Discord Markdown formatting
        response = f"""
### {item['name']}
{item['effect']}
*{item['description']}*
"""

        # Send the message as plain text, formatted with Markdown
        await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(ItemCommand(bot))
