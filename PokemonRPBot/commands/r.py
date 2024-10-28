import discord
from discord import app_commands
from discord.ext import commands
from helpers import ParsedRollQuery

class RollView(discord.ui.View):
    def __init__(self, query_string: str):
        super().__init__()
        self.query_string = query_string  # Store the query for reuse

    @discord.ui.button(label="Roll again!", style=discord.ButtonStyle.primary)
    async def roll_again_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Parse the query string to retrieve the roll parameters
        parsed_query = ParsedRollQuery.from_query(self.query_string)

        # Execute the roll again and get the result text
        result_text = parsed_query.execute()

        # Send a new message with the roll result, without the button
        await interaction.response.send_message(content=result_text, ephemeral=False)

class RollCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="r", description="Roll dice using a '1d6+4' style query.")
    async def roll(self, interaction: discord.Interaction, query: str):
        parsed_query = ParsedRollQuery.from_query(query)
        result_text = parsed_query.execute()
        query_string = parsed_query.as_button_callback_query_string()
        
        # Send the initial roll message with the button for rerolling
        await interaction.response.send_message(
            content=result_text,
            view=RollView(query_string)  # Includes "Roll again!" button
        )

async def setup(bot):
    await bot.add_cog(RollCommand(bot))
