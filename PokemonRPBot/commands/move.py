import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from helpers import load_move, ParsedRollQuery
from emojis import get_type_emoji, get_category_emoji

# Directory where move files and character files are stored
MOVES_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/moves")
CHARACTERS_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Characters")

def load_user_stats(user_id: int):
    """Load user stats from a JSON file in the Characters directory."""
    files = os.listdir(CHARACTERS_DIRECTORY)
    matching_file = next(
        (f for f in files if f.startswith(f"{user_id}_") and f.endswith(".json")), 
        None
    )
    if not matching_file:
        return None
    stats_file = os.path.join(CHARACTERS_DIRECTORY, matching_file)
    with open(stats_file, "r") as file:
        return json.load(file)

def build_dice_query(dice_count: int):
    """Build a query string for ParsedRollQuery based on the number of dice."""
    return f"{dice_count}d6"

class MoveCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def move_name_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        move_names = [
            f[:-5] for f in os.listdir(MOVES_DIRECTORY) if f.endswith(".json")
        ]
        suggestions = [
            app_commands.Choice(name=move, value=move)
            for move in move_names
            if current.lower() in move.lower()
        ]
        return suggestions[:25]

    @app_commands.command(name="move", description="Display and roll details of a Pokémon move.")
    @app_commands.autocomplete(move_name=move_name_autocomplete)
    async def move(self, interaction: discord.Interaction, move_name: str):
        move = load_move(move_name)
        if move is None:
            await interaction.response.send_message(f"Move '{move_name}' not found.", ephemeral=True)
            return

        user_stats = load_user_stats(interaction.user.id)
        if user_stats is None:
            await interaction.response.send_message("User stats not found. Please set up your stats first.", ephemeral=True)
            return

        # Get emojis for the move's type and category
        type_icon = get_type_emoji(move["Type"])
        category_icon = get_category_emoji(move["Category"])

        # Construct the base response
        move_description = f"""
### {move['Name']}
*{move['Description']}*
**Type**: {type_icon} {move['Type']} — **{category_icon} {move['Category']}**
**Target**: {move["Target"]}
"""
        if move["Damage1"]:
            move_description += f"**Damage Dice**: {move['Damage1']} + {move['Power']}\n"
        move_description += f"""**Accuracy Dice**: {move["Accuracy1"]} + Rank
**Effect**: {move["Effect"]}
"""

        # Extract stats needed for rolls
        accuracy_stat = move["Accuracy1"].lower()
        rank = 1  # Default rank
        accuracy_dice = user_stats["stats"].get(accuracy_stat, 0) + rank

        damage_stat = move["Damage1"].lower() if move["Damage1"] else None
        damage_dice = (
            user_stats["stats"].get(damage_stat, 0) + int(move["Power"])
            if damage_stat
            else None
        )

        class RollView(discord.ui.View):
            @discord.ui.button(label="Roll Accuracy", style=discord.ButtonStyle.primary)
            async def roll_accuracy(self, interaction: discord.Interaction, button: discord.ui.Button):
                # Parse and roll for accuracy
                accuracy_query = build_dice_query(accuracy_dice)
                parsed_query = ParsedRollQuery.from_query(accuracy_query)
                accuracy_result = parsed_query.execute()

                # Send a new message with accuracy roll and reroll button
                roll_response = f"""
### {move['Name']}
**Accuracy Roll**: {accuracy_result}
"""
                await interaction.response.send_message(
                    roll_response, 
                    view=RerollView(accuracy_query, is_accuracy=True)
                )

            @discord.ui.button(label="Roll Damage", style=discord.ButtonStyle.primary, disabled=(damage_dice is None))
            async def roll_damage(self, interaction: discord.Interaction, button: discord.ui.Button):
                if damage_dice is None:
                    await interaction.response.send_message("This move has no damage roll.", ephemeral=True)
                    return

                # Parse and roll for damage
                damage_query = build_dice_query(damage_dice)
                parsed_query = ParsedRollQuery.from_query(damage_query)
                damage_result = parsed_query.execute()

                # Send a new message with damage roll and reroll button
                roll_response = f"""
### {move['Name']}
**Damage Roll**: {damage_result}
"""
                await interaction.response.send_message(
                    roll_response, 
                    view=RerollView(damage_query, is_accuracy=False)
                )

        class RerollView(discord.ui.View):
            def __init__(self, query: str, is_accuracy: bool):
                super().__init__()
                self.query = query
                self.is_accuracy = is_accuracy

            @discord.ui.button(label="Reroll", style=discord.ButtonStyle.primary)
            async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
                # Parse and reroll
                parsed_query = ParsedRollQuery.from_query(self.query)
                result = parsed_query.execute()

                roll_type = "Accuracy" if self.is_accuracy else "Damage"
                roll_response = f"""
### {move['Name']}
**{roll_type} Reroll**: {result}
"""
                await interaction.response.send_message(roll_response)

        # Send the initial move description with the roll buttons
        await interaction.response.send_message(move_description, view=RollView())

async def setup(bot):
    await bot.add_cog(MoveCommand(bot))
