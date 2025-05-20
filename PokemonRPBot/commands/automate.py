import discord
from discord import app_commands
from discord.ext import commands
from helpers import ParsedRollQuery
import random

def count_successes_from_result(result_text):
    import re
    match = re.search(r"\*\*(\d+)\*\* Success", result_text)
    return int(match.group(1)) if match else 0

def format_accuracy_result(acc_result, raw_successes, accuracy_mod):
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
        extra = ""
        if "\n" in acc_result:
            extra = "\n".join(acc_result.split("\n")[2:])
        return f"{base_line}\n{dice_line}{mod_line}{final_line}" + (f"\n{extra}" if extra else "")
    else:
        return acc_result

def crit_roll(crit_die):
    die_options = {"d8": 8, "d6": 6, "d4": 4, "d2": 2, "d1": 1}
    die = die_options.get(crit_die.lower())
    if die is None:
        return None, None, None
    roll = random.randint(1, die)
    is_crit = (roll == die)
    return die, roll, is_crit

def extract_final_successes(dmg_result):
    import re
    match = re.search(r"\*\*(\d+)\*\* Success", dmg_result)
    return match.group(1) if match else "?"

def build_crit_line_for_initial(crit_die, crit_roll_number, was_crit, dmg_result=None):
    line = f"**Crit Roll:** 1{crit_die} → {crit_roll_number}"
    if was_crit:
        line += "\n**CRIT!**"
        if dmg_result is not None:
            final_successes = extract_final_successes(dmg_result)
            line += f"\nUse ```/crit damage:{final_successes}``` and fill out the other parameters to determine the damage."
    return line


def build_crit_line_for_reroll(final_successes):
    return f"Use ```/crit damage:{final_successes}``` and fill out the other parameters to determine the damage."

class Roll2View(discord.ui.View):
    def __init__(
        self,
        acc_query_str,
        dmg_query_str,
        interaction_user,
        acc_successes,
        original_miss,
        accuracy_mod,
        crit_die,
        crit_roll_number,
        was_crit,
        crit_final_successes
    ):
        super().__init__(timeout=None)
        self.acc_query_str = acc_query_str
        self.dmg_query_str = dmg_query_str
        self.interaction_user = interaction_user
        self.rerolled = False
        self.acc_successes = acc_successes
        self.original_miss = original_miss
        self.accuracy_mod = accuracy_mod
        self.crit_die = crit_die
        self.crit_roll_number = crit_roll_number
        self.was_crit = was_crit
        self.crit_final_successes = crit_final_successes
        if not dmg_query_str or dmg_query_str.strip() == "":
            self.children[1].disabled = True
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
        acc_query = ParsedRollQuery.from_query(self.acc_query_str)
        acc_result = acc_query.execute()
        raw_successes = count_successes_from_result(acc_result)
        final_successes = max(0, raw_successes + self.accuracy_mod)

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
                dmg_result = ParsedRollQuery.from_query(self.dmg_query_str).execute() if self.dmg_query_str else None
                content = (
                    f"**Accuracy Roll:**\n{format_accuracy_result(acc_result, raw_successes, self.accuracy_mod)}\n\n"
                    f"**Hit!**\n\n"
                )
                if dmg_result:
                    content += f"**Damage Roll:**\n{dmg_result}\n\n"
                    # Only show /crit line if the original crit was a crit and this is a damage roll
                    if self.was_crit:
                        final_successes = extract_final_successes(dmg_result)
                        if final_successes != "?":
                            content += build_crit_line_for_reroll(final_successes)
                await interaction.response.send_message(content=content.strip(), ephemeral=False)
            else:
                content = (
                    f"**Accuracy Roll:**\n{format_accuracy_result(acc_result, raw_successes, self.accuracy_mod)}\n\n"
                    f"**Hit!**\n\n"
                )
                await interaction.response.send_message(content=content, ephemeral=False)

    @discord.ui.button(label="Reroll Damage", style=discord.ButtonStyle.danger, custom_id="reroll_damage")
    async def reroll_damage(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.rerolled = True
        dmg_result = ParsedRollQuery.from_query(self.dmg_query_str).execute()
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

    async def crit_die_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ):
        options = [
            ("d8 (0 buffs)", "d8"),
            ("d6 (1 buff)", "d6"),
            ("d4 (2 buffs)", "d4"),
            ("d2 (3 buffs)", "d2"),
            ("d1 (4+ buffs)", "d1"),
        ]
        current = current.lower().replace("d", "")
        filtered = [
            app_commands.Choice(name=label, value=die)
            for label, die in options
            if current in die or current in die.replace("d", "")
        ]
        if not filtered:
            filtered = [app_commands.Choice(name=label, value=die) for label, die in options]
        return filtered[:25]

    @app_commands.command(
        name="automate_rolls",
        description="Roll accuracy (with optional modifier), damage, and crit roll (d8 by default)."
    )
    @app_commands.describe(
        accuracy="Dice roll for accuracy, e.g. '2d6+1'",
        damage="Dice roll for damage, e.g. '3d8' (use 0 for status moves)",
        accuracy_mod="Accuracy modifier (e.g. -1 or 2).",
        crit_die="Crit die to roll for crit (d8, d6, d4, d2, d1). Type a number or leave blank for d8."
    )
    @app_commands.autocomplete(crit_die=crit_die_autocomplete)
    async def automate_rolls(
        self,
        interaction: discord.Interaction,
        accuracy: str,
        damage: str,
        accuracy_mod: int = 0,
        crit_die: str = None
    ):
        if not crit_die:
            crit_die = "d8"
        crit_die_clean = "d" + crit_die.lower().replace("d", "")
        if crit_die_clean not in ("d8", "d6", "d4", "d2", "d1"):
            await interaction.response.send_message(
                "Crit die must be one of: d8, d6, d4, d2, d1.",
                ephemeral=True
            )
            return

        # Roll for crit ONCE, store outcome
        die, crit_roll_number, was_crit = crit_roll(crit_die_clean)

        acc_query = ParsedRollQuery.from_query(accuracy)
        acc_result = acc_query.execute()
        raw_successes = count_successes_from_result(acc_result)
        final_successes = max(0, raw_successes + accuracy_mod)

        acc_query_str = acc_query.as_button_callback_query_string()
        damage_clean = damage.replace(" ", "").lower()
        no_damage = (
            damage_clean in ("0", "0d", "0d6", "0d8", "")
            or damage_clean.startswith("0d")
        )

        dmg_result = None
        crit_final_successes = None
        if final_successes == 0:
            content = f"{format_accuracy_result(acc_result, raw_successes, accuracy_mod)}\n\n**Miss!**"
            original_miss = True
        else:
            if not no_damage:
                dmg_query = ParsedRollQuery.from_query(damage)
                dmg_result = dmg_query.execute()
                if was_crit:
                    crit_final_successes = extract_final_successes(dmg_result)
                content = (
                    f"**Accuracy Roll:**\n{format_accuracy_result(acc_result, raw_successes, accuracy_mod)}\n\n"
                    f"**Hit!**\n\n"
                    f"**Damage Roll:**\n{dmg_result}"
                )
            else:
                dmg_result = None
                content = (
                    f"**Accuracy Roll:**\n{format_accuracy_result(acc_result, raw_successes, accuracy_mod)}\n\n"
                    f"**Hit!**"
                )
            original_miss = False

        # Always show the crit roll line on the initial message (even for miss/status/no-damage)
        content += f"\n\n{build_crit_line_for_initial(crit_die_clean, crit_roll_number, was_crit, dmg_result if was_crit and dmg_result else None)}"

        view = Roll2View(
            acc_query_str,
            damage if not no_damage else "",
            interaction.user,
            final_successes,
            original_miss,
            accuracy_mod,
            crit_die_clean,
            crit_roll_number,
            was_crit,
            crit_final_successes
        )
        await interaction.response.send_message(content=content.strip(), view=view)

async def setup(bot):
    await bot.add_cog(AutomateRoll(bot))
