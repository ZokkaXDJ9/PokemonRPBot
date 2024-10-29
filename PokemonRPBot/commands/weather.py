import discord
from discord import app_commands
from discord.ext import commands
import os
from helpers import load_weather  # Function to load weather data

# Directory where weather files are stored
WEATHER_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/weather")

class WeatherCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest weather names
    async def autocomplete_weather(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # List all weather files and strip the '.json' extension
        weather_names = [
            f[:-5] for f in os.listdir(WEATHER_DIRECTORY) if f.endswith(".json")
        ]
        
        # Filter weather names to those that contain the current input as a substring (case insensitive)
        suggestions = [
            app_commands.Choice(name=weather, value=weather)
            for weather in weather_names
            if current.lower() in weather.lower()
        ]

        # Limit to 25 choices as per Discord's restriction
        return suggestions[:25]

    @app_commands.command(name="weather", description="Display details of a weather effect")
    @app_commands.autocomplete(name=autocomplete_weather)
    async def weather(self, interaction: discord.Interaction, name: str):
        # Load the weather data from JSON file
        weather = load_weather(name)  # Use a helper function to load weather data
        if weather is None:
            await interaction.response.send_message(
                content=f"Unable to find a weather effect named **{name}**, sorry! If that wasn't a typo, maybe it isn't implemented yet?",
                ephemeral=True
            )
            return

        # Construct a plain text message with Discord Markdown formatting
        response = f"""
### {weather['name']} Weather
*{weather['description']}*
{weather['effect']}
"""

        # Send the message as plain text, formatted with Markdown
        await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(WeatherCommand(bot))
