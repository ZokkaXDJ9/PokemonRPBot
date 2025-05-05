import os, sys, subprocess, asyncio, discord
from discord import app_commands
from discord.ext import commands

OWNER_ID = 307627785818603523                 # <-- your Discord user ID
REPO_DIR = r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot"             # <-- folder that has .git
GREET = {
    "xenoverse-extension": "Welcome to Eldiw!",
    "main": "Welcome back to the Citadel!",
}

class Switch(commands.Cog):
    def __init__(self, bot): self.bot = bot

    # /switch <branch>
    @app_commands.command(name="switch", description="Swap git branch & restart")
    @app_commands.describe(branch="Branch name (tab‑complete)")
    async def switch(self, itx: discord.Interaction, branch: str):
        if itx.user.id != OWNER_ID:
            return await itx.response.send_message("⛔ Owner only.", ephemeral=True)

        await itx.response.defer(ephemeral=True)

        run = lambda *c: subprocess.run(c, cwd=REPO_DIR, check=True,
                                        stdout=subprocess.PIPE, text=True)
        try:
            run("git", "fetch", "--all", "--prune")
            run("git", "checkout", branch)
            run("git", "reset", "--hard", f"origin/{branch}")
            run("git", "pull", "--ff-only")
        except subprocess.CalledProcessError as e:
            out = (e.stdout or "").strip()[:1800]
            return await itx.followup.send(f"❌ Git error:\n```{out}```", ephemeral=True)

        # --- send greeting BEFORE reboot ---------------------------------
        if branch in GREET:
            await itx.channel.send(GREET[branch])

        await itx.followup.send(f"✅ On **{branch}** – restarting…", ephemeral=True)
        sys.exit(0)                     # runbot.bat will start us again

    # autocomplete origin branches
    @switch.autocomplete("branch")
    async def auto(self, itx: discord.Interaction, cur: str):
        try:
            out = subprocess.check_output(
                ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"],
                cwd=REPO_DIR, text=True)
            names = [r.split("/",1)[-1] for r in out.splitlines()]
            return [app_commands.Choice(name=n, value=n)
                    for n in names if cur.lower() in n.lower()][:25]
        except: return []

async def setup(bot):
    await bot.add_cog(Switch(bot))
