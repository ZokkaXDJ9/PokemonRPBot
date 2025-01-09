import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import json
import os

class WarningCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = "warnings.json"
        self.user_warnings = self.load_warnings()

    def load_warnings(self):
        if os.path.exists(self.warnings_file):
            with open(self.warnings_file, "r") as file:
                return json.load(file)
        return {}

    def save_warnings(self):
        with open(self.warnings_file, "w") as file:
            json.dump(self.user_warnings, file, default=str)

    async def warn_user(self, user, interaction, message_id):
        user_id = str(user.id)
        now = datetime.utcnow()

        if user_id not in self.user_warnings:
            self.user_warnings[user_id] = []

        # Remove expired warnings
        self.user_warnings[user_id] = [w for w in self.user_warnings[user_id] if not self.is_warning_expired(w)]

        # Count existing warnings
        warning_count = len([w for w in self.user_warnings[user_id] if w["type"] == "Warning"])
        timeout_count = len([w for w in self.user_warnings[user_id] if w["type"] == "Timeout"])

        if warning_count < 1:
            warning_type = "Warning"
            self.user_warnings[user_id].append({"type": warning_type, "timestamp": now.isoformat()})
            response = f"{user.mention}, this is your first warning for inappropriate behavior. Please stop that."
        elif timeout_count < 1:
            warning_type = "Timeout"
            self.user_warnings[user_id].append({"type": warning_type, "timestamp": now.isoformat()})
            await user.timeout(timedelta(days=1))
            response = f"{user.mention}, you have been timed out for 1 day due to repeated warnings."
        elif timeout_count < 2:
            warning_type = "Timeout"
            self.user_warnings[user_id].append({"type": warning_type, "timestamp": now.isoformat()})
            await user.timeout(timedelta(weeks=1))
            response = f"{user.mention}, you have been timed out for 1 week due to continued inappropriate behavior."
        else:
            warning_type = "Ban"
            self.user_warnings[user_id].append({"type": warning_type, "timestamp": now.isoformat()})
            await interaction.guild.ban(user, reason="Repeated violations of server rules.")
            response = f"{user.mention} has been banned for repeated violations, but their warning history will be retained."

        self.save_warnings()

        channel = interaction.channel
        if channel:
            await channel.send(f"Warning issued for [message](https://discord.com/channels/{interaction.guild_id}/{channel.id}/{message_id}): {response}")

    def is_warning_expired(self, warning):
        warning_type = warning["type"]
        timestamp = datetime.fromisoformat(warning["timestamp"])
        now = datetime.utcnow()

        if warning_type == "Warning":
            return now > timestamp + timedelta(weeks=1)
        elif warning_type == "Timeout":
            return now > timestamp + timedelta(weeks=2)
        elif warning_type == "Ban":
            return False
        return False

    @app_commands.command(name="warn", description="Warn a user for inappropriate behavior.")
    @app_commands.checks.has_permissions(administrator=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, message_id: str):
        await self.warn_user(user, interaction, message_id)

    @app_commands.command(name="clearwarnings", description="Clear all warnings for a user.")
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_warnings(self, interaction: discord.Interaction, user: discord.Member):
        user_id = str(user.id)
        if user_id in self.user_warnings:
            self.user_warnings[user_id] = []
            self.save_warnings()
            await interaction.channel.send(f"All warnings for {user.mention} have been cleared.")
        else:
            await interaction.channel.send(f"{user.mention} has no warnings.")

    @tasks.loop(hours=24)
    async def clean_expired_warnings(self):
        """Clean up expired warnings regularly."""
        for user_id in list(self.user_warnings.keys()):
            self.user_warnings[user_id] = [w for w in self.user_warnings[user_id] if not self.is_warning_expired(w)]
            if not self.user_warnings[user_id]:
                del self.user_warnings[user_id]
        self.save_warnings()

    @app_commands.command(name="warnings", description="Check a user's warning levels.")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        user_id = str(user.id)
        if user_id in self.user_warnings:
            warning_count = len([w for w in self.user_warnings[user_id] if w["type"] == "Warning"])
            timeout_count = len([w for w in self.user_warnings[user_id] if w["type"] == "Timeout"])
            await interaction.channel.send(f"{user.mention} has {warning_count} warnings and {timeout_count} timeouts.")
        else:
            await interaction.channel.send(f"{user.mention} has no warnings.")

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = await self.bot.tree.sync()
        print(f"Synced slash commands to {len(guilds)} guild(s).")

async def setup(bot):
    await bot.add_cog(WarningCog(bot))
