import discord
from discord import app_commands
from discord.ext import commands
from data_loader import load_pokemon_data, get_pokemon_moves, pokemon_base_data

class MoveRanks:
    RANKS = {
        "Bronze": "<:badgebronze:1272532685197152349>",
        "Silver": "<:badgesilver:1272533590697185391>",
        "Gold": "<:badgegold:1272532681992962068>",
        "Platinum": "<:badgeplatinum:1272533593750507570>",
        "Diamond": "<:badgediamond:1272532683431481445>"
    }

    @classmethod
    def get_rank_emoji(cls, rank):
        return cls.RANKS.get(rank, "")


class LearnsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        pokemon_data = load_pokemon_data(pokemon_name)
        if not pokemon_data:
            await interaction.response.send_message(
                content=f"Unable to find a Pokémon named **{pokemon_name}**.",
                ephemeral=True
            )
            return

        # Build the moves display text
        learnable_moves_text = self.build_moves_by_rank(pokemon_name, pokemon_data)

        # Button to show additional moves
        view = discord.ui.View()
        button = discord.ui.Button(label="Show Additional Moves", style=discord.ButtonStyle.primary)
        view.add_item(button)

        # Define and add a callback for the button
        async def button_callback(interaction: discord.Interaction):
            await self.show_additional_moves_callback(interaction, pokemon_data)
        button.callback = button_callback

        await interaction.response.send_message(content=learnable_moves_text, view=view)

    def build_moves_by_rank(self, pokemon_name, pokemon_data):
        """Builds the moves text grouped by rank."""
        moves_text = f"### {pokemon_name} [#{pokemon_data['number']}]\n"
        for rank, emoji in MoveRanks.RANKS.items():
            moves = pokemon_data.get("moves", {}).get(rank, [])
            if moves:
                moves_text += f"{emoji} **{rank}**\n" + " | ".join(moves) + "\n\n"
        return moves_text

    async def show_additional_moves_callback(self, interaction, pokemon_data):
        """Displays all moves for a Pokémon using `get_pokemon_moves`."""
        # Properly defer and handle the follow-up response
        await interaction.response.defer()

        # Use get_pokemon_moves to fetch the full list of moves for this Pokémon
        pokemon_name = pokemon_data["name"]
        message_parts = get_pokemon_moves(pokemon_name)

        # Send each part individually if there are multiple messages
        for part in message_parts:
            await interaction.followup.send(content=part)


# Register the cog
async def setup(bot):
    await bot.add_cog(LearnsCommand(bot))
