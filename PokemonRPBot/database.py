import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path: str):
        """Initialize the database connection."""
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def close(self):
        """Close the database connection."""
        self.connection.close()

    # --- Character Functions ---

    def create_character(self, user_id: int, guild_id: int, name: str, pokemon_species_id: int, is_shiny: bool, phenotype: int, experience: int = 0, money: int = 500):
        """Create a new character, checking if it already exists."""
        # Check if character exists
        self.cursor.execute("SELECT * FROM character WHERE name = ? AND guild_id = ?", (name, guild_id))
        if self.cursor.fetchone():
            return "Character with this name already exists in the guild."

        # Insert new character
        creation_date = datetime.utcnow().date().isoformat()
        query = """
            INSERT INTO character (
                user_id, guild_id, name, experience, money, creation_date,
                species_api_id, is_shiny, phenotype
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (user_id, guild_id, name, experience, money, creation_date, pokemon_species_id, is_shiny, phenotype))
        self.connection.commit()
        return f"Character '{name}' created successfully!"

    def get_character(self, name: str, guild_id: int) -> Optional[Tuple]:
        """Retrieve character details by name and guild."""
        self.cursor.execute("SELECT * FROM character WHERE name = ? AND guild_id = ?", (name, guild_id))
        return self.cursor.fetchone()

    def update_character_stats(self, character_id: int, new_exp: int, new_money: int):
        """Update experience and money for a character."""
        self.cursor.execute("UPDATE character SET experience = ?, money = ? WHERE id = ?", (new_exp, new_money, character_id))
        self.connection.commit()
        return "Character stats updated successfully."

    # --- Quest Functions ---

    def create_quest(self, guild_id: int, channel_id: int, creator_id: int, max_participants: int) -> int:
        """Add a new quest and return the quest ID."""
        creation_timestamp = int(datetime.utcnow().timestamp())
        query = """
            INSERT INTO quest (
                guild_id, channel_id, creator_id, creation_timestamp, maximum_participant_count
            ) VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (guild_id, channel_id, creator_id, creation_timestamp, max_participants))
        self.connection.commit()
        return self.cursor.lastrowid

    def add_quest_participant(self, quest_id: int, character_id: int, accepted: bool = False):
        """Sign a character up for a quest."""
        timestamp = int(datetime.utcnow().timestamp())
        query = """
            INSERT INTO quest_signup (
                quest_id, character_id, timestamp, accepted
            ) VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(query, (quest_id, character_id, timestamp, accepted))
        self.connection.commit()
        return f"Character {character_id} signed up for quest {quest_id}."

    def complete_quest(self, quest_id: int, character_id: int):
        """Mark a quest as completed for a character."""
        query = "INSERT INTO quest_completion (quest_id, character_id) VALUES (?, ?)"
        self.cursor.execute(query, (quest_id, character_id))
        self.connection.commit()
        return f"Character {character_id} completed quest {quest_id}."

    # --- Guild Functions ---

    def update_guild_money(self, guild_id: int, new_money: int):
        """Update the money for a guild."""
        self.cursor.execute("UPDATE guild SET money = ? WHERE id = ?", (new_money, guild_id))
        self.connection.commit()
        return f"Guild {guild_id} money updated to {new_money}."

    def get_guild_money(self, guild_id: int) -> int:
        """Retrieve the money value for a guild."""
        self.cursor.execute("SELECT money FROM guild WHERE id = ?", (guild_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    # --- Emoji Functions ---

    def add_emoji(self, species_api_id: int, guild_id: int, is_female: bool, is_shiny: bool, is_animated: bool, discord_string: str):
        """Add an emoji based on character properties."""
        query = """
            INSERT INTO emoji (
                species_api_id, guild_id, is_female, is_shiny, is_animated, discord_string
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (species_api_id, guild_id, is_female, is_shiny, is_animated, discord_string))
        self.connection.commit()
        return f"Emoji for species {species_api_id} added to guild {guild_id}."

    def get_emoji(self, species_api_id: int, guild_id: int, is_female: bool, is_shiny: bool) -> Optional[str]:
        """Retrieve an emoji string based on species, guild, gender, and shiny status."""
        query = """
            SELECT discord_string FROM emoji
            WHERE species_api_id = ? AND guild_id = ? AND is_female = ? AND is_shiny = ?
        """
        self.cursor.execute(query, (species_api_id, guild_id, is_female, is_shiny))
        result = self.cursor.fetchone()
        return result[0] if result else None

# Usage Example:
# db = Database('/path/to/database.sqlite')
# print(db.create_character(user_id=1, guild_id=1234, name="TestCharacter", pokemon_species_id=25, is_shiny=False, phenotype=1))
# print(db.add_quest_participant(quest_id=1, character_id=1))
# print(db.get_guild_money(1234))
# db.close()
