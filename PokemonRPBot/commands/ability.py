import discord
from discord import app_commands
from discord.ext import commands
import os
from helpers import load_ability  # Function to load ability data

# Directory where ability files are stored
ABILITIES_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/abilities")

class AbilityCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest ability names
    async def autocomplete_ability(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # List all ability files and strip the '.json' extension
        ability_names = [
            f[:-5] for f in os.listdir(ABILITIES_DIRECTORY) if f.endswith(".json")
        ]
        
        # Filter abilities to those that contain the current input as a substring (case insensitive)
        suggestions = [
            app_commands.Choice(name=ability, value=ability)
            for ability in ability_names
            if current.lower() in ability.lower()
        ]

        # Limit to 25 choices as per Discord's restriction
        return suggestions[:25]

    @app_commands.command(name="ability", description="Display details of an ability")
    @app_commands.autocomplete(name=autocomplete_ability)
    async def ability(self, interaction: discord.Interaction, name: str):
        # Load the ability data from JSON file or data source
        ability = load_ability(name)  # Use a helper function to load ability data
        if ability is None:
            await interaction.response.send_message(
                content=f"Unable to find an ability named **{name}**, sorry! If that wasn't a typo, maybe it isn't implemented yet?",
                ephemeral=True
            )
            return

        # Construct a plain text message with Discord Markdown formatting
        response = f"""
### {ability['name']}
{ability['effect']}
*{ability['description']}*
"""

        # Send the message as plain text, formatted with Markdown
        await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(AbilityCommand(bot))
