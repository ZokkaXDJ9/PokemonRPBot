import discord
from discord import app_commands
from discord.ext import commands
import os
import json

class SetupQuestGiver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = "Data/questgiver/"

        # Ensure the folder exists
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    @app_commands.command(name="setup_questgiver", description="Set up a quest giver for your account.")
    async def setup_questgiver(self, interaction: discord.Interaction, name: str, role: str, description: str):
        user_id = str(interaction.user.id)
        file_path = os.path.join(self.data_folder, f"{user_id}.json")

        # If the file doesn't exist, create it with an empty list of quest givers
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump({"quest_givers": []}, file)

        # Load the existing quest givers from the file
        with open(file_path, "r") as file:
            data = json.load(file)

        # Append the new quest giver
        quest_giver = {
            "name": name,
            "role": role,
            "description": description
        }
        data["quest_givers"].append(quest_giver)

        # Save the updated list back to the file
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        # Confirm to the user
        await interaction.response.send_message(f"Quest giver '{name}' has been set up for your account!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetupQuestGiver(bot))
