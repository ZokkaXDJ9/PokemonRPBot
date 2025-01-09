import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class SlotMachineCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slot", description="Spin a 3x3 slot machine and stop the bars with buttons!")
    async def slot(self, interaction: discord.Interaction):
        # Generate shuffled columns with numbers 0–9
        bars = [self.generate_shuffled_numbers(seed=i) for i in range(3)]
        positions = [0, 0, 0]  # Current positions in each column
        stopped = [False, False, False]  # Tracks whether each column has stopped

        # Send the initial message with buttons
        view = SlotMachineView(bars, positions, stopped)
        await interaction.response.send_message(
            content=self.render_grid(bars, positions, spinning=True), view=view
        )

        # Animation loop
        message = await interaction.original_response()
        while not all(stopped):
            for i in range(3):
                if not stopped[i]:
                    positions[i] = (positions[i] + 1) % 10  # Cycle through numbers
            await message.edit(content=self.render_grid(bars, positions, spinning=True), view=view)
            await asyncio.sleep(0.2)  # Control animation speed

        # Final result
        await message.edit(content=self.render_grid(bars, positions, spinning=False), view=None)
        result = "🎉 You win!" if self.check_win(bars, positions) else "Better luck next time!"
        await interaction.followup.send(result)

    def generate_shuffled_numbers(self, seed):
        """Generate a shuffled list of numbers from 0 to 9."""
        numbers = list(range(10))
        random.seed(seed)
        random.shuffle(numbers)
        return numbers

    def render_grid(self, bars, positions, spinning=True):
        """Render the 3x3 grid based on current positions."""
        grid = [[bars[col][(positions[col] + row) % 10] for col in range(3)] for row in range(3)]
        grid_display = "\n".join([" | ".join(map(str, row)) for row in grid])
        status = "Spinning..." if spinning else "Stopped!"
        return f"🎰 Slot Machine 🎰\n\n{grid_display}\n\n{status}"

    def check_win(self, bars, positions):
        """Check if any row has identical numbers."""
        grid = [[bars[col][(positions[col] + row) % 10] for col in range(3)] for row in range(3)]
        for row in grid:
            if len(set(row)) == 1:
                return True
        return False

class SlotMachineView(discord.ui.View):
    """View with buttons to stop the slot machine columns."""

    def __init__(self, bars, positions, stopped):
        super().__init__(timeout=None)
        self.bars = bars
        self.positions = positions
        self.stopped = stopped

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary, row=0)
    async def stop_col_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.stopped[0]:
            self.stopped[0] = True
            await interaction.response.defer()

    @discord.ui.button(label="2", style=discord.ButtonStyle.primary, row=0)
    async def stop_col_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.stopped[1]:
            self.stopped[1] = True
            await interaction.response.defer()

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary, row=0)
    async def stop_col_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.stopped[2]:
            self.stopped[2] = True
            await interaction.response.defer()

async def setup(bot):
    await bot.add_cog(SlotMachineCommand(bot))
