import discord
from discord import app_commands
from discord.ext import commands
import os
import json
from data_loader import load_pokemon_data
from emojis import get_type_emoji

# Resolve the absolute path to the current script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use absolute paths for Pokémon data directories
POKEMON_NEW_DIRECTORY = os.path.join(BASE_DIR, "../Data/pokemon_new")
POKEMON_OLD_DIRECTORY = os.path.join(BASE_DIR, "../Data/pokemon_old")

# Character storage directory
CHARACTERS_DIR = os.path.join(BASE_DIR, "../characters/")

if not os.path.exists(CHARACTERS_DIR):
    os.makedirs(CHARACTERS_DIR)


class IncrementStatButton(discord.ui.Button):
    """A button for incrementing a specific stat."""
    def __init__(self, stat_name: str, parent_view: "StatDistributionView"):
        super().__init__(label=f"+ {stat_name.title()}", style=discord.ButtonStyle.green)
        self.stat_name = stat_name
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.remaining_points <= 0:
            await interaction.response.send_message(
                content=f"You have already allocated all available stat points for **{self.parent_view.character_data['name']}**.",
                ephemeral=True
            )
            return

        if self.parent_view.character_data["stats"][self.stat_name] >= 5:
            await interaction.response.send_message(
                content=f"**{self.stat_name.title()}** is already at its maximum value (5).",
                ephemeral=True
            )
            return

        # Increment the stat and decrease the remaining points
        self.parent_view.character_data["stats"][self.stat_name] += 1
        self.parent_view.remaining_points -= 1

        # Save changes to the JSON file
        with open(self.parent_view.filepath, "w") as file:
            json.dump(self.parent_view.character_data, file, indent=4)

        await self.parent_view.update_message(interaction)
        await self.parent_view.update_main_sheet()


class AcceptStatButton(discord.ui.Button):
    """A button to confirm and save the stat distribution."""
    def __init__(self, parent_view: "StatDistributionView"):
        super().__init__(label="Accept", style=discord.ButtonStyle.success)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        # Save final stats to the JSON file (already updated in real-time)
        with open(self.parent_view.filepath, "w") as file:
            json.dump(self.parent_view.character_data, file, indent=4)

        # Update the main message to reflect the finalized state
        await self.parent_view.update_main_sheet()

        # Confirm to the user that everything is finalized
        await interaction.response.edit_message(
            content=f"Stat allocation for **{self.parent_view.character_data['name']}** has been finalized and saved!",
            view=None  # Disable the view
        )


class StatDistributionView(discord.ui.View):
    """Interactive view for stat distribution."""
    def __init__(self, character_data, filepath, main_message, remaining_points):
        super().__init__()
        self.character_data = character_data
        self.filepath = filepath
        self.main_message = main_message  # Reference to the main message for updating
        self.remaining_points = remaining_points
        self.create_buttons()

    async def update_message(self, interaction: discord.Interaction):
        """Update the ephemeral message with the current stats and remaining points."""
        stats = self.character_data["stats"]
        stats_display = (
            f"```HP: {stats['hp']} \n"
            f"Willpower: {stats['willpower']}\n\n"
            f"Strength:  {stats['strength']} | {'⬤' * stats['strength']} {'⭘' * (5 - stats['strength'])}\n"
            f"Dexterity: {stats['dexterity']} | {'⬤' * stats['dexterity']} {'⭘' * (5 - stats['dexterity'])}\n"
            f"Vitality:  {stats['vitality']} | {'⬤' * stats['vitality']} {'⭘' * (5 - stats['vitality'])}\n"
            f"Special:   {stats['special']} | {'⬤' * stats['special']} {'⭘' * (5 - stats['special'])}\n"
            f"Insight:   {stats['insight']} | {'⬤' * stats['insight']} {'⭘' * (5 - stats['insight'])}\n\n"
            f"Defense: {stats['defense']}\n"
            f"Special Defense: {stats['special_defense']}\n"
            f"Active Move Limit: {stats['active_move_limit']}```\n"
            f"{self.remaining_points} Remaining Points.\n"
            f"(You don't have to apply them all at once!)\n"
            f"Only you can see this • Dismiss message"
        )
        await interaction.response.edit_message(content=f":noibat:{self.character_data['name']}\n{stats_display}", view=self)

    async def update_main_sheet(self):
        """Update the main character sheet message."""
        updated_response = (
            f"## <:badge_gold:1119185974149251092> {self.character_data['name']} <:noivern:1179259164611055646> \n"
            f"**Level {self.character_data['level']}** `({self.character_data['experience']} / {self.character_data['experience_to_next_level']})`\n"
            f"{self.character_data['money']} <:poke_coin:1120237132200546304> \n"
            f"### Stats {', '.join([f'{get_type_emoji(t)} {t}' for t in self.character_data['types']])}\n"
            f"```HP: {self.character_data['stats']['hp']}\n"
            f"Willpower: {self.character_data['stats']['willpower']}\n\n"
            f"Strength:  {self.character_data['stats']['strength']} | {'⬤' * self.character_data['stats']['strength']} {'⭘' * (5 - self.character_data['stats']['strength'])}\n"
            f"Dexterity: {self.character_data['stats']['dexterity']} | {'⬤' * self.character_data['stats']['dexterity']} {'⭘' * (5 - self.character_data['stats']['dexterity'])}\n"
            f"Vitality:  {self.character_data['stats']['vitality']} | {'⬤' * self.character_data['stats']['vitality']} {'⭘' * (5 - self.character_data['stats']['vitality'])}\n"
            f"Special:   {self.character_data['stats']['special']} | {'⬤' * self.character_data['stats']['special']} {'⭘' * (5 - self.character_data['stats']['special'])}\n"
            f"Insight:   {self.character_data['stats']['insight']} | {'⬤' * self.character_data['stats']['insight']} {'⭘' * (5 - self.character_data['stats']['insight'])}\n\n"
            f"Defense: {self.character_data['stats']['defense']}\n"
            f"Special Defense: {self.character_data['stats']['special_defense']}\n"
            f"Active Move Limit: {self.character_data['stats']['active_move_limit']}```\n"
            f"### Abilities \n"
            f"- {self.character_data['abilities'][0]}\n"
            f"- {self.character_data['abilities'][1]}\n"
            f"### Terastallization Charges\n"
            f"- `1/1` <:type_water:1118594885344297062> Water\n"
            f"### Statistics\n"
            f"🎒 Backpack Slots: {self.character_data['statistics']['backpack_slots']}\n\n"
            f"🏆 Completed Quests: {self.character_data['statistics']['completed_quests']}\n"
            f"🤺 Total Sparring Sessions: {self.character_data['statistics']['sparring_sessions']}"
        )
        await self.main_message.edit(content=updated_response)

    def create_buttons(self):
        """Create increment buttons for each stat."""
        for stat in ["strength", "dexterity", "vitality", "special", "insight"]:
            self.add_item(IncrementStatButton(stat, self))
        self.add_item(AcceptStatButton(self))


class PermanentSheetView(discord.ui.View):
    """View for the permanent sheet with a button for stat distribution."""
    def __init__(self, character_data, filepath, main_message):
        super().__init__()
        self.character_data = character_data
        self.filepath = filepath
        self.main_message = main_message

        # Calculate remaining points dynamically
        self.remaining_points = (
            4 + self.character_data["level"] - 1 - sum(
                self.character_data["stats"][stat] - 1
                for stat in ["strength", "dexterity", "vitality", "special", "insight"]
            )
        )

        if self.remaining_points > 0:
            self.add_item(self.StatDistributionButton(self))

    class StatDistributionButton(discord.ui.Button):
        """Button to open the stat distribution view."""
        def __init__(self, parent_view: "PermanentSheetView"):
            super().__init__(label="Distribute Stats", style=discord.ButtonStyle.blurple)
            self.parent_view = parent_view

        async def callback(self, interaction: discord.Interaction):
            """Callback to show the stat distribution view."""
            view = StatDistributionView(
                self.parent_view.character_data,
                self.parent_view.filepath,
                self.parent_view.main_message,
                remaining_points=self.parent_view.remaining_points
            )
            await interaction.response.send_message(
                content=f":noibat:{self.parent_view.character_data['name']}\n"
                        f"Click buttons below to distribute your points!",
                view=view,
                ephemeral=True
            )


class CreateCharacterCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def autocomplete_pokemon(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete Pokémon species names."""
        pokemon_names = []
        if os.path.exists(POKEMON_NEW_DIRECTORY):
            pokemon_names.extend(
                f[:-5] for f in os.listdir(POKEMON_NEW_DIRECTORY) if f.endswith(".json")
            )
        if os.path.exists(POKEMON_OLD_DIRECTORY):
            pokemon_names.extend(
                f[:-5] for f in os.listdir(POKEMON_OLD_DIRECTORY)
                if f.endswith(".json") and f[:-5] not in pokemon_names
            )

        sorted_names = sorted(pokemon_names)

        return [
            app_commands.Choice(name=name, value=name)
            for name in sorted_names
            if current.lower() in name.lower()
        ][:25]  # Limit to 25 choices as per Discord's restrictions

    async def autocomplete_gender(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete gender options."""
        genders = ["Male", "Female", "Genderless"]
        return [
            app_commands.Choice(name=gender, value=gender)
            for gender in genders
            if current.lower() in gender.lower()
        ]

    @app_commands.command(
        name="create_character",
        description="Create a new character with custom parameters."
    )
    @app_commands.autocomplete(
        pokemon_species=autocomplete_pokemon, gender=autocomplete_gender
    )
    async def create_character(
        self,
        interaction: discord.Interaction,
        player: discord.Member,
        name: str,
        pokemon_species: str,
        gender: str,
        is_shiny: bool = False,
        exp: int = 0,
        money: int = 500
    ):
        """Create a character for a specified player."""
        user_id = player.id
        guild_id = interaction.guild.id

        character_file = os.path.join(CHARACTERS_DIR, f"{user_id}_{guild_id}_{name.lower()}.json")

        if os.path.exists(character_file):
            await interaction.response.send_message(content=f"A character named **{name}** already exists for {player.mention} in this server.", ephemeral=True)
            return

        data = load_pokemon_data(pokemon_species)
        if data is None:
            await interaction.response.send_message(content=f"Unable to find Pokémon data for **{pokemon_species}**, sorry!", ephemeral=True)
            return

        level = exp // 100 + 1
        character_data = {
            "id": user_id,
            "user_id": user_id,
            "guild_id": guild_id,
            "name": name,
            "level": level,
            "experience": exp % 100,
            "experience_to_next_level": 100,
            "money": money,
            "types": data["type"],
            "gender": gender,
            "is_shiny": is_shiny,
            "stats": {
                "hp": data["base_hp"],
                "willpower": 3,
                "strength": 1,
                "dexterity": 2,
                "vitality": 1,
                "special": 1,
                "insight": 1,
                "defense": 1,
                "special_defense": 1,
                "active_move_limit": 3
            },
            "abilities": data["abilities"][:2],
            "statistics": {
                "backpack_slots": 6,
                "completed_quests": 0,
                "sparring_sessions": 0
            }
        }

        with open(character_file, "w") as file:
            json.dump(character_data, file, indent=4)

        response = (
            f"## <:badge_gold:1119185974149251092> {character_data['name']} <:noivern:1179259164611055646> \n"
            f"**Level {character_data['level']}** `({character_data['experience']} / {character_data['experience_to_next_level']})`\n"
            f"{character_data['money']} <:poke_coin:1120237132200546304> \n"
            f"### Stats {', '.join([f'{get_type_emoji(t)} {t}' for t in character_data['types']])}\n"
            f"```HP: {character_data['stats']['hp']}\n"
            f"Willpower: {character_data['stats']['willpower']}\n\n"
            f"Strength:  {character_data['stats']['strength']} | {'⬤' * character_data['stats']['strength']} {'⭘' * (5 - character_data['stats']['strength'])}\n"
            f"Dexterity: {character_data['stats']['dexterity']} | {'⬤' * character_data['stats']['dexterity']} {'⭘' * (5 - character_data['stats']['dexterity'])}\n"
            f"Vitality:  {character_data['stats']['vitality']} | {'⬤' * character_data['stats']['vitality']} {'⭘' * (5 - character_data['stats']['vitality'])}\n"
            f"Special:   {character_data['stats']['special']} | {'⬤' * character_data['stats']['special']} {'⭘' * (5 - character_data['stats']['special'])}\n"
            f"Insight:   {character_data['stats']['insight']} | {'⬤' * character_data['stats']['insight']} {'⭘' * (5 - character_data['stats']['insight'])}\n\n"
            f"Defense: {character_data['stats']['defense']}\n"
            f"Special Defense: {character_data['stats']['special_defense']}\n"
            f"Active Move Limit: {character_data['stats']['active_move_limit']}```\n"
            f"### Abilities \n"
            f"- {character_data['abilities'][0]}\n"
            f"- {character_data['abilities'][1]}\n"
            f"### Terastallization Charges\n"
            f"- `1/1` <:type_water:1118594885344297062> Water\n"
            f"### Statistics\n"
            f"🎒 Backpack Slots: {character_data['statistics']['backpack_slots']}\n\n"
            f"🏆 Completed Quests: {character_data['statistics']['completed_quests']}\n"
            f"🤺 Total Sparring Sessions: {character_data['statistics']['sparring_sessions']}"
        )

        main_message = await interaction.channel.send(response)
        view = PermanentSheetView(character_data, character_file, main_message)
        await main_message.edit(view=view)


async def setup(bot):
    """Load the cog."""
    await bot.add_cog(CreateCharacterCommand(bot))
