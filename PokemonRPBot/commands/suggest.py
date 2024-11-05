import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import os
import json
import random

class SuggestCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = "Data/questgiver/"

    def load_user_characters(self, user_id):
        """Load quest givers from a user's JSON file, or return an empty list if none exist."""
        file_path = os.path.join(self.data_folder, f"{user_id}.json")

        # If the file exists, load and return the quest givers
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                return data.get("quest_givers", [])

        # Return an empty list if the file does not exist
        return []

    async def questgiver_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete function to suggest quest giver names."""
        user_id = interaction.user.id
        quest_givers = self.load_user_characters(user_id)
        
        # Filter quest giver names based on the current input
        return [
            app_commands.Choice(name=qg["name"], value=qg["name"])
            for qg in quest_givers
            if current.lower() in qg["name"].lower()
        ][:25]  # Limit to 25 choices for Discord's limit

    @app_commands.command(name="suggest", description="Suggest a quest idea for Pokerole using AI.")
    @app_commands.autocomplete(name=questgiver_autocomplete)
    async def suggest(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        user_id = interaction.user.id

        # Load the quest givers and find the selected one
        quest_givers = self.load_user_characters(user_id)
        selected_character = next((qg for qg in quest_givers if qg["name"].lower() == name.lower()), None)

        if not selected_character:
            await interaction.followup.send("Quest giver not found. Please make sure you've set them up with `/setup_questgiver`.")
            return

        # Prepare character details for the prompt
        character_text = f"{selected_character['name']} - {selected_character['role']}: {selected_character['description']}"

        # Define the AI prompt
        prompt_template = ("""You are an assistant that creates quest ideas for a Pokémon role-playing game using Pokerole.
Generate a creative and engaging quest idea for a Pokémon Mystery Dungeon role-playing discord server using a modified version of Pokerole.
Include details such as setting, characters, objectives, and challenges, but let the Game Master handle the technical details.
We have a Citadel called "Citadel of Lost Legends" and the characters are in an adventuring guild that has the citadel as its HQ.
The characters are all Pokémon. There are no humans in this world. The quest givers can be anyone you want.

NPC/Character List:
Characters associated with this quest:
- {character_text}
The following characters can be used by anyone at any time. Be creative with it:
- The Administrator (Porygon-Z) - in charge of the guild, acting more like a server administrator than a Guildmaster.
- You are welcome to add new characters from the old times as quest givers or Pokémon the team might have to rescue.
- There is NO Guildmaster/Guild Leader right now. Please also DO NOT make one up.

Reward Guidelines:
Safe:
- 75 pokécoin per hour, for each character.
- 1-2 berries, common item per character.
Moderately Dangerous:
- 1-2 berries of any rarity, additional uncommon items.
Highly Dangerous:
- 2-3 berries of any rarity, 1 TM of choice (any rarity), additional rare items.

Generate a quest idea based on these parameters.
""")

        # Replace {character_text} with the actual quest giver details
        prompt = prompt_template.format(character_text=character_text)

        try:
            loop = asyncio.get_event_loop()
            quest_idea = await loop.run_in_executor(None, self.generate_response, prompt)
            quest_idea = quest_idea.strip()

            max_message_length = 2000
            prefix = "Here's a quest idea:\n\n"

            # Send the quest idea, breaking it up if it exceeds Discord's message limit
            quest_idea_parts = []
            current_part = ""
            for paragraph in quest_idea.split('\n'):
                if len(current_part) + len(paragraph) + 1 <= max_message_length - len(prefix):
                    current_part += paragraph + '\n'
                else:
                    quest_idea_parts.append(current_part)
                    current_part = paragraph + '\n'
            if current_part:
                quest_idea_parts.append(current_part)

            message = await interaction.followup.send(f"{prefix}{quest_idea_parts[0]}")

            for part in quest_idea_parts[1:]:
                await message.reply(part.strip())

        except Exception as e:
            print(f"Error generating quest idea: {e}")
            await interaction.followup.send("Sorry, I couldn't generate a quest idea at this time.")

    def generate_response(self, prompt):
        from openai import OpenAI
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        
        # Define messages for a chat completion
        messages = [
            {"role": "system", "content": "You are an assistant that creates quest ideas for a Pokémon role-playing game using Pokerole."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="your-model-identifier",  # Replace with your desired model
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        
        # Extract and return the assistant's reply
        return response.choices[0].message.content.strip()

async def setup(bot):
    await bot.add_cog(SuggestCommand(bot))
