import discord
from discord import app_commands
from discord.ext import commands
from data_loader import load_pokemon_data, get_additional_moves_from_csv, pokemon_base_data

class LearnsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Autocomplete function to suggest Pokémon names based on CSV data
    async def autocomplete_pokemon(
        self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        pokemon_names = [data["name"] for data in pokemon_base_data.values()]
        suggestions = [
            app_commands.Choice(name=name, value=name)
            for name in sorted(pokemon_names)
            if current.lower() in name.lower()
        ]
        return suggestions[:25]

    @app_commands.command(name="learns", description="Display moves a Pokémon can learn.")
    @app_commands.autocomplete(pokemon_name=autocomplete_pokemon)
    async def learns(self, interaction: discord.Interaction, pokemon_name: str):
        # Load Pokémon data from JSON
        pokemon_data = load_pokemon_data(pokemon_name)
        if not pokemon_data:
            await interaction.response.send_message(
                content=f"Unable to find a Pokémon named **{pokemon_name}**.",
                ephemeral=True
            )
            return

        # Build the basic output text with moves grouped by rank
        learnable_moves_text = f"### {pokemon_name} [#{pokemon_data['number']}]\n"
        for rank, emoji in {
            "Bronze": "<:badgebronze:1272532685197152349>",
            "Silver": "<:badgesilver:1272533590697185391>",
            "Gold": "<:badgegold:1272532681992962068>",
            "Platinum": "<:badgeplatinum:1272533593750507570>",
            "Diamond": "**Diamond**"
        }.items():
            moves = pokemon_data.get("moves", {}).get(rank, [])
            if moves:
                learnable_moves_text += f"{emoji} **{rank}**\n" + " | ".join(moves) + "\n\n"

        # Button to show additional moves
        view = discord.ui.View()
        button = discord.ui.Button(label="Show Additional Moves", style=discord.ButtonStyle.primary)

        # Define the button callback for showing additional moves
        async def show_additional_moves(interaction: discord.Interaction):
            additional_moves = get_additional_moves_from_csv(pokemon_data["number"])
            additional_info = ""
            if additional_moves["TM Moves"]:
                additional_info += f":cd: **TM Moves**\n{' | '.join(additional_moves['TM Moves'])}\n\n"
            if additional_moves["Egg Moves"]:
                additional_info += f":egg: **Egg Moves**\n{' | '.join(additional_moves['Egg Moves'])}\n\n"
            if additional_moves["Tutor"]:
                additional_info += f":teacher: **Tutor**\n{' | '.join(additional_moves['Tutor'])}\n\n"
            if additional_moves["Other"]:
                additional_info += f":question: **Other**\n{' | '.join(additional_moves['Other'])}"

            # Split message if it exceeds the character limit
            message_parts = [additional_info[i:i+2000] for i in range(0, len(additional_info), 2000)]
            for part in message_parts:
                await interaction.followup.send(content=part)

        # Attach the callback and add button to the view
        button.callback = show_additional_moves
        view.add_item(button)

        # Send initial message with the view containing the button
        await interaction.response.send_message(content=learnable_moves_text, view=view)

# Register the cog
async def setup(bot):
    await bot.add_cog(LearnsCommand(bot))
