import discord
from discord import app_commands
from discord.ext import commands
import os
from data_loader import load_pokemon_data  # Function to load Pokémon data
from emojis import get_type_emoji

# Directories where Pokémon data files are stored
POKEMON_NEW_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/pokemon_new")
POKEMON_OLD_DIRECTORY = os.path.join(os.path.dirname(__file__), "../Data/pokemon_old")

class StatsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest Pokémon names
    async def autocomplete_pokemon(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        # Load all Pokémon names from the new directory first
        pokemon_names = {
            f[:-5] for f in os.listdir(POKEMON_NEW_DIRECTORY) if f.endswith(".json")
        }
        
        # Add names from the old directory only if they aren't in the new directory
        pokemon_names.update(
            f[:-5] for f in os.listdir(POKEMON_OLD_DIRECTORY)
            if f.endswith(".json") and f[:-5] not in pokemon_names
        )

        # Sort the Pokémon names alphabetically
        sorted_names = sorted(pokemon_names)

        # Filter names that contain the current input (case insensitive)
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in sorted_names
            if current.lower() in name.lower()
        ]

        # Limit to 25 choices as per Discord's restriction
        return suggestions[:25]

    @app_commands.command(name="stats", description="Get stats for a specified Pokémon.")
    @app_commands.autocomplete(pokemon_name=autocomplete_pokemon)
    async def stats(self, interaction: discord.Interaction, pokemon_name: str):
        # Load Pokémon data from JSON file
        data = load_pokemon_data(pokemon_name)
        if data is None:
            await interaction.response.send_message(
                content=f"Unable to find a Pokémon named **{pokemon_name}**, sorry!",
                ephemeral=True
            )
            return

        # Format data as specified
        title = f"### {data['name']} [#{data['number']}]"
        size = (
            f"{data.get('height_m', 0):.2f}m / {data.get('height_ft', 0):.2f}ft   |   "
            f"{data.get('weight_kg', 0):.2f}kg / {data.get('weight_lb', 0):.2f}lbs"
        )        
        # Type with emojis, separated by " / " if there are multiple types
        type_display = " / ".join([f"{get_type_emoji(t)} {t}" for t in data["type"] if t])
        
        # Base HP
        base_hp = f"**Base HP**: {data['base_hp']}"
        
        # Format each stat with circles
        strength = f"**Strength**: {format_stat(data['strength'])}"
        dexterity = f"**Dexterity**: {format_stat(data['dexterity'])}"
        vitality = f"**Vitality**: {format_stat(data['vitality'])}"
        special = f"**Special**: {format_stat(data['special'])}"
        insight = f"**Insight**: {format_stat(data['insight'])}"
        
        # Abilities formatted with " / " separator
        abilities = " / ".join(filter(None, data["abilities"][:2]))  # Primary and Secondary
        hidden_ability = data["abilities"][2] if len(data["abilities"]) > 2 else None
        abilities_display = f"**Ability**: {abilities}" + (f" ({hidden_ability})" if hidden_ability else "")

        # Combine all formatted data into the output message
        response = f"""{title}
{size}
**Type**: {type_display}
{base_hp}
{strength}
{dexterity}
{vitality}
{special}
{insight}
{abilities_display}"""

        # Send the formatted message
        await interaction.response.send_message(response)

def format_stat(stat_tuple):
    """Formats stats using filled and empty circles based on min and max values."""
    filled = "⬤" * stat_tuple[0]
    empty = "⭘" * (stat_tuple[1] - stat_tuple[0])
    return f"{filled}{empty} `{stat_tuple[0]}/{stat_tuple[1]}`"

async def setup(bot):
    await bot.add_cog(StatsCommand(bot))
