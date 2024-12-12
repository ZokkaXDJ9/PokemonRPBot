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

        if os.path.exists(BONK_COUNT_FILE) and os.path.getsize(BONK_COUNT_FILE) > 0:
            try:
                with open(BONK_COUNT_FILE, "r", encoding="utf-8") as f:
                    self.bonk_counts = json.load(f)
            except Exception as e:
                print(f"Failed to load bonk counts: {e}")
                self.bonk_counts = {}
        else:
            self.bonk_counts = {}

    def save_bonk_counts(self):
        with open(BONK_COUNT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.bonk_counts, f, ensure_ascii=False, indent=4)

    @app_commands.command(name="bonk", description="Bonk a user for being inappropriate in general channels!")
    async def bonk(self, interaction: discord.Interaction, member: discord.Member):
        # Retrieve and increment the bonk count for the specified user
        user_id = str(member.id)
        if user_id not in self.bonk_counts:
            self.bonk_counts[user_id] = 1
        else:
            self.bonk_counts[user_id] += 1
    
        # Save the updated bonk count
        self.save_bonk_counts()
    
        # Construct the bonk message
        response = f"Bonks {member.mention}!! No horni in general! [This user has been bonked {self.bonk_counts[user_id]} time{'s' if self.bonk_counts[user_id] > 1 else ''}]"
    
        # Send the message
        await interaction.response.send_message(response)


async def setup(bot):
    await bot.add_cog(BonkCommand(bot))
