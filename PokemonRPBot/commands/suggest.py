# suggest.py
import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class SuggestCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Removed OpenAI client initialization here to avoid blocking the event loop
        self.user_characters = {
            307627785818603523: ['Dusk - cartographer and scout', 'Ludwig - adventurer from the old times'],
            234431157008072704: ['Delilah - legendary Blacksmith of the Guild', 'King Claw (self proclaimed) - a weird and lewd crab who lives at the Krabby Beach', 'Shell - Battle Trainer and founder of Team Cool'],
            646909143055204353: ['Gehrman - A quest giver who travels through the world'],
        }

    @app_commands.command(name="suggest", description="Suggest a quest idea for Pokerole using AI.")
    async def suggest(self, interaction: discord.Interaction):
        # Defer the response immediately to acknowledge the interaction
        await interaction.response.defer()

        # Retrieve the user's ID
        user_id = interaction.user.id

        # Get the character list for this user
        character_list = self.user_characters.get(user_id, [])
        if character_list:
            character_text = "Characters associated with you:\n- " + "\n- ".join(character_list)
        else:
            character_text = ""

        # Define the prompt for the AI
        prompt_template = ("""You are an assistant that creates quest ideas for a Pokémon role-playing game using Pokerole.
Generate a creative and engaging quest idea for a Pokémon Mystery Dungeon role-playing discord server using a modified version of Pokerole.
Include details such as setting, characters, objectives, and challenges, but let the Game Master handle the technical details.
We have a Citadel called "Citadel of Lost Legends" and the characters are in an adventuring guild that has the citadel as its HQ.
The characters are all Pokémon. There are no humans in this world. The quest givers can be anyone you want.

Backstory:
The Citadel of Lost Legends
Deep within the Johto Region, far beyond the reaches of known civilization, lies a hidden fortress known only to a few: the Citadel of Lost Legends. Tucked away in the most remote corner of the region, this ancient structure is shrouded in mystery and is conspicuously absent from any map or travel guide. No human has set foot in its halls for centuries, and for good reason. The Citadel is protected by powerful enchantments that make it nearly impossible to find or approach without the guidance of those who already know its secrets.
The Citadel's origins date back to a time long before the advent of human civilization in the Pokémon world. It was built by a council of ancient, wise Pokémon, who were able to foresee the very flow of time. The rise of humanity and the potential imbalance it could bring to the natural order, the creation of more chaotic and destructive Legendary Pokémon, and even dangers from other dimensions and outer space—all of these and more had filled those ancient Pokémon with worry. As a sanctuary, the Citadel was designed to be a place where Pokémon could live free from any of those interferences—and fight back, should the need arise. As a sacred space dedicated to the preservation of Pokémon knowledge, history, and culture, the Citadel of Lost Legends has stood strong against the teeth of time, countless attacks, and even the intervention of divine beings.
At the heart of the Citadel lies its most remarkable feature: a grand portal circle that allows instant travel to any location in the Pokémon world. This circle of power is the lifeline of the Citadel, enabling its inhabitants to reach distant places and gather information, but also serving as the primary means for those with permission to enter its protected grounds. However, the portal's magic is ancient and complex, requiring specific knowledge or artifacts to activate it. This ensures that only those with a deep connection to the Citadel—or the favor of its guardians—can use it.
The Citadel is a place where time seems to stand still. It is steeped in an aura of timelessness, as if the very air within its walls is thicker, older, and infused with the memories of ages past. The stone halls echo with whispers of ancient Pokémon who once walked its corridors, and the walls are adorned with murals depicting legendary battles, forgotten heroes, and tales of Pokémon long forgotten by the outside world.
But what truly sets the Citadel apart is its complete absence of humans. The guardians of the Citadel, a group of powerful Pokémon with an unbroken lineage stretching back to the Citadel's founding, have ensured that no human ever discovers or invades their sacred home. This is not out of malice, but out of a deep-seated belief that the Citadel must remain a place of purity, untouched by the hands of those who might exploit its power.
But over time, the Citadel has fallen from its original grace. Old bloodlines have died out, and one guardian after another began to leave the Citadel of Lost Legends, leaving behind hauntingly empty halls and walls. Until only one has remained: the one who's referring to themselves as the "Administrator."
As an artisan of lower rank and not fit for leadership, it was the Administrator who began to invite foreign Pokémon to the Citadel to build their own society as they see fit. Only those who are of strong heart and goodwill are allowed to enter, as the Citadel is still acting as a sanctuary for those who wish to escape the troubles of the world and a place where the ancient ways are preserved. Imitating its original purpose, the ancient walls of the Citadel are once again used to study the mysteries of the universe, meditating on the balance between the natural world and the ever-changing forces that threaten it—and take on missions to fight against those forces.
Though its existence is known to very few, the Citadel of Lost Legends remains a beacon of hope for Pokémon who dream of a world where they can live freely and fight to preserve balance across all worlds and dimensions. Its location may be remote, its secrets well-guarded, but for those who are worthy, the Citadel is a place where the past and present converge, and where the future of the Pokémon world is quietly shaped, one ancient secret at a time.

The World We Live In
Centuries ago, the entire human population vanished without a trace in an instant. Pokémon, left in a world without their former companions and guidance, found themselves alone and had to adapt to survive. Nature has reclaimed human cities, and wild Pokémon have grown stronger.
Many Pokémon have formed guilds and societies to take on the roles that humans once played, including exploration, protection, and preservation of the world's balance. Many of those guilds have banded together to explore strange phenomena—time distortions, spatial anomalies, and the emergence of strange new dungeons. These dungeons seem to be linked to the mysterious event, with some believing they hold the answers to the humans' fate.
The disappearance of humanity is still a mystery to all. Some Pokémon believe the humans were taken away by a higher power or transported to another dimension. Others think they left of their own accord, abandoning Pokémon to fend for themselves. And the most zealous believe that Arceus himself had chosen to eradicate humankind to free the world of their constant blight and destruction of nature.
But the most mysterious phenomena are the so-called "echoes." After the humans disappeared, some Pokémon began hearing strange "echoes"—whispers, visions, and memories of the past that seem to come from the world of humans. These echoes are faint but persistent, guiding Pokémon to places of significance, like ancient ruins or hidden dungeons. Some Pokémon believe the echoes are the last remnants of human consciousness, while others think they are clues left behind by the humans before they vanished.
Whatever the reason, Pokémon now live on their own accord, and many former balances of power are crumbling and reshaping. Only the Citadel of Lost Legends would've been a bastion of stability had its original Guardians not abandoned it.

NPC/Character List:

{character_text}
Following characters can be used by anyone at any time. Be creative with it:
- The Administrator (Porygon-Z) - is in charge of the guild now, but not as a Guildmaster but as a weird server guy (which is just a fun reference to real-life admins)
- You are welcome to add new characters from the old times as quest givers or Pokémon the team might have to rescue, etc.
- You may also generate completely random quest givers that are not involved with the Citadel at all!
- There is NO Guildmaster/Guild Leader right now. Please also DO NOT make one up.
Also, do NOT add characters to the missions! This is done by the GM, and it will break consistency if you do! Do NOT do that! 
Also, they are characters of players, and you will break something when you send them to missions or let them vanish! Add them as quest givers instead.
You also don't have to add the titles to the characters if you want to use them as quest givers. Everyone knows about them.
Also: DO NOT make the whole quest dependent on them!! They are not the only Pokémon in the guild or the surrounding area!

Reward Guidelines
To have a better idea of what to expect from a quest and what to give out to your players, we're offering this reward guideline to our GMs. These guidelines estimate an adventuring group of 4 people.

Poké Reward
75 pokécoin per hour, for each character.
Modifiers, based on danger level:
safe - x2
moderately dangerous - x3
highly dangerous - x4

Item Rewards
Safe:
Per Character:
1-2 berries per character, up to uncommon

Shared Loot:
1 other common item per character, as an unlockable bonus for good questing (in a hidden chest, for example). May include lockboxes.

Moderately Dangerous:
Per Character:
1-2 berries of any rarity
1 more item up to uncommon (may include TMs). May include lockboxes.

Shared Loot:
2 lockboxes
1 more item of any kind up to rare (may include TMs). May include lockboxes.
1 other uncommon item per character, as an unlockable bonus for good questing (in a hidden chest, for example). May include lockboxes.

Highly Dangerous:
Per Character:
2-3 berries of any rarity
1 lockbox
1 TM of choice (of any rarity)

Shared Loot:
2 held items of any rarity
2 more berries of any kind and rarity
1 other item per character up to rare, as an unlockable bonus for good questing (in a hidden chest, for example). May include lockboxes.

You MAY add rewards any time, but don't remove rewards. The list provides the absolute minimum.

Now, generate a creative and engaging quest idea considering the above information.
""")

        # Replace {character_text} in prompt_template with actual character_text
        prompt = prompt_template.format(character_text=character_text)

        try:
            # Run the blocking code in an executor to prevent blocking the event loop
            loop = asyncio.get_event_loop()
            quest_idea = await loop.run_in_executor(None, self.generate_response, prompt)

            quest_idea = quest_idea.strip()

            # Ensure the message doesn't exceed Discord's limit
            max_message_length = 2000
            prefix = "Here's a quest idea:\n\n"

            # Split the quest_idea into chunks that fit within Discord's message limit
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

            # Send the initial message
            message = await interaction.followup.send(f"{prefix}{quest_idea_parts[0]}")

            # Send subsequent parts as replies to the original message
            for part in quest_idea_parts[1:]:
                await message.reply(part.strip())

        except Exception as e:
            print(f"Error generating quest idea: {e}")
            await interaction.followup.send("Sorry, I couldn't generate a quest idea at this time.")

    def generate_response(self, prompt):
        # Import and initialize the OpenAI client here to avoid blocking the event loop
        from openai import OpenAI

        # Initialize the OpenAI client pointing to your local LM Studio server
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

        # Prepare messages for the chat completion
        messages = [
            {"role": "system", "content": "You are an assistant that creates quest ideas for a Pokémon role-playing game using Pokerole."},
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model="your-model-identifier",  # Replace with your LM Studio model identifier
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        # Extract the assistant's reply
        quest_idea = response.choices[0].message.content.strip()
        return quest_idea

async def setup(bot):
    await bot.add_cog(SuggestCommand(bot))
