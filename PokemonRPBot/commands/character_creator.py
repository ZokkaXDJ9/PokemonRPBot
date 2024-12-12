import discord
from discord import app_commands
from discord.ext import commands
from data_loader import load_pokemon_data

class CharacterCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="character_creator",
        description="Guides you through character creation step-by-step."
    )
    async def character_creator(self, interaction: discord.Interaction):
        """Guides the user through character creation."""
        
        # Function to validate user responses
        def check_response(message):
            return message.author == interaction.user and message.channel == interaction.channel

        # Start of the command
        await interaction.response.send_message(
            "🌟 Welcome to Character Creation! 🌟\nLet's create your character step-by-step."
        )
        character = {}

        # Step 1: Name
        await interaction.channel.send("What is your character's name?")
        name_msg = await self.bot.wait_for("message", check=check_response)
        character["Name"] = name_msg.content.strip()

        # Step 2: Species
        while True:
            await interaction.channel.send("What Pokémon species will your character be?")
            species_msg = await self.bot.wait_for("message", check=check_response)
            character["Species"] = species_msg.content.strip()

            # Load Pokémon data
            pokemon_data = load_pokemon_data(character["Species"])
            if pokemon_data is not None:
                break
            else:
                await interaction.channel.send(
                    f"Pokémon species **{character['Species']}** not found. Please try again."
                )

        # Step 3: Pronouns
        await interaction.channel.send("What pronouns should others use for your character?")
        pronouns_msg = await self.bot.wait_for("message", check=check_response)
        character["Pronouns"] = pronouns_msg.content.strip()

        # Step 4: Size and Weight (User Input)
        while True:
            await interaction.channel.send(
                "Enter your character's size (e.g., 1m) and weight (e.g., 10kg). Separate them with a comma."
            )
            size_weight_msg = await self.bot.wait_for("message", check=check_response)
            try:
                size, weight = size_weight_msg.content.split(",")
                character["Size"] = size.strip()
                character["Weight"] = weight.strip()
                break
            except ValueError:
                await interaction.channel.send(
                    "Invalid input. Please provide size and weight separated by a comma (e.g., 1m, 10kg)."
                )

        # Step 5: Nature
        await interaction.channel.send("What is your character's nature? (Optional, e.g., Brave, Calm)")
        nature_msg = await self.bot.wait_for("message", check=check_response)
        character["Nature"] = nature_msg.content.strip() or "Not specified"

        # Step 6: Sexuality
        await interaction.channel.send("What is your character's sexuality? (Optional)")
        sexuality_msg = await self.bot.wait_for("message", check=check_response)
        character["Sexuality"] = sexuality_msg.content.strip() or "Not specified"

        # Step 7: Extract Abilities
        abilities = [pokemon_data["Ability1"], pokemon_data["Ability2"], pokemon_data.get("HiddenAbility")]
        character["Abilities"] = "\n".join(f"- {ability}" for ability in abilities if ability)

        # Step 8: Extract Bronze Moves
        bronze_moves = [
            move["Name"] for move in pokemon_data["Moves"]
            if move["Learned"] in {"Starter", "Beginner"}
        ]
        character["Unlocked Moves"] = "\n".join(f"- {move}" for move in bronze_moves)

        # Step 9: Egg Moves
        egg_moves = [
            move["Name"] for move in pokemon_data["Moves"]
            if move["Learned"] == "Egg"
        ]
        if egg_moves:
            await interaction.channel.send(
                f"The following Egg moves are available for **{character['Species']}**:\n"
                + "\n".join(f"{idx + 1}. {move}" for idx, move in enumerate(egg_moves))
                + "\nPlease select one by typing its number:"
            )

            while True:
                egg_move_msg = await self.bot.wait_for("message", check=check_response)
                try:
                    selected_index = int(egg_move_msg.content.strip()) - 1
                    if 0 <= selected_index < len(egg_moves):
                        character["Egg Move"] = egg_moves[selected_index]
                        break
                    else:
                        await interaction.channel.send("Invalid choice. Please enter a valid number.")
                except ValueError:
                    await interaction.channel.send("Invalid input. Please enter a number corresponding to the Egg move.")
        else:
            character["Egg Move"] = "None"

        # Step 10: Items (Static Starting Inventory)
        character["Items"] = [
            "Apple",
            "Oran Berry",
            "Oran Berry",
            "1 Stun Seed",
            "1 Sleep Seed",
            "1 Lucky Egg",
        ]

        # Step 11: Display the Completed Character Sheet
        character_sheet = f"""
**Name:** {character['Name']}
**Team:** (Leave this blank for now)
**Species:** {character['Species']}
**Size:** {character['Size']}
**Weight:** {character['Weight']}
**Gender & Pronouns:** {character['Pronouns']}
**Nature:** {character['Nature']}
**Sexuality:** {character['Sexuality']}
## Abilities
{character['Abilities']}
## Unlocked Moves
{character['Unlocked Moves']}
## Egg Move
- {character['Egg Move']}
## Items
### Inventory (6 slots):
- {"\n- ".join(character['Items'])}
        """

        await interaction.channel.send(
            "🎉 Here is your completed character sheet:\n```" + character_sheet + "```"
        )

# Setup function to register the Cog
async def setup(bot):
    await bot.add_cog(CharacterCreator(bot))
