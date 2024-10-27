import discord_token
import discord
from discord.ext import commands
import config

# Set up intents, including message content intent
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Initialize bot with the updated intents
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_commands():
    for extension in config.COMMANDS:
        await bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await load_commands()
    # Sync commands with Discord to make them available
    await bot.tree.sync()
    print("Commands loaded and synced with Discord.")

bot.run(discord_token.TOKEN)
