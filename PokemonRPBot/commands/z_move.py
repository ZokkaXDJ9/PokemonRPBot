import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from helpers import load_z_move, ParsedRollQuery
from emojis import get_type_emoji, get_category_emoji

# Directories for z_move files and character files
MOVES_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/z_moves")
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

def get_z_move_field(z_move: dict, field: str, alt_field: str = None):
    """
    Retrieve a value from the z_move dict, trying both the provided key and an alternate version.
    If alt_field is not provided, defaults to the lowercase version of field.
    """
    if alt_field is None:
        alt_field = field.lower()
    return z_move.get(field) or z_move.get(alt_field)

class ZMoveCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def z_move_name_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        z_move_names = [
            f[:-5] for f in os.listdir(MOVES_DIRECTORY) if f.endswith(".json")
        ]
        suggestions = [
            app_commands.Choice(name=z_move, value=z_move)
            for z_move in z_move_names
            if current.lower() in z_move.lower()
        ]
        return suggestions[:25]

    @app_commands.command(
        name="z_move", 
        description="Display details of a Pokémon z_move."
    )
    @app_commands.autocomplete(z_move=z_move_name_autocomplete)
    async def z_move(self, interaction: discord.Interaction, z_move: str):
        z_move = load_z_move(z_move)
        if z_move is None:
            await interaction.response.send_message(
                f"Move '{z_move}' not found.", ephemeral=True
            )
            return

        user_stats = load_user_stats(interaction.user.id)

        # Retrieve z_move fields using the helper to support both key formats.
        z_move_name_field = get_z_move_field(z_move, "Name")
        type_field = get_z_move_field(z_move, "Type")
        category_field = get_z_move_field(z_move, "Category")
        description_field = get_z_move_field(z_move, "Description")
        target_field = get_z_move_field(z_move, "Target")
        effect_field = get_z_move_field(z_move, "Effect")
        damage_field = get_z_move_field(z_move, "Damage2", "damage")
        power_field = get_z_move_field(z_move, "Power", "power")
        accuracy_field = get_z_move_field(z_move, "Accuracy1", "accuracy")

        # Get emojis for the z_move's type and category
        type_icon = get_type_emoji(type_field)
        category_icon = get_category_emoji(category_field)

        # Build the z_move description text
        z_move_description = f"""
### {z_move_name_field}
*{description_field}*
**Type**: {type_icon} {type_field} — **{category_icon} {category_field}**
**Target**: {target_field}
"""
        if damage_field:
            z_move_description += f"**Damage Dice**: {damage_field} + {power_field}\n"
        z_move_description += f"""**Accuracy Dice**: {accuracy_field} + Rank
**Effect**: {effect_field}
"""

        # For now, just send the z_move description without interactive buttons.
        await interaction.response.send_message(z_move_description)

        # The following code is for interactive roll buttons (a feature for later).
        # Uncomment the lines below when you're ready to enable roll buttons.
        #
        # if user_stats is None:
        #     await interaction.response.send_message(z_move_description)
        #     return
        #
        # # Prepare dice roll values using user stats.
        # accuracy_stat = accuracy_field.lower() if accuracy_field else ""
        # rank = 1  # Default rank value
        # accuracy_dice = user_stats["stats"].get(accuracy_stat, 0) + rank
        #
        # damage_stat = damage_field.lower() if damage_field else None
        # damage_dice = (
        #     user_stats["stats"].get(damage_stat, 0) + int(power_field)
        #     if damage_stat and power_field != ""
        #     else None
        # )
        #
        # class RollView(discord.ui.View):
        #     @discord.ui.button(label="Roll Accuracy", style=discord.ButtonStyle.primary)
        #     async def roll_accuracy(self, interaction: discord.Interaction, button: discord.ui.Button):
        #         # Roll for accuracy.
        #         accuracy_query = build_dice_query(accuracy_dice)
        #         parsed_query = ParsedRollQuery.from_query(accuracy_query)
        #         accuracy_result = parsed_query.execute()
        #
        #         roll_response = f"""
        # ### {z_move_name_field}
        # **Accuracy Roll**: {accuracy_result}
        # """
        #         await interaction.response.send_message(
        #             roll_response,
        #             view=RerollView(accuracy_query, is_accuracy=True)
        #         )
        #
        #     @discord.ui.button(
        #         label="Roll Damage", 
        #         style=discord.ButtonStyle.primary, 
        #         disabled=(damage_dice is None)
        #     )
        #     async def roll_damage(self, interaction: discord.Interaction, button: discord.ui.Button):
        #         if damage_dice is None:
        #             await interaction.response.send_message(
        #                 "This z_move has no damage roll.", ephemeral=True
        #             )
        #             return
        #
        #         # Roll for damage.
        #         damage_query = build_dice_query(damage_dice)
        #         parsed_query = ParsedRollQuery.from_query(damage_query)
        #         damage_result = parsed_query.execute()
        #
        #         roll_response = f"""
        # ### {z_move_name_field}
        # **Damage Roll**: {damage_result}
        # """
        #         await interaction.response.send_message(
        #             roll_response,
        #             view=RerollView(damage_query, is_accuracy=False)
        #         )
        #
        # class RerollView(discord.ui.View):
        #     def __init__(self, query: str, is_accuracy: bool):
        #         super().__init__()
        #         self.query = query
        #         self.is_accuracy = is_accuracy
        #
        #     @discord.ui.button(label="Reroll", style=discord.ButtonStyle.primary)
        #     async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        #         parsed_query = ParsedRollQuery.from_query(self.query)
        #         result = parsed_query.execute()
        #
        #         roll_type = "Accuracy" if self.is_accuracy else "Damage"
        #         roll_response = f"""
        # ### {z_move_name_field}
        # **{roll_type} Reroll**: {result}
        # """
        #         await interaction.response.send_message(roll_response)
        #
        # # Send the initial z_move description with interactive roll buttons.
        # await interaction.response.send_message(z_move_description, view=RollView())

async def setup(bot):
    await bot.add_cog(ZMoveCommand(bot))
