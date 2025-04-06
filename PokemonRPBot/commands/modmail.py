import discord
from discord.ext import commands
from discord import app_commands
import uuid
import json
import os

# Path to the JSON file for persistent storage.
DATA_FILE = "mod_mail_records.json"

class ClaimView(discord.ui.View):
    def __init__(self, mod_mail_id, cog, disabled=False):
        super().__init__(timeout=None)
        self.mod_mail_id = mod_mail_id
        self.cog = cog
        # Disable all buttons if this mod mail has been claimed.
        for item in self.children:
            item.disabled = disabled

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, custom_id="claim_button")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Retrieve the mod mail record.
        record = self.cog.mod_mail_records.get(self.mod_mail_id)
        if record is None:
            await interaction.response.send_message("Mod mail record not found.", ephemeral=True)
            return

        # Retrieve the guild using the stored guild_id.
        guild = self.cog.bot.get_guild(record.get("guild_id"))
        if guild is None:
            await interaction.response.send_message("Guild not found.", ephemeral=True)
            return

        # Get the member object (since in a DM, interaction.user is a User, not a Member).
        member = guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("Could not verify your membership in the guild.", ephemeral=True)
            return

        mod_role = guild.get_role(self.cog.mod_role_id)
        if mod_role not in member.roles:
            await interaction.response.send_message("You are not authorized to claim mod mail.", ephemeral=True)
            return

        # If already claimed, notify the moderator.
        if record["claimed"]:
            claimer = record.get("claimer_id")
            claimer_mention = f"<@{claimer}>" if claimer else "Unknown"
            await interaction.response.send_message(
                f"This mod mail has already been claimed by {claimer_mention}.", ephemeral=True
            )
            return

        # Mark this mod mail as claimed.
        record["claimed"] = True
        record["claimer_id"] = interaction.user.id

        # Update all DM messages to disable the claim button.
        await self.cog.update_mod_mail_views(self.mod_mail_id)
        await self.cog.save_mod_mail_records()

        await interaction.response.send_message("You have claimed this mod mail.", ephemeral=True)

        # Notify the original user if the mail wasn't sent anonymously.
        if not record.get("anonymous", True) and "user_id" in record:
            try:
                user = await self.cog.bot.fetch_user(record["user_id"])
                await user.send(
                    f"Your mod mail has been claimed by {interaction.user.mention}. They will be in touch with you shortly."
                )
            except Exception as e:
                print(f"Failed to notify user: {e}")

class ModMail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # In-memory storage of mod mail records.
        # Each record is keyed by a unique mod_mail_id and stores:
        #   - guild_id: The guild where the mod mail originated.
        #   - description: The complaint text.
        #   - anonymous: Whether the sender chose to be anonymous.
        #   - claimed: Boolean flag for claim status.
        #   - claimer_id: The ID of the moderator who claimed it.
        #   - messages: A list of dicts for each DM sent, holding mod_id, channel_id, and message_id.
        #   - user_id: (optional) The ID of the user who submitted the mod mail (if not anonymous).
        self.mod_mail_records = {}
        # Configure your moderator role ID and mod notification channel ID here:
        self.mod_role_id = 1271553707355541594       # Replace with your moderator role ID.
        self.mod_notification_channel_id = 1357082399044931695  # Replace with your notification channel ID.

        self.load_mod_mail_records()

    def load_mod_mail_records(self):
        """Load mod mail records from disk if available."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.mod_mail_records = json.load(f)
            except Exception as e:
                print(f"Error loading mod mail records: {e}")

    async def save_mod_mail_records(self):
        """Save the current mod mail records to disk."""
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.mod_mail_records, f)
        except Exception as e:
            print(f"Error saving mod mail records: {e}")

    async def update_mod_mail_views(self, mod_mail_id):
        """
        For a given mod mail record, fetch all stored DM messages and update their views.
        If the record is claimed, the claim buttons are disabled.
        """
        record = self.mod_mail_records.get(mod_mail_id)
        if not record:
            return
        disabled = record.get("claimed", False)
        # Iterate over each stored DM message info.
        for msg_info in record.get("messages", []):
            try:
                # Get the DM channel; if not cached, fetch it.
                channel = self.bot.get_channel(msg_info["channel_id"])
                if channel is None:
                    channel = await self.bot.fetch_channel(msg_info["channel_id"])
                msg = await channel.fetch_message(msg_info["message_id"])
                # Create a new ClaimView (disabled if already claimed).
                view = ClaimView(mod_mail_id, self, disabled=disabled)
                await msg.edit(view=view)
            except Exception as e:
                print(f"Failed to update DM message (mod_mail_id {mod_mail_id}): {e}")

    async def cog_load(self):
        """
        Once the cog is loaded (or after a bot restart),
        re-bind the interactive views to any stored mod mail records.
        """
        for mod_mail_id, record in self.mod_mail_records.items():
            await self.update_mod_mail_views(mod_mail_id)

    @app_commands.command(name="modmail", description="Send a mod mail complaint")
    async def modmail(self, interaction: discord.Interaction, description: str, anonymize: bool):
        # Acknowledge the command privately.
        await interaction.response.send_message("Your mod mail has been sent.", ephemeral=True)
        mod_mail_id = str(uuid.uuid4())
        # Create a record for this mod mail.
        record = {
            "guild_id": interaction.guild.id,  # Store the originating guild's ID.
            "description": description,
            "anonymous": anonymize,
            "claimed": False,
            "claimer_id": None,
            "messages": []  # This will hold dicts with mod_id, channel_id, message_id.
        }
        # Save the sender's user ID only if not anonymous.
        if not anonymize:
            record["user_id"] = interaction.user.id

        self.mod_mail_records[mod_mail_id] = record

        # Format user info based on anonymize flag.
        user_info = "Anonymous" if anonymize else f"{interaction.user} (ID: {interaction.user.id})"
        mod_mail_content = f"**New Mod Mail**\n**User:** {user_info}\n**Description:** {description}"

        # Find all mods in the guild (by checking for the specified mod role).
        mods = [
            member for member in interaction.guild.members
            if any(role.id == self.mod_role_id for role in member.roles)
        ]
        for mod in mods:
            try:
                dm = await mod.create_dm()
                view = ClaimView(mod_mail_id, self, disabled=False)
                msg = await dm.send(content=mod_mail_content, view=view)
                # Save the message details for persistence.
                record["messages"].append({
                    "mod_id": mod.id,
                    "channel_id": dm.id,
                    "message_id": msg.id
                })
            except Exception as e:
                print(f"Could not send DM to mod {mod}: {e}")

        await self.save_mod_mail_records()

        # Send a notification in the designated channel (pinging the mod role).
        channel = self.bot.get_channel(self.mod_notification_channel_id)
        if channel:
            await channel.send(content=f"<@&{self.mod_role_id}> You have new mod mail!")
        else:
            print("Mod notification channel not found.")

async def setup(bot):
    await bot.add_cog(ModMail(bot))
