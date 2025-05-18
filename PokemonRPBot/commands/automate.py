import discord
from discord import app_commands
from discord.ext import commands
from helpers import ParsedRollQuery

def count_successes_from_result(result_text):
    import re
    match = re.search(r"\*\*(\d+)\*\* Success", result_text)
    return int(match.group(1)) if match else 0

def format_accuracy_result(acc_result, raw_successes, accuracy_mod):
    # Compose result with modifier explained and final result
    mod_text = ""
    if accuracy_mod > 0:
        mod_text = f" (+{accuracy_mod} modifier)"
    elif accuracy_mod < 0:
        mod_text = f" ({accuracy_mod} modifier)"
    final_successes = max(0, raw_successes + accuracy_mod)
    if accuracy_mod != 0:
        base_line = acc_result.split("\n")[0]
        dice_line = acc_result.split("\n")[1] if "\n" in acc_result else ""
        mod_line = f" **{accuracy_mod:+d}** Accuracy "
        final_line = f"= **{final_successes}** Successes."
        # If there is critical info line, show it (from your helpers)
        extra = ""
        if "\n" in acc_result:
            extra = "\n".join(acc_result.split("\n")[2:])
        return f"{base_line}\n{dice_line}{mod_line}{final_line}" + (f"\n{extra}" if extra else "")
    else:
        return acc_result

class Roll2View(discord.ui.View):
    def __init__(self, acc_query_str, dmg_query_str, interaction_user, acc_successes, original_miss, accuracy_mod):
        super().__init__(timeout=60)
        self.acc_query_str = acc_query_str
        self.dmg_query_str = dmg_query_str
        self.interaction_user = interaction_user
        self.rerolled = False
        self.acc_successes = acc_successes
        self.original_miss = original_miss
        self.accuracy_mod = accuracy_mod
        if acc_successes == 0:
            self.children[1].disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.interaction_user:
            await interaction.response.send_message(
                "Only the original roller can reroll!",
                ephemeral=True
            )
            return False
        if self.rerolled:
            await interaction.response.send_message(
                "You can only reroll once.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Reroll Accuracy", style=discord.ButtonStyle.primary, custom_id="reroll_accuracy")
    async def reroll_accuracy(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.rerolled = True
        # Roll dice and get the raw result string and successes
        acc_query = ParsedRollQuery.from_query(self.acc_query_str)
        acc_result = acc_query.execute()
        raw_successes = count_successes_from_result(acc_result)
        final_successes = max(0, raw_successes + self.accuracy_mod)

        # Disable buttons in the original message
        for child in self.children:
            child.disabled = True
        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass

        if final_successes == 0:
            content = f"{format_accuracy_result(acc_result, raw_successes, self.accuracy_mod)}\n\n**Miss!**"
            await interaction.response.send_message(content=content, ephemeral=False)
        else:
            if self.original_miss:
                # If the original roll was a miss, and reroll is a hit, roll damage now!
                dmg_result = ParsedRollQuery.from_query(self.dmg_query_str).execute()
                content = (
                    f"{format_accuracy_result(acc_result, raw_successes, self.accuracy_mod)}\n\n"
                    f"**Hit!**\n\n"
                    f"**Damage Roll:**\n{dmg_result}"
                )
                await interaction.response.send_message(content=content, ephemeral=False)
            else:
                # Original roll was a hit; just show new accuracy result, not new damage
                content = f"{format_accuracy_result(acc_result, raw_successes, self.accuracy_mod)}\n\n**Hit!**"
                await interaction.response.send_message(content=content, ephemeral=False)

    @discord.ui.button(label="Reroll Damage", style=discord.ButtonStyle.danger, custom_id="reroll_damage")
    async def reroll_damage(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.rerolled = True
        dmg_result = ParsedRollQuery.from_query(self.dmg_query_str).execute()
        # Disable all buttons in the original message
        for child in self.children:
            child.disabled = True
        try:
            await interaction.message.edit(view=self)
        except Exception:
            pass

        content = f"**Damage Roll:**\n{dmg_result}"
        await interaction.response.send_message(content=content, ephemeral=False)

class AutomateRoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="automate_rolls",
        description="Roll accuracy (with optional modifier) and damage if it hits."
    )
    @app_commands.describe(
        accuracy="Dice roll for accuracy, e.g. '2d6+1'",
        damage="Dice roll for damage, e.g. '3d8'",
        accuracy_mod="Accuracy modifier (e.g. -1 or 2)."
    )
    async def automate_rolls(
        self,
        interaction: discord.Interaction,
        accuracy: str,
        damage: str,
        accuracy_mod: int = 0
    ):
        acc_query = ParsedRollQuery.from_query(accuracy)
        acc_result = acc_query.execute()
        raw_successes = count_successes_from_result(acc_result)
        final_successes = max(0, raw_successes + accuracy_mod)

        acc_query_str = acc_query.as_button_callback_query_string()
        dmg_query_str = ParsedRollQuery.from_query(damage).as_button_callback_query_string()

        if final_successes == 0:
            content = f"{format_accuracy_result(acc_result, raw_successes, accuracy_mod)}\n\n**Miss!**"
            original_miss = True
        else:
            dmg_query = ParsedRollQuery.from_query(damage)
            dmg_result = dmg_query.execute()
            content = (
                f"{format_accuracy_result(acc_result, raw_successes, accuracy_mod)}\n\n"
                f"**Hit!**\n\n"
                f"**Damage Roll:**\n{dmg_result}"
            )
            original_miss = False

        view = Roll2View(
            acc_query_str, dmg_query_str, interaction.user,
            final_successes, original_miss, accuracy_mod
        )
        await interaction.response.send_message(content=content, view=view)

async def setup(bot):
    await bot.add_cog(AutomateRoll(bot))
