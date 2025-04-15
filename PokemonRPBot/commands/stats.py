import math
import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import re

from emojis import get_type_emoji

# ------------------------------
# Helper functions & constants
# ------------------------------

def normalize_name(name: str) -> str:
    """
    Converts a Pokémon name to a normalized form:
      - Lowercase
      - Replace non-alphanumeric characters with hyphens
      - Merge multiple hyphens and trim leading/trailing hyphens.
    Example: "Sirfetch'd" → "sirfetch-d"
    """
    normalized = name.lower()
    normalized = re.sub(r'[^a-z0-9]', '-', normalized)
    normalized = re.sub(r'-+', '-', normalized)
    normalized = normalized.strip('-')
    return normalized

def load_defensive_chart():
    r"""
    Load the defensive type interaction chart from a JSON file.
    The JSON file is located at:
    PokemonRPBot/PokemonRPBot/Data/typechart.json
    """
    file_path = os.path.join(os.path.dirname(__file__), "..", "Data", "typechart.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
DEFENSIVE_CHART = load_defensive_chart()

def normalize_type(t: str) -> str:
    """
    Normalize the input type string to match one of the keys in DEFENSIVE_CHART.
    This function compares the lowercase of the input to the lowercase of each key
    and returns the properly cased key if found. Otherwise, it returns the input.
    """
    t_normalized = t.lower()
    for key in DEFENSIVE_CHART.keys():
        if key.lower() == t_normalized:
            return key
    return t

def get_effectiveness_category(multiplier: float) -> str:
    """
    Convert the combined multiplier into a text category using base-2 logarithms:
      - log₂(4) = 2    → "Super Effective (+2)"
      - log₂(2) = 1    → "Effective (+1)"
      - log₂(0.5) = -1 → "Ineffective (-1)"
      - log₂(0.25) = -2→ "Super Ineffective (-2)"
      - 0 multiplier  → "Immune (No Damage)"
    """
    if multiplier == 0:
        return "Immune (No Damage)"
    shift = round(math.log(multiplier, 2))
    if shift == 0:
        return "Neutral (0)"
    elif shift == 1:
        return "Effective (+1)"
    elif shift == 2:
        return "Super Effective (+2)"
    elif shift == -1:
        return "Ineffective (-1)"
    elif shift == -2:
        return "Super Ineffective (-2)"
    elif shift > 2:
        return f"Ultra Effective (+{shift})"
    elif shift < -2:
        return f"Ultra Ineffective ({shift})"
    return f"Multiplier {multiplier}"

def sort_key(category: str) -> float:
    """
    Extract a numeric key from the category string by searching for the numeric value
    within parentheses (e.g., '(+2)'). "Immune (No Damage)" is forced to a low value.
    """
    if category == "Immune (No Damage)":
        return -999
    m = re.search(r'\(([-+]\d+)\)', category)
    if m:
        return int(m.group(1))
    return 0

def find_movelist_filename(normalized: str, folder: str = os.path.join("data", "movelists")) -> str:
    """
    Given a normalized Pokémon name, returns the full filename of the movelist JSON file.
    Checks for an exact match first, then does a fuzzy check.
    """
    exact_path = os.path.join(folder, f"{normalized}.json")
    if os.path.exists(exact_path):
        return exact_path

    target_nohyphen = normalized.replace("-", "")
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            candidate = filename[:-5]  # Remove .json extension
            candidate_norm = normalize_name(candidate)
            candidate_nohyphen = candidate_norm.replace("-", "")
            if candidate_nohyphen == target_nohyphen:
                return os.path.join(folder, filename)
            if candidate_nohyphen in target_nohyphen or target_nohyphen in candidate_nohyphen:
                return os.path.join(folder, filename)
    return None

def format_stat_bar(stat: str) -> str:
    """
    Given a stat string (e.g. "3/6"), returns a visual bar (like "⬤⬤⬤⭘⭘⭘").
    """
    try:
        filled, total = stat.split('/')
        filled = int(filled)
        total = int(total)
        return "⬤" * filled + "⭘" * (total - filled)
    except Exception:
        return stat

def format_moves(moves_list: list) -> str:
    """
    Joins a list of moves with "  |  " or returns "None" if empty.
    """
    return "  |  ".join(moves_list) if moves_list else "None"

# A mapping for type emojis.
TYPE_EMOJIS = {
    "Psychic": "<:typepsychic:1272535970897592330>",
    # Add more as needed.
}

# Load ability data exactly by its given name (no normalization)
def load_ability(ability_name: str, folder: str = None) -> dict:
    if folder is None:
        folder = os.path.join(os.path.dirname(__file__), "..", "Data", "abilities")
    file_path = os.path.join(folder, f"{ability_name}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading ability {ability_name}: {e}")
    return None


# ------------------------------
# Persistent view classes (no user check)
# ------------------------------
# Each button’s custom_id encodes the Pokémon’s normalized name.
# Format: "pokemon:<action>:<normalized>"
# (We no longer restrict by invoker.)

class PersistentPokemonAbilitiesButton(discord.ui.Button):
    def __init__(self, normalized: str):
        custom_id = f"pokemon:abilities:{normalized}"
        super().__init__(label="Abilities", style=discord.ButtonStyle.primary, custom_id=custom_id)
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        try:
            _, action, normalized = self.custom_id.split(":")
        except Exception:
            await interaction.followup.send("Internal error in button data.")
            return

        folder = os.path.join("data", "movelists")
        filename = find_movelist_filename(normalized, folder)
        if not filename:
            await interaction.followup.send("Could not find Pokémon data.")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            await interaction.followup.send("Error loading Pokémon data.")
            return

        abilities = data.get("abilities", {})
        message = f"## {data.get('name', 'Unknown')} Abilities\n"
        for ability in abilities.get("normal", []):
            ability_data = load_ability(ability)
            message += f"\n### {ability}\n"
            if ability_data:
                message += f"{ability_data.get('effect', 'No effect description.')}\n"
                message += f"*{ability_data.get('description', 'No detailed description.')}*\n"
            else:
                message += "No data found for this ability.\n"
        for ability in abilities.get("hidden", []):
            ability_data = load_ability(ability)
            message += f"\n### {ability} (Hidden)\n"
            if ability_data:
                message += f"{ability_data.get('effect', 'No effect description.')}\n"
                message += f"*{ability_data.get('description', 'No detailed description.')}*\n"
            else:
                message += "No data found for this ability.\n"
        await interaction.followup.send(message)

class PersistentPokemonTypeEffectivenessButton(discord.ui.Button):
    def __init__(self, normalized: str):
        custom_id = f"pokemon:te:{normalized}"
        super().__init__(label="Type Effectiveness", style=discord.ButtonStyle.primary, custom_id=custom_id)
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        
        try:
            _, action, normalized = self.custom_id.split(":")
        except Exception:
            await interaction.followup.send("Internal error in button data.")
            return

        folder = os.path.join("data", "movelists")
        filename = find_movelist_filename(normalize_name(normalized), folder)
        if not filename:
            await interaction.followup.send("Could not find Pokémon data.")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            await interaction.followup.send("Error loading Pokémon data.")
            return
        
        # Retrieve the Pokémon's name and its types from the JSON data.
        pokemon_name = data.get("name", "Unknown")
        defender_types = data.get("types", [])
        defender_types = [normalize_type(t) for t in defender_types]
        
        # Calculate overall effectiveness for each attacking type.
        results = {}
        for attack_type in DEFENSIVE_CHART.keys():
            multiplier = 1.0
            for def_type in defender_types:
                multiplier *= DEFENSIVE_CHART[def_type][attack_type]
            if multiplier == 1:
                continue
            category = get_effectiveness_category(multiplier)
            if category == "Neutral (0)":
                continue
            results.setdefault(category, []).append(attack_type)
        
        # Sort the categories using their numeric value (extracted from the category string)
        sorted_categories = sorted(results.keys(), key=sort_key, reverse=True)
        
        # Build a plain text message with a header containing the Pokémon's name.
        message_lines = [f"## Type Chart for {pokemon_name}"]
        for category in sorted_categories:
            types_list = results[category]
            types_str = "  |  ".join(f"{get_type_emoji(t)} {t}" for t in types_list)
            message_lines.append(f"### {category}")
            message_lines.append(types_str)
        
        message = "\n".join(message_lines)
        await interaction.followup.send(message)

class PersistentPokemonMovesButton(discord.ui.Button):
    def __init__(self, normalized: str):
        custom_id = f"pokemon:moves:{normalized}"
        super().__init__(label="Moves", style=discord.ButtonStyle.primary, custom_id=custom_id)
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        try:
            _, action, normalized = self.custom_id.split(":")
        except Exception:
            await interaction.followup.send("Internal error in button data.")
            return

        folder = os.path.join("data", "movelists")
        filename = find_movelist_filename(normalized, folder)
        if not filename:
            await interaction.followup.send("Could not find Pokémon data.")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            await interaction.followup.send("Error loading Pokémon data.")
            return

        header = f"### {data.get('name', 'Unknown')} [#{data.get('number', '?')}]"
        moves = data.get("moves", {})
        bronze_moves = format_moves(moves.get("bronze", []))
        silver_moves = format_moves(moves.get("silver", []))
        gold_moves = format_moves(moves.get("gold", []))
        platinum_moves = format_moves(moves.get("platinum", []))
        rank_sections = []
        rank_data = [
            ("<:badgebronze:1272532685197152349> **Bronze**", bronze_moves),
            ("<:badgesilver:1272533590697185391> **Silver**", silver_moves),
            ("<:badgegold:1272532681992962068> **Gold**", gold_moves),
            ("<:badgeplatinum:1272533593750507570> **Platinum**", platinum_moves)
        ]
        for rank_title, moves_text in rank_data:
            if moves_text != "None":
                rank_sections.append(f"{rank_title}\n{moves_text}")
    
        initial_text = header
        if rank_sections:
            initial_text += "\n\n" + "\n\n".join(rank_sections)
    
        # Attach the persistent learn moves view.
        view = PersistentLearnMovesView(normalized)
        await interaction.followup.send(initial_text, view=view)

class PersistentLearnMovesView(discord.ui.View):
    """
    A persistent view with a single button "Show all learnable Moves"
    that expands the move list (TM, Egg, Tutor moves).
    """
    def __init__(self, normalized: str):
        super().__init__(timeout=None)
        self.normalized = normalized
        custom_id = f"pokemon:learnmoves:{normalized}"
        button = discord.ui.Button(label="Show all learnable Moves", style=discord.ButtonStyle.primary, custom_id=custom_id)
        button.callback = self.learn_moves_callback
        self.add_item(button)

    async def learn_moves_callback(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        try:
            _, action, normalized = interaction.data.get("custom_id", "").split(":")
        except Exception:
            await interaction.followup.send("Internal error in button data.")
            return

        folder = os.path.join("data", "movelists")
        filename = find_movelist_filename(normalized, folder)
        if not filename:
            await interaction.followup.send("Could not find Pokémon data.")
            return
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            await interaction.followup.send("Error loading Pokémon data.")
            return

        header = f"### {data.get('name', 'Unknown')} [#{data.get('number', '?')}]"
        moves = data.get("moves", {})
        tm_moves = format_moves(moves.get("tm", []))
        egg_moves = format_moves(moves.get("egg", []))
        tutor_moves = format_moves(moves.get("tutor", []))
        
        sections = [
            (":cd: **TM Moves**", tm_moves),
            (":egg: **Egg Moves**", egg_moves),
            (":teacher: **Tutor Moves**", tutor_moves)
        ]
        messages = []
        current_message = header
        for title, content in sections:
            section_text = f"{title}\n{content}"
            if len(current_message) + 2 + len(section_text) > 2000:
                messages.append(current_message)
                current_message = header + "\n\n" + section_text
            else:
                current_message += "\n\n" + section_text
        messages.append(current_message)
        for msg in messages:
            await interaction.followup.send(msg)

# Bundle the persistent buttons in one persistent view.
class PersistentPokemonView(discord.ui.View):
    def __init__(self, normalized: str):
        super().__init__(timeout=None)
        self.add_item(PersistentPokemonAbilitiesButton(normalized))
        self.add_item(PersistentPokemonTypeEffectivenessButton(normalized))
        self.add_item(PersistentPokemonMovesButton(normalized))

# ------------------------------
# The main Pokémon cog
# ------------------------------

class StatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stats", description="Show details for a Pokémon")
    async def pokemon(self, interaction: discord.Interaction, pokemon: str):
        norm_pokemon = normalize_name(pokemon)
        folder = os.path.join("data", "movelists")
        if not os.path.exists(folder):
            await interaction.response.send_message("Pokémon data folder not found.", ephemeral=True)
            return

        filename = find_movelist_filename(norm_pokemon, folder)
        if not filename:
            await interaction.response.send_message(f"Could not find data for Pokémon **{pokemon}**.", ephemeral=True)
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            await interaction.response.send_message("Error loading the Pokémon data.", ephemeral=True)
            print(f"Error loading {filename}: {e}")
            return

        # Build the Pokémon display message.
        output = f"### {data.get('name', 'Unknown')} [#{data.get('number', '?')}]"
        if all(key in data for key in ("height_m", "height_ft", "weight_kg", "weight_lb")):
            output += f"\n{data['height_m']}m / {data['height_ft']}ft   |   {data['weight_kg']}kg / {data['weight_lb']}lbs"
        else:
            output += "\n"
        types_list = data.get("types", [])
        # Use the imported get_type_emoji function to retrieve each type's emoji.
        type_str = " / ".join([f"{get_type_emoji(t)} {t}" for t in types_list])
        output += f"\n**Type**: {type_str}"
        output += f"\n**Base HP**: {data.get('base_hp', '?')}"
        output += f"\n**Strength**: {format_stat_bar(data.get('strength', ''))} `{data.get('strength', '')}`"
        output += f"\n**Dexterity**: {format_stat_bar(data.get('dexterity', ''))} `{data.get('dexterity', '')}`"
        output += f"\n**Vitality**: {format_stat_bar(data.get('vitality', ''))} `{data.get('vitality', '')}`"
        output += f"\n**Special**: {format_stat_bar(data.get('special', ''))} `{data.get('special', '')}`"
        output += f"\n**Insight**: {format_stat_bar(data.get('insight', ''))} `{data.get('insight', '')}`"
        abilities = data.get("abilities", {})
        normal_abilities = abilities.get("normal", [])
        hidden_abilities = abilities.get("hidden", [])
        abilities_str = " / ".join(normal_abilities)
        if hidden_abilities:
            abilities_str += " (" + " / ".join(hidden_abilities) + ")"
        output += f"\n**Ability**: {abilities_str}"
        view = PersistentPokemonView(norm_pokemon)
        await interaction.response.send_message(output, view=view)
        self.bot.add_view(view)

    @pokemon.autocomplete("pokemon")
    async def pokemon_autocomplete(self, interaction: discord.Interaction, current: str):
        suggestions = []
        folder = os.path.join("data", "movelists")
        if not os.path.exists(folder):
            return suggestions

        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                pokemon_name = filename[:-5]
                if current.lower() in pokemon_name.lower():
                    suggestions.append(app_commands.Choice(name=pokemon_name, value=pokemon_name))
                    if len(suggestions) >= 25:
                        break
        return suggestions

# ------------------------------
# Cog setup
# ------------------------------

async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))
