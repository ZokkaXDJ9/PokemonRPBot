import discord
from discord import app_commands
from discord.ext import commands
from helpers import ParsedRollQuery

class RollView(discord.ui.View):
    def __init__(self, query_string: str):
        super().__init__()
        # Add the "Roll again" button to the view
        self.add_item(discord.ui.Button(label="Roll again!", custom_id=query_string))

class RollCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="r", description="Roll dice using a '1d6+4' style query.")
    async def roll(self, interaction: discord.Interaction, query: str):
        parsed_query = ParsedRollQuery.from_query(query)
        result_text = parsed_query.execute()
        query_string = parsed_query.as_button_callback_query_string()
        
        # Use RollView to add the button
        await interaction.response.send_message(
            content=result_text,
            view=RollView(query_string)  # Use 'view' instead of 'components'
        )

async def setup(bot):
    await bot.add_cog(RollCommand(bot))
