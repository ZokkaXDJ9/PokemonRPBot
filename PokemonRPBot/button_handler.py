import discord
from helpers import ParsedRollQuery  # Ensure ParsedRollQuery is defined or imported in helpers

class RollView(discord.ui.View):
    def __init__(self, query_string: str):
        super().__init__(timeout=180)  # Timeout for button inactivity
        self.query_string = query_string  # Store query string to reuse it in the callback

        # Add the "Roll again" button
        self.add_item(
            discord.ui.Button(
                label="Roll again!",
                style=discord.ButtonStyle.primary,
                custom_id="roll_again"
            )
        )

    @discord.ui.button(label="Roll again!", style=discord.ButtonStyle.primary, custom_id="roll_again")
    async def roll_again_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Parse the query string to retrieve the previous roll parameters
        parsed_query = ParsedRollQuery.from_query_string(self.query_string)

        # Execute the roll again and get the result text
        result_text = parsed_query.execute()

        # Update the interaction with the new roll result
        await interaction.response.edit_message(content=result_text, view=self)

# Function to get a RollView instance based on a query string
def get_roll_view(query_string: str) -> RollView:
    return RollView(query_string)
