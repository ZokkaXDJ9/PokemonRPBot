import discord
from discord import app_commands
from discord.ext import commands
import os
from helpers import load_status  # Function to load status data

# Directory where status files are stored
STATUS_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/status")

class StatusCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest status names
    async def autocomplete_status(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # List all status files and strip the '.json' extension
        status_names = [
            f[:-5] for f in os.listdir(STATUS_DIRECTORY) if f.endswith(".json")
        ]
        
        # Filter statuses to those that contain the current input as a substring (case insensitive)
        suggestions = [
            app_commands.Choice(name=status, value=status)
            for status in status_names
            if current.lower() in status.lower()
        ]

        # Limit to 25 choices as per Discord's restriction
        return suggestions[:25]

    @app_commands.command(name="status", description="Display details of a status effect")
    @app_commands.autocomplete(name=autocomplete_status)
    async def status(self, interaction: discord.Interaction, name: str):
        # Load the status data from JSON file
        status = load_status(name)  # Use a helper function to load status data
        if status is None:
            await interaction.response.send_message(
                content=f"Unable to find a status named **{name}**, sorry! If that wasn't a typo, maybe it isn't implemented yet?",
                ephemeral=True
            )
            return

        # Construct a plain text message with Discord Markdown formatting
        response = f"""
### {status['name']}
*{status['description']}*
- {status['resist']}
- {status['effect']}
- {status['duration']}
"""

        # Send the message as plain text, formatted with Markdown
        await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(StatusCommand(bot))
