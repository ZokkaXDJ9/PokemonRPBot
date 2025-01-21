import discord
from discord import app_commands
from discord.ext import commands
import random

class LootBox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Define multiple lock tables
        self.lock_boxes = {
            "Berry": [
                {"item": "Aspear Berry",    "probability": 100},
                {"item": "Cheri Berry",     "probability": 100},
                {"item": "Chesto Berry",    "probability": 100},
                {"item": "Coba Berry",      "probability": 100},
                {"item": "Colbur Berry",    "probability": 100},
                {"item": "Drash Berry",     "probability": 100},
                {"item": "Pecha Berry",     "probability": 100},
                {"item": "Persim Berry",    "probability": 100},
                {"item": "Rawst Berry",     "probability": 100},
                {"item": "Starf Berry",     "probability": 100},
            ],
            
            "TM": [
                {"item": "Play Rough",          "probability": 100},
                {"item": "Moonblast",           "probability": 100},
                {"item": "Metal Claw",          "probability": 100},
                {"item": "Flash Cannon",        "probability": 100},
                {"item": "Metal Sound",         "probability": 100},
                {"item": "Assurance",           "probability": 100},
                {"item": "Dark Pulse",          "probability": 100},
                {"item": "Nasty Plot",          "probability": 100},
                {"item": "Shadow Claw",         "probability": 100},
                {"item": "Shadow Ball",         "probability": 100},
                {"item": "Curse",               "probability": 100},            
                {"item": "Dragon Claw",         "probability": 100},
                {"item": "Dragon Pulse",        "probability": 100},
                {"item": "Dragon Dance",        "probability": 100},
                {"item": "Bug Bite",            "probability": 100},
                {"item": "Signal Beam",         "probability": 100},
                {"item": "Ice Fang",            "probability": 100},
                {"item": "Aurora Beam",         "probability": 100},
                {"item": "Rock Tomb",           "probability": 100},
                {"item": "Power Gem",           "probability": 100},
                {"item": "Stealth Rock",        "probability": 100},
                {"item": "Zen Headbutt",        "probability": 100},
                {"item": "Psychic",             "probability": 100},
                {"item": "Agility",             "probability": 100},
                {"item": "Light Screen",        "probability": 100},
                {"item": "Reflect",             "probability": 100},
                {"item": "Calm Mind",           "probability": 100},
                {"item": "Drill Run",           "probability": 100},
                {"item": "Earth Power",         "probability": 100},
                {"item": "Spikes",              "probability": 100},
                {"item": "Thunder Fang",        "probability": 100},
                {"item": "Thunderbolt",         "probability": 100},
                {"item": "Thunder Wave",        "probability": 100},
                {"item": "Poison Jab",          "probability": 100},
                {"item": "Venoshock",           "probability": 100},
                {"item": "Toxic",               "probability": 100},
                {"item": "Seed Bomb",           "probability": 100},
                {"item": "Energy Ball",         "probability": 100},
                {"item": "Synthesis",           "probability": 100},
                {"item": "Aerial Ace",          "probability": 100},
                {"item": "Air Slash",           "probability": 100},
                {"item": "Tailwind",            "probability": 100},
                {"item": "Liquidation",         "probability": 100},
                {"item": "Scald",               "probability": 100},
                {"item": "Rock Smash",          "probability": 100},
                {"item": "Aura Sphere",         "probability": 100},
                {"item": "Bulk Up",             "probability": 100},
                {"item": "Detect",              "probability": 100},
                {"item": "Fire Fang",           "probability": 100},
                {"item": "Flamethrower",        "probability": 100},
                {"item": "Will-O-Wisp",         "probability": 100},
                {"item": "Body Slam",           "probability": 100},
                {"item": "Crush Claw",          "probability": 100},
                {"item": "Slash",               "probability": 100},
                {"item": "Round",               "probability": 100},
                {"item": "Double Team",         "probability": 100},
                {"item": "Focus Energy",        "probability": 100},
                {"item": "Helping Hand",        "probability": 100},
                {"item": "Metronome",           "probability": 100},
                {"item": "Protect",             "probability": 100},
                {"item": "Swords Dance",        "probability": 100},
                {"item": "Hidden Power",        "probability": 100},
                {"item": "Song of Storms",      "probability": 100},
                {"item": "Infinity Fracture",   "probability": 100},
                {"item": "Witching Hour",       "probability": 100},
                {"item": "Aura Burst",          "probability": 100},
                {"item": "Springtide",          "probability": 100},
                {"item": "Ground Zero",         "probability": 100},
                {"item": "Tempest",             "probability": 100},
                {"item": "Eclipse",             "probability": 100},
                {"item": "Pheromones",          "probability": 100},
                {"item": "Pole Shift",          "probability": 100},
                {"item": "Cloudy Day",          "probability": 100},
                {"item": "Starry Sky",          "probability": 100},
                {"item": "Incantation",         "probability": 100},
                {"item": "Weather Ball",        "probability": 100},
            ],
            
            "Seed": [
                {"item": "Blast Seed",      "probability": 100},
                {"item": "Encourage Seed",  "probability": 66},
                {"item": "Heal Seed",       "probability": 50},
                {"item": "Reviver Seed",    "probability": 33},
                {"item": "Sleep Seed",      "probability": 100},
                {"item": "Stun Seed",       "probability": 100},
            ],
            
            "Money": [ # This is assuming that Boxes will cost 100 to open
                {"item": "200",    "probability": 100},
                {"item": "300",    "probability": 75},
                {"item": "500",    "probability": 50},
                {"item": "1000",   "probability": 20},
                {"item": "1500",   "probability": 10},
                {"item": "2000",   "probability": 5},
                {"item": "5000",   "probability": 1},
            ],
            
            "Orb": [
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
                {"item": "",   "probability": 100},
            ],
            
            "Common Held Item": [
                {"item": "Air Balloon",     "probability": 100},
                {"item": "Destiny Knot",    "probability": 100},
                {"item": "Electric Seed",   "probability": 100},
                {"item": "Grassy Seed",     "probability": 100},
                {"item": "Misty Seed",      "probability": 100},
                {"item": "Psychic Seed",    "probability": 100},
                {"item": "Focus Band",      "probability": 100},
                {"item": "Grip Claw",       "probability": 100},
                {"item": "Iron Ball",       "probability": 100},
                {"item": "Iron Braces",     "probability": 100},
                {"item": "Punching Glove",  "probability": 100},
                {"item": "Quick Claw",      "probability": 100},
                {"item": "Ring Target",     "probability": 100},
                {"item": "Room Service",    "probability": 100},
                {"item": "Throat Spray",    "probability": 100},
                {"item": "Blunder Policy",  "probability": 100},
                {"item": "Blue Scarf",      "probability": 100},
                {"item": "Green Scarf",     "probability": 100},
                {"item": "Pink Scarf",      "probability": 100},
                {"item": "Red Scarf",       "probability": 100},
                {"item": "Yellow Scarf",    "probability": 100},
                {"item": "Shed Shell",      "probability": 100},
                {"item": "Black Belt",      "probability": 100},
                {"item": "Black Glasses",   "probability": 100},
                {"item": "Charcoal",        "probability": 100},
                {"item": "Dragon Fang",     "probability": 100},
                {"item": "Fairy Feather",   "probability": 100},
                {"item": "Hard Stone",      "probability": 100},
                {"item": "Magnet",          "probability": 100},
                {"item": "Metal Coat",      "probability": 100},
                {"item": "Miracle Seed",    "probability": 100},
                {"item": "Mystic Water",    "probability": 100},
                {"item": "Never-Melt Ice",  "probability": 100},
                {"item": "Poison Barb",     "probability": 100},
                {"item": "Sharp Beak",      "probability": 100},
                {"item": "Silk Scarf",      "probability": 100},
                {"item": "Silver Powder",   "probability": 100},
                {"item": "Soft Sand",       "probability": 100},
                {"item": "Spell Tag",       "probability": 100},
                {"item": "Twisted Spoon",   "probability": 100},
            ],
            
#            "Rare": [
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#            ],
#            
#            "Shop Voucher": [
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#            ],
            
            "Move Card": [
                {"item": "Raging Storm",   "probability": 8},
                {"item": "Focused Winds",   "probability": 8},
                {"item": "Piercing Force",   "probability": 8},
                {"item": "Meteor Shower",   "probability": 5},
                {"item": "Laser Cutter",   "probability": 5},
                {"item": "Mystery Sting",   "probability": 14},
                {"item": "Adaptive Blade",   "probability": 11},
                {"item": "Adaptive Blast",   "probability": 11},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
            ],
#            
#            "RP Item": [
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#            ],
#            
#            "Thing": [
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#                {"item": "",   "probability": 100},
#            ],
        }
    
    def roll_lock(self, box_type):
        if box_type not in self.lock_boxes:
            raise ValueError(f"Invalid lockbox type: {box_type}. Available types: {', '.join(self.lock_boxes.keys())}")
        
        lock_table = self.lock_boxes[box_type]
        total_probability = sum(lock["probability"] for lock in lock_table)
        roll = random.uniform(0, total_probability)
        
        cumulative_probability = 0
        for lock in lock_table:
            cumulative_probability += lock["probability"]
            if roll <= cumulative_probability:
                return lock["item"]
    
    async def lockbox_autocomplete(self, interaction: discord.Interaction, current: str):
        """Provides autocomplete suggestions for lockbox types."""
        return [
            app_commands.Choice(name=box, value=box)
            for box in self.lock_boxes.keys()
            if current.lower() in box.lower()
        ]

    @app_commands.command(name="open_box")
    @app_commands.autocomplete(box_type=lockbox_autocomplete)
    async def lockbox(self, interaction: discord.Interaction, box_type: str):
        """Roll a lockbox of a specified type and get a random item based on probability."""
        try:
            item_won = self.roll_lock(box_type)
            await interaction.response.send_message(f"You opened a {box_type} box and received: **{item_won}**")
        except ValueError as e:
            await interaction.response.send_message(f"❌ {interaction.user.mention}, {str(e)}", ephemeral=True)

# Setup function to add the cog
async def setup(bot):
    
    await bot.add_cog(LootBox(bot))
