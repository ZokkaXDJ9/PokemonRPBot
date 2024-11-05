import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# Path to the JSON file for storing bonk counts
BONK_COUNT_FILE = "Data/bonk_counts.json"

class BonkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bonk_counts = self.load_bonk_counts()

    def load_bonk_counts(self):
        """Load bonk counts from a JSON file."""
        if os.path.exists(BONK_COUNT_FILE):
            with open(BONK_COUNT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_bonk_counts(self):
        """Save bonk counts to a JSON file."""
        with open(BONK_COUNT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.bonk_counts, f, ensure_ascii=False, indent=4)

    @app_commands.command(name="bonk", description="Bonk a user for being inappropriate in general channels!")
    async def bonk(self, interaction: discord.Interaction, user: discord.Member):
        # Retrieve and increment the bonk count for the specified user
        user_id = str(user.id)
        self.bonk_counts[user_id] = self.bonk_counts.get(user_id, 0) + 1
        bonk_count = self.bonk_counts[user_id]
        
        # Save the updated bonk count
        self.save_bonk_counts()

        # Construct the bonk message
        response = f"Bonks {user.mention}!! No horni in general! [This user has been bonked {bonk_count} time{'s' if bonk_count > 1 else ''}]"

        # Send the message
        await interaction.response.send_message(response)

async def setup(bot):
    await bot.add_cog(BonkCommand(bot))
