import discord
from discord import app_commands
from discord.ext import commands
import os
import json

class EditQuestGiverCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = "Data/questgiver/"

    def load_user_questgivers(self, user_id):
        """Load the user's quest givers from JSON or return an empty list if none exist."""
        file_path = os.path.join(self.data_folder, f"{user_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file).get("quest_givers", [])
        return []

    def save_user_questgivers(self, user_id, quest_givers):
        """Save the user's quest givers to JSON."""
        file_path = os.path.join(self.data_folder, f"{user_id}.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            json.dump({"quest_givers": quest_givers}, file, indent=4)

    async def questgiver_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete function for quest giver names."""
        user_id = interaction.user.id
        quest_givers = self.load_user_questgivers(user_id)
        
        return [
            app_commands.Choice(name=qg["name"], value=qg["name"])
            for qg in quest_givers
            if current.lower() in qg["name"].lower()
        ][:25]

    @app_commands.command(name="edit_questgiver", description="Edit an existing quest giver's information.")
    @app_commands.autocomplete(name=questgiver_autocomplete)
    async def edit_questgiver(
        self, 
        interaction: discord.Interaction, 
        name: str, 
        new_name: str = None, 
        new_role: str = None, 
        new_description: str = None
    ):
        user_id = interaction.user.id

        # Ensure at least one additional field is provided
        if not any([new_name, new_role, new_description]):
            await interaction.response.send_message(
                "Please provide at least one field to update (new_name, new_role, or new_description).",
                ephemeral=True
            )
            return

        # Load the user's quest givers
        quest_givers = self.load_user_questgivers(user_id)
        quest_giver = next((qg for qg in quest_givers if qg["name"].lower() == name.lower()), None)

        if not quest_giver:
            await interaction.response.send_message("Quest giver not found. Please check the name and try again.", ephemeral=True)
            return

        # Update the quest giver's information
        if new_name:
            quest_giver["name"] = new_name
        if new_role:
            quest_giver["role"] = new_role
        if new_description:
            quest_giver["description"] = new_description

        # Save the updated quest givers back to the JSON file
        self.save_user_questgivers(user_id, quest_givers)

        # Confirm the update to the user
        await interaction.response.send_message(f"Quest giver '{name}' has been updated successfully.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EditQuestGiverCommand(bot))
