import discord
from discord import app_commands
from helpers import get_database, load_pokemon_stats
from datetime import datetime

class CreateCharacterCommand(app_commands.Command):
    def __init__(self):
        super().__init__(
            name="create_character",
            description="Create a new character for a user.",
            callback=self.callback,
        )

    async def callback(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        name: str,
        pokemon_species: str,
        is_shiny: bool = False,
        phenotype: str = "genderless",
        experience: int = 0,
        money: int = 500
    ):
        db = get_database()
        
        # Validate user input for name length, etc.
        if len(name) > 30:
            await interaction.response.send_message("Character name too long.", ephemeral=True)
            return
        
        # Check if character already exists
        if db.get_character(name, interaction.guild_id):
            await interaction.response.send_message("Character name already exists.", ephemeral=True)
            return

        # Load Pokémon stats
        pokemon_data = load_pokemon_stats(pokemon_species)
        if not pokemon_data:
            await interaction.response.send_message("Invalid Pokémon species.", ephemeral=True)
            return
        
        # Set phenotype code
        phenotype_map = {"male": 1, "female": 2, "genderless": 3}
        phenotype_code = phenotype_map.get(phenotype.lower(), 3)

        # Create stat message placeholder
        stat_message = await interaction.channel.send("[Stat Placeholder]")

        # Insert new character in the database
        db.create_character(
            user_id=user.id,
            guild_id=interaction.guild_id,
            name=name,
            pokemon_species_id=pokemon_data["poke_api_id"],
            is_shiny=is_shiny,
            phenotype=phenotype_code,
            experience=experience,
            money=money,
            stat_message_id=stat_message.id,
            stat_channel_id=interaction.channel_id,
            creation_date=datetime.utcnow().date().isoformat(),
        )
        
        await interaction.response.send_message("Character created successfully!", ephemeral=True)
        db.close()
