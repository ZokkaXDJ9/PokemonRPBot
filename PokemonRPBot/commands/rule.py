import discord
from discord import app_commands
from discord.ext import commands
import os
from helpers import load_rule  # Function to load rule data

# Directory where rule files are stored
RULES_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/rules")

class RulesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest rule names
    async def autocomplete_rule(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # List all rule files and strip the '.json' extension
        rule_names = [
            f[:-5] for f in os.listdir(RULES_DIRECTORY) if f.endswith(".json")
        ]
        
        # Filter rules to those that contain the current input as a substring (case insensitive)
        suggestions = [
            app_commands.Choice(name=rule, value=rule)
            for rule in rule_names
            if current.lower() in rule.lower()
        ]

        # Limit to 25 choices as per Discord's restriction
        return suggestions[:25]

    @app_commands.command(name="rule", description="Display details of a game rule")
    @app_commands.autocomplete(name=autocomplete_rule)
    async def rules(self, interaction: discord.Interaction, name: str):
        # Load the rule data from JSON file
        rule = load_rule(name)  # Use a helper function to load rule data
        if rule is None:
            await interaction.response.send_message(
                content=f"Unable to find a rule named **{name}**, sorry! If that wasn't a typo, maybe it isn't implemented yet?",
                ephemeral=True
            )
            return

        # Construct a plain text message with Discord Markdown formatting
        response = f"""
### {rule['name']}
*{rule['flavor']}*

{rule['text']}
"""

        # Optionally add the "example" field if it is not empty
        if rule.get("example"):
            response += f"**Example**: {rule['example']}\n"

        # Send the message as plain text, formatted with Markdown
        await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(RulesCommand(bot))
