import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import re

# ------------------------------
# Helper functions & constants
# ------------------------------

def normalize_name(name: str) -> str:
    """
    Converts a Pokémon (or ability) name to a normalized form:
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

def find_movelist_filename(normalized: str, folder: str = os.path.join("data", "movelists")) -> str:
    """
    Given a normalized Pokémon name, returns the full filename of the movelist JSON file.
    It first checks for an exact match; if not found, it attempts a fuzzy match.
    """
    exact_path = os.path.join(folder, f"{normalized}.json")
    if os.path.exists(exact_path):
        return exact_path

    target_nohyphen = normalized.replace("-", "")
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            candidate = filename[:-5]  # remove .json extension
            candidate_norm = normalize_name(candidate)
            candidate_nohyphen = candidate_norm.replace("-", "")
            if candidate_nohyphen == target_nohyphen:
                return os.path.join(folder, filename)
            # Extra fuzzy check: one is a substring of the other.
            if candidate_nohyphen in target_nohyphen or target_nohyphen in candidate_nohyphen:
                return os.path.join(folder, filename)
    return None

def format_stat_bar(stat: str) -> str:
    """
    Given a stat string (e.g. "3/6"), returns a visual representation such as "⬤⬤⬤⭘⭘⭘".
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
    Joins a list of moves with a separator. Returns 'None' if the list is empty.
    """
    return "  |  ".join(moves_list) if moves_list else "None"

# A simple mapping for type emojis (add more as needed)
TYPE_EMOJIS = {
    "Psychic": "<:typepsychic:1272535970897592330>",
    # Example:
    # "Fire": "<:typefire:123456789012345678>",
    # "Water": "<:typewater:123456789012345678>",
}

# ------------------------------
# View classes for interactions
# ------------------------------

class LearnMovesView(discord.ui.View):
    """
    This view displays a button to show all learnable moves (TM, Egg, Tutor moves)
    exactly like your /learns command.
    """
    def __init__(self, pokemon_data: dict, author: discord.User):
        super().__init__(timeout=180)
        self.pokemon_data = pokemon_data
        self.author = author

    @discord.ui.button(label="Show all learnable Moves", style=discord.ButtonStyle.primary)
    async def show_all_moves(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You did not invoke this command.", ephemeral=True)
            return

        # Disable the button once pressed.
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        header = f"### {self.pokemon_data.get('name', 'Unknown')} [#{self.pokemon_data.get('number', '?')}]"
        moves = self.pokemon_data.get("moves", {})

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
            await interaction.followup.send(msg, ephemeral=False)

class PokemonView(discord.ui.View):
    """
    This view displays interactive buttons for a Pokémon's details:
    - Abilities (loads ability data from the abilities folder)
    - Type Effectiveness (placeholder for now)
    - Moves (displays rank moves exactly as in the /learns command and attaches LearnMovesView)
    """
    def __init__(self, pokemon_data: dict, invoker: discord.User):
        super().__init__(timeout=180)
        self.pokemon_data = pokemon_data
        self.invoker = invoker

    def load_ability(self, ability_name: str, folder: str = os.path.join("data", "abilities")) -> dict:
        """
        Loads an ability's JSON file (if it exists) from the abilities folder.
        """
        normalized = normalize_name(ability_name)
        file_path = os.path.join(folder, f"{normalized}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading ability {ability_name}: {e}")
        return None

    @discord.ui.button(label="Abilities", style=discord.ButtonStyle.primary)
    async def abilities_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Restrict interaction to the invoking user.
        if interaction.user.id != self.invoker.id:
            await interaction.response.send_message("You did not invoke this command.", ephemeral=True)
            return

        abilities = self.pokemon_data.get("abilities", {})
        message = f"## {self.pokemon_data.get('name', 'Unknown')} Abilities\n"
        
        # Normal abilities:
        for ability in abilities.get("normal", []):
            ability_data = self.load_ability(ability)
            message += f"\n### {ability}\n"
            if ability_data:
                message += f"{ability_data.get('effect', 'No effect description.')}\n"
                message += f"*{ability_data.get('description', 'No detailed description.')}*\n"
            else:
                message += "No data found for this ability.\n"
        
        # Hidden abilities:
        for ability in abilities.get("hidden", []):
            ability_data = self.load_ability(ability)
            message += f"\n### {ability} (Hidden)\n"
            if ability_data:
                message += f"{ability_data.get('effect', 'No effect description.')}\n"
                message += f"*{ability_data.get('description', 'No detailed description.')}*\n"
            else:
                message += "No data found for this ability.\n"
        
        await interaction.response.send_message(message, ephemeral=False)

    @discord.ui.button(label="Type Effectiveness", style=discord.ButtonStyle.primary)
    async def type_effectiveness_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Restrict interaction to the invoking user.
        if interaction.user.id != self.invoker.id:
            await interaction.response.send_message("You did not invoke this command.", ephemeral=True)
            return
        
        types_list = self.pokemon_data.get("types", [])
        # Placeholder for type effectiveness.
        effectiveness_message = f"Type effectiveness for {', '.join(types_list)} is not implemented yet."
        await interaction.response.send_message(effectiveness_message, ephemeral=False)

    @discord.ui.button(label="Moves", style=discord.ButtonStyle.primary)
    async def moves_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Restrict interaction to the invoking user.
        if interaction.user.id != self.invoker.id:
            await interaction.response.send_message("You did not invoke this command.", ephemeral=True)
            return
    
        # Build header and rank move sections as in the /learns command.
        header = f"### {self.pokemon_data.get('name', 'Unknown')} [#{self.pokemon_data.get('number', '?')}]"
        moves = self.pokemon_data.get("moves", {})

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

        # Attach the LearnMovesView as a button for showing TM, Egg and Tutor moves.
        view = LearnMovesView(pokemon_data=self.pokemon_data, author=interaction.user)
        await interaction.response.send_message(initial_text, view=view)

# ------------------------------
# The main Pokémon cog
# ------------------------------

class PokemonCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pokemon", description="Show details for a Pokémon")
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
        output = f"### {data.get('name', 'Unknown')} [#{data.get('number', '?')}]\n"
        # Optionally include height/weight if available.
        if all(key in data for key in ("height_m", "height_ft", "weight_kg", "weight_lb")):
            output += f"{data['height_m']}m / {data['height_ft']}ft   |   {data['weight_kg']}kg / {data['weight_lb']}lbs\n"
        else:
            output += "\n"
        # Display type(s) using emoji mapping if available.
        types_list = data.get("types", [])
        type_str = " / ".join([f"{TYPE_EMOJIS.get(t, '')} {t}".strip() for t in types_list])
        output += f"**Type**: {type_str}\n"

        # Display Base HP and stat bars.
        output += f"**Base HP**: {data.get('base_hp', '?')}\n"
        output += f"**Strength**: {format_stat_bar(data.get('strength', ''))} `{data.get('strength', '')}`\n"
        output += f"**Dexterity**: {format_stat_bar(data.get('dexterity', ''))} `{data.get('dexterity', '')}`\n"
        output += f"**Vitality**: {format_stat_bar(data.get('vitality', ''))} `{data.get('vitality', '')}`\n"
        output += f"**Special**: {format_stat_bar(data.get('special', ''))} `{data.get('special', '')}`\n"
        output += f"**Insight**: {format_stat_bar(data.get('insight', ''))} `{data.get('insight', '')}`\n"

        # Format abilities (normal and hidden).
        abilities = data.get("abilities", {})
        normal_abilities = abilities.get("normal", [])
        hidden_abilities = abilities.get("hidden", [])
        abilities_str = " / ".join(normal_abilities)
        if hidden_abilities:
            abilities_str += " (" + " / ".join(hidden_abilities) + ")"
        output += f"**Ability**: {abilities_str}\n"

        # Create a view instance and send the message.
        view = PokemonView(pokemon_data=data, invoker=interaction.user)
        await interaction.response.send_message(output, view=view)

    @pokemon.autocomplete("pokemon")
    async def pokemon_autocomplete(self, interaction: discord.Interaction, current: str):
        """
        Returns autocomplete suggestions by scanning the movelists folder for JSON files
        whose names include the current input.
        """
        suggestions = []
        folder = os.path.join("data", "movelists")
        if not os.path.exists(folder):
            return suggestions

        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                pokemon_name = filename[:-5]  # Remove the .json extension.
                if current.lower() in pokemon_name.lower():
                    suggestions.append(app_commands.Choice(name=pokemon_name, value=pokemon_name))
                    if len(suggestions) >= 25:
                        break
        return suggestions

# ------------------------------
# Cog setup
# ------------------------------

async def setup(bot: commands.Bot):
    await bot.add_cog(PokemonCog(bot))