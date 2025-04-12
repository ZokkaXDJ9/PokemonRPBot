import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from helpers import load_move, load_legend_move, load_ability, load_item, load_potion, load_rule, load_status, load_weather, load_z_move

# Directories for each JSON category.
ABILITIES_DIRECTORY     = os.path.join(os.path.dirname(__file__), "../Data/abilities")
ITEMS_DIRECTORY         = os.path.join(os.path.dirname(__file__), "../Data/items")
LEGENDMOVES_DIRECTORY   = os.path.join(os.path.dirname(__file__), "../Data/legend_moves")
MOVES_DIRECTORY         = os.path.join(os.path.dirname(__file__), "../Data/moves")
POTIONS_DIRECTORY       = os.path.join(os.path.dirname(__file__), "../Data/potions")
RULES_DIRECTORY         = os.path.join(os.path.dirname(__file__), "../Data/rules")
STATUS_DIRECTORY        = os.path.join(os.path.dirname(__file__), "../Data/status")
WEATHER_DIRECTORY       = os.path.join(os.path.dirname(__file__), "../Data/weather")
ZMOVES_DIRECTORY        = os.path.join(os.path.dirname(__file__), "../Data/z_moves")

def get_field_value(item: dict, keys: list, default):
    """
    Searches the given dictionary for any key matching one of the provided keys (case-insensitive).
    Returns the corresponding value if found; otherwise returns the default.
    """
    for key in keys:
        for k, value in item.items():
            if k.lower() == key.lower():
                return value
    return default

class TemplateCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Autocomplete functions for each category ---

    async def move_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        move_names = [f[:-5] for f in os.listdir(MOVES_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in move_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def legend_move_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        move_names = [f[:-5] for f in os.listdir(LEGENDMOVES_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in move_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def ability_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        ability_names = [f[:-5] for f in os.listdir(ABILITIES_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in ability_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def item_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        item_names = [f[:-5] for f in os.listdir(ITEMS_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in item_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def potion_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        potion_names = [f[:-5] for f in os.listdir(POTIONS_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in potion_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def rule_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        rule_names = [f[:-5] for f in os.listdir(RULES_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in rule_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def status_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        status_names = [f[:-5] for f in os.listdir(STATUS_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in status_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def weather_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        weather_names = [f[:-5] for f in os.listdir(WEATHER_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in weather_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    async def zmove_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        zmove_names = [f[:-5] for f in os.listdir(ZMOVES_DIRECTORY) if f.endswith(".json")]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in zmove_names if current.lower() in name.lower()
        ]
        return suggestions[:25]

    # --- Template Commands for each category ---

    @app_commands.command(
        name="mtemplate",
        description="Display a standardized move template for editing."
    )
    @app_commands.autocomplete(move=move_autocomplete)
    async def mtemplate(self, interaction: discord.Interaction, move: str):
        loaded_move = load_move(move)
        if loaded_move is None:
            await interaction.response.send_message(f"Move '{move}' not found.", ephemeral=True)
            return

        standardized_move = {
            "name": get_field_value(loaded_move, ["name", "Name"], "Template"),
            "type": get_field_value(loaded_move, ["type", "Type"], "Typeless/any Type"),
            "power": get_field_value(loaded_move, ["power", "Power"], 0),
            "damage": get_field_value(loaded_move, ["damage", "damage1", "Damage1"], "Strength/Special etc."),
            "accuracy": get_field_value(loaded_move, ["accuracy", "accuracy1", "Accuracy1"], "Dexterity/Insight etc."),
            "target": get_field_value(loaded_move, ["target", "Target"], "Foe/User/etc"),
            "effect": get_field_value(loaded_move, ["effect", "Effect"], "Effect Description"),
            "description": get_field_value(loaded_move, ["description", "Description"], "Some roleplay description"),
            "category": get_field_value(loaded_move, ["category", "Category"], "Physical/Special/Support")
        }
        formatted_json = json.dumps(standardized_move, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
            name="ltemplate",
            description="Display a standardized legendary move template for editing."
        )
    @app_commands.autocomplete(legend_move=legend_move_autocomplete)
    async def ltemplate(self, interaction: discord.Interaction, legend_move: str):
        loaded_legend_move = load_legend_move(legend_move)
        if loaded_legend_move is None:
            await interaction.response.send_message(f"Legendary Move '{legend_move}' not found.", ephemeral=True)
            return

        standardized_legend_move = {
            "name": get_field_value(loaded_legend_move, ["name", "Name"], "Template"),
            "type": get_field_value(loaded_legend_move, ["type", "Type"], "Typeless/any Type"),
            "power": get_field_value(loaded_legend_move, ["power", "Power"], 0),
            "damage": get_field_value(loaded_legend_move, ["damage", "damage1", "Damage1"], "Strength/Special etc."),
            "accuracy": get_field_value(loaded_legend_move, ["accuracy", "accuracy1", "Accuracy1"], "Dexterity/Insight etc."),
            "target": get_field_value(loaded_legend_move, ["target", "Target"], "Foe/User/etc"),
            "effect": get_field_value(loaded_legend_move, ["effect", "Effect"], "Effect Description"),
            "description": get_field_value(loaded_legend_move, ["description", "Description"], "Some roleplay description"),
            "category": get_field_value(loaded_legend_move, ["category", "Category"], "Physical/Special/Support")
        }
        formatted_json = json.dumps(standardized_legend_move, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
        name="atemplate",
        description="Display a standardized ability template for editing."
    )
    @app_commands.autocomplete(ability=ability_autocomplete)
    async def atemplate(self, interaction: discord.Interaction, ability: str):
        loaded_ability = load_ability(ability)
        if loaded_ability is None:
            await interaction.response.send_message(f"Ability '{ability}' not found.", ephemeral=True)
            return

        standardized_ability = {
            "name": get_field_value(loaded_ability, ["name", "Name"], "Template Ability"),
            "description": get_field_value(loaded_ability, ["description", "Description"], "No description provided"),
            "effect": get_field_value(loaded_ability, ["effect", "Effect"], "No effect defined")
        }
        formatted_json = json.dumps(standardized_ability, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
        name="itemplate",
        description="Display a standardized item template for editing."
    )
    @app_commands.autocomplete(item=item_autocomplete)
    async def itemplate(self, interaction: discord.Interaction, item: str):
        loaded_item = load_item(item)
        if loaded_item is None:
            await interaction.response.send_message(f"Item '{item}' not found.", ephemeral=True)
            return

        standardized_item = {
            "name": get_field_value(loaded_item, ["name", "Name"], "Template Item"),
            "description": get_field_value(loaded_item, ["description", "Description"], "No description provided"),
            "category": get_field_value(loaded_item, ["category", "Category"], "Uncategorized"),
            "single_use": get_field_value(loaded_item, ["single_use", "Single_Use"], False)
        }
        formatted_json = json.dumps(standardized_item, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
        name="ptemplate",
        description="Display a standardized potion template for editing."
    )
    @app_commands.autocomplete(potion=potion_autocomplete)
    async def ptemplate(self, interaction: discord.Interaction, potion: str):
        loaded_potion = load_potion(potion)
        if loaded_potion is None:
            await interaction.response.send_message(f"Potion '{potion}' not found.", ephemeral=True)
            return

        standardized_potion = {
            "name": get_field_value(loaded_potion, ["name", "Name"], "Template Potion"),
            "description": get_field_value(loaded_potion, ["description", "Description"], "No description provided"),
            "effect": get_field_value(loaded_potion, ["effect", "Effect"], "No effect defined"),
            "recipes": get_field_value(loaded_potion, ["recipes", "Recipes"], [])
        }
        formatted_json = json.dumps(standardized_potion, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
        name="rtemplate",
        description="Display a standardized rule template for editing."
    )
    @app_commands.autocomplete(rule=rule_autocomplete)
    async def rtemplate(self, interaction: discord.Interaction, rule: str):
        loaded_rule = load_rule(rule)
        if loaded_rule is None:
            await interaction.response.send_message(f"Rule '{rule}' not found.", ephemeral=True)
            return

        standardized_rule = {
            "name": get_field_value(loaded_rule, ["name", "Name"], "Template Rule"),
            "flavor": get_field_value(loaded_rule, ["flavor", "Flavor"], "No flavor text provided"),
            "text": get_field_value(loaded_rule, ["text", "Text"], "No rule text provided"),
            "example": get_field_value(loaded_rule, ["example", "Example"], "")
        }
        formatted_json = json.dumps(standardized_rule, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
        name="stemplate",
        description="Display a standardized status template for editing."
    )
    @app_commands.autocomplete(status=status_autocomplete)
    async def stemplate(self, interaction: discord.Interaction, status: str):
        loaded_status = load_status(status)
        if loaded_status is None:
            await interaction.response.send_message(f"Status '{status}' not found.", ephemeral=True)
            return

        standardized_status = {
            "name": get_field_value(loaded_status, ["name", "Name"], "Template Status"),
            "description": get_field_value(loaded_status, ["description", "Description"], "No description provided"),
            "resist": get_field_value(loaded_status, ["resist", "Resist"], "No resist information"),
            "effect": get_field_value(loaded_status, ["effect", "Effect"], "No effect defined"),
            "duration": get_field_value(loaded_status, ["duration", "Duration"], "Duration not specified")
        }
        formatted_json = json.dumps(standardized_status, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
        name="wtemplate",
        description="Display a standardized weather template for editing."
    )
    @app_commands.autocomplete(weather=weather_autocomplete)
    async def wtemplate(self, interaction: discord.Interaction, weather: str):
        loaded_weather = load_weather(weather)
        if loaded_weather is None:
            await interaction.response.send_message(f"Weather '{weather}' not found.", ephemeral=True)
            return

        standardized_weather = {
            "name": get_field_value(loaded_weather, ["name", "Name"], "Template Weather"),
            "description": get_field_value(loaded_weather, ["description", "Description"], "No description provided"),
            "effect": get_field_value(loaded_weather, ["effect", "Effect"], "No effect defined")
        }
        formatted_json = json.dumps(standardized_weather, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

    @app_commands.command(
        name="ztemplate",
        description="Display a standardized Z‑Move template for editing."
    )
    @app_commands.autocomplete(zmove=zmove_autocomplete)
    async def ztemplate(self, interaction: discord.Interaction, zmove: str):
        loaded_zmove = load_z_move(zmove)
        if loaded_zmove is None:
            await interaction.response.send_message(f"Z‑Move '{zmove}' not found.", ephemeral=True)
            return

        standardized_zmove = {
            "name": get_field_value(loaded_zmove, ["name", "Name"], "Template Z‑Move"),
            "type": get_field_value(loaded_zmove, ["type", "Type"], "Typeless"),
            "power": get_field_value(loaded_zmove, ["power", "Power"], 0),
            "damage1": get_field_value(loaded_zmove, ["damage", "Damage1", "damage1"], ""),
            "damage2": get_field_value(loaded_zmove, ["damage2", "Damage2"], ""),
            "accuracy1": get_field_value(loaded_zmove, ["accuracy", "Accuracy1", "accuracy1"], ""),
            "accuracy2": get_field_value(loaded_zmove, ["accuracy2", "Accuracy2"], ""),
            "target": get_field_value(loaded_zmove, ["target", "Target"], "Battlefield"),
            "effect": get_field_value(loaded_zmove, ["effect", "Effect"], "No effect defined"),
            "description": get_field_value(loaded_zmove, ["description", "Description"], "No description provided"),
            "_id": get_field_value(loaded_zmove, ["_id"], ""),
            "attributes": get_field_value(loaded_zmove, ["attributes", "Attributes"], {}),
            "added_effects": get_field_value(loaded_zmove, ["addedeffects", "AddedEffects"], {}),
            "category": get_field_value(loaded_zmove, ["category", "Category"], "Support")
        }
        formatted_json = json.dumps(standardized_zmove, indent=4)
        await interaction.response.send_message(f"```json\n{formatted_json}\n```")

async def setup(bot):
    await bot.add_cog(TemplateCommands(bot))
