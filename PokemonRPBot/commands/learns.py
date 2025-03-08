import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# Helper function to join moves with the pipe separator.
def format_moves(moves_list: list) -> str:
    return "  |  ".join(moves_list) if moves_list else "None"

class LearnMovesView(discord.ui.View):
    def __init__(self, pokemon_data: dict, author: discord.User):
        super().__init__(timeout=180)  # timeout in seconds
        self.pokemon_data = pokemon_data
        self.author = author

    @discord.ui.button(label="Show all learnable Moves", style=discord.ButtonStyle.primary)
    async def show_all_moves(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Restrict button usage to the command author.
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You did not invoke this command.", ephemeral=True)
            return

        # Disable the button (grey it out) on the original message.
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        # Prepare header and sections for TM, Egg, and Tutor moves.
        header = f"### {self.pokemon_data.get('name', 'Unknown')} [#{self.pokemon_data.get('number', '?')}]"
        moves = self.pokemon_data.get("moves", {})

        tm_moves = format_moves(moves.get("tm", []))
        egg_moves = format_moves(moves.get("egg", []))
        tutor_moves = format_moves(moves.get("tutor", []))

        # Build each section as a complete unit.
        sections = [
            (":cd: **TM Moves**", tm_moves),
            (":egg: **Egg Moves**", egg_moves),
            (":teacher: **Tutor**", tutor_moves)
        ]

        # Pack sections into messages, ensuring none exceeds 2000 characters.
        messages = []
        current_message = header  # start with header in every message
        for title, content in sections:
            section_text = f"{title}\n{content}"
            # If adding this section would exceed 2000 characters, start a new message.
            if len(current_message) + 2 + len(section_text) > 2000:
                messages.append(current_message)
                current_message = header + "\n\n" + section_text
            else:
                current_message += "\n\n" + section_text
        messages.append(current_message)

        # Send each message as a follow-up reply.
        for msg in messages:
            await interaction.followup.send(msg, ephemeral=False)

class MovesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="learns", description="Show move list info for a Pokémon")
    async def learns(self, interaction: discord.Interaction, pokemon: str):
        """
        Displays a Pokémon’s move list as defined in a JSON file.
        
        The JSON file should be in data/movelists/<pokemon_name>.json with the structure:
        {
          "number": 0,
          "name": "Pokemon Name",
          "moves": {
            "bronze": ["A", "B", "..."],
            "silver": ["A", "B", "..."],
            "gold": ["A", "B", "..."],
            "platinum": ["A", "B", "..."],
            "diamond": [],
            "tm": ["A", "B", "C"],
            "egg": ["D", "E", "F"],
            "tutor": ["G", "H", "I"]
          }
        }
        """
        filename = os.path.join("data", "movelists", f"{pokemon.lower()}.json")
        if not os.path.exists(filename):
            await interaction.response.send_message(f"Could not find data for Pokémon **{pokemon}**.", ephemeral=True)
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            await interaction.response.send_message("Error loading the Pokémon data.", ephemeral=True)
            print(f"Error loading {filename}: {e}")
            return

        moves = data.get("moves", {})
        header = f"### {data.get('name', 'Unknown')} [#{data.get('number', '?')}]"
        bronze_moves = format_moves(moves.get("bronze", []))
        silver_moves = format_moves(moves.get("silver", []))
        gold_moves = format_moves(moves.get("gold", []))
        platinum_moves = format_moves(moves.get("platinum", []))

        # Build the initial message text by including only non-empty rank sections.
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

        view = LearnMovesView(pokemon_data=data, author=interaction.user)
        await interaction.response.send_message(initial_text, view=view)

    @learns.autocomplete("pokemon")
    async def pokemon_autocomplete(self, interaction: discord.Interaction, current: str):
        """
        Autocomplete callback for the 'pokemon' argument.
        It scans the data/movelists/ folder for JSON files and suggests Pokémon names that contain
        the currently typed string.
        """
        suggestions = []
        folder = os.path.join("data", "movelists")
        if not os.path.exists(folder):
            return suggestions

        for filename in os.listdir(folder):
            if filename.endswith(".json"):
                # Remove the .json extension.
                pokemon_name = filename[:-5]
                if current.lower() in pokemon_name.lower():
                    suggestions.append(app_commands.Choice(name=pokemon_name.capitalize(), value=pokemon_name))
                    if len(suggestions) >= 25:
                        break
        return suggestions

# Setup function to add the cog.
async def setup(bot: commands.Bot):
    await bot.add_cog(MovesCog(bot))
