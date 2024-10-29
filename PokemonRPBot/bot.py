import discord_token
import discord
from discord.ext import commands
import config
import sys
import os
import folder_manager  # Import the folder manager

# Add the root directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up intents, including message content intent
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.guilds = True           # Enable guilds intent

# Initialize bot with the updated intents
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_commands():
    for extension in config.COMMANDS:
        await bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    # Set up folders for all guilds
    await folder_manager.setup_folders(bot)
    
    # Load commands
    await load_commands()
    
    # Sync commands with Discord
    await bot.tree.sync()
    print("Commands loaded and synced with Discord.")

# Register the on_guild_join event from folder_manager
bot.event(folder_manager.on_guild_join)

# Run the bot with the token from discord_token module
bot.run(discord_token.TOKEN)
