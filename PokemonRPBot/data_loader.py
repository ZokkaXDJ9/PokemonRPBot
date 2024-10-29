import os
import json

# Define paths to Pokémon data folders
POKEMON_NEW_FOLDER = "Data/pokemon_new"
POKEMON_OLD_FOLDER = "Data/pokemon_old"

# Define mappings for rank conversions
RANK_MAPPING = {
    "Starter": "Bronze",
    "Beginner": "Bronze",
    "Amateur": "Silver",
    "Ace": "Gold",
    "Pro": "Platinum",
    "Master": "Diamond",
    "Champion": "Diamond"
}

def load_pokemon_data(pokemon_name):
    """Loads Pokémon data, prioritizing the new format if available."""
    # Define file paths for new and old formats using the exact Pokémon name
    new_file_path = os.path.join(POKEMON_NEW_FOLDER, f"{pokemon_name}.json")
    old_file_path = os.path.join(POKEMON_OLD_FOLDER, f"{pokemon_name}.json")

    # Check for new data file first
    if os.path.exists(new_file_path):
        with open(new_file_path, "r") as file:
            new_data = json.load(file)
    else:
        new_data = None

    # Check for old data file if new data is not available or partial
    if os.path.exists(old_file_path):
        with open(old_file_path, "r") as file:
            old_data = json.load(file)
    else:
        old_data = None

    # If neither file exists, return None
    if new_data is None and old_data is None:
        return None

    # Combine data: prioritize new_data, supplement with old_data if necessary
    combined_data = combine_pokemon_data(new_data, old_data)
    return combined_data

def combine_pokemon_data(new_data, old_data):
    """Combine new and old Pokémon data, prioritizing new data where available."""
    if new_data and not old_data:
        return format_new_data(new_data)
    if old_data and not new_data:
        return format_old_data(old_data)

    # Format both data formats
    formatted_new_data = format_new_data(new_data)
    formatted_old_data = format_old_data(old_data)

    # Merge with new_data taking priority
    combined_data = {**formatted_old_data, **formatted_new_data}
    return combined_data

def format_new_data(data):
    """Format new data to a consistent structure."""
    return {
        "number": data.get("number"),
        "name": data.get("name"),
        "base_hp": data.get("base_hp"),
        "strength": parse_stat_range(data.get("strength", "0/0")),
        "dexterity": parse_stat_range(data.get("dexterity", "0/0")),
        "vitality": parse_stat_range(data.get("vitality", "0/0")),
        "special": parse_stat_range(data.get("special", "0/0")),
        "insight": parse_stat_range(data.get("insight", "0/0")),
        "moves": parse_moves_new(data.get("moves", {})),
        "abilities": data.get("abilities", []),
        "type": data.get("type", ["Electric"]),  # Example if only one type
        "height_m": data.get("height_m", 0),
        "height_ft": data.get("height_ft", 0),
        "weight_kg": data.get("weight_kg", 0),
        "weight_lb": data.get("weight_lb", 0),
        "evolutions": data.get("evolutions", [])
    }

def format_old_data(data):
    """Format old data to a consistent structure, applying rank mappings."""
    return {
        "number": data.get("Number"),
        "name": data.get("Name"),
        "base_hp": data.get("BaseHP"),
        "strength": (data.get("Strength", 0), data.get("MaxStrength", 0)),
        "dexterity": (data.get("Dexterity", 0), data.get("MaxDexterity", 0)),
        "vitality": (data.get("Vitality", 0), data.get("MaxVitality", 0)),
        "special": (data.get("Special", 0), data.get("MaxSpecial", 0)),
        "insight": (data.get("Insight", 0), data.get("MaxInsight", 0)),
        "moves": parse_moves_old(data.get("Moves", [])),
        "abilities": [data.get("Ability1"), data.get("Ability2"), data.get("HiddenAbility")],
        "type": [data.get("Type1"), data.get("Type2")],
        "height_m": data.get("Height", {}).get("Meters", 0),
        "height_ft": data.get("Height", {}).get("Feet", 0),
        "weight_kg": data.get("Weight", {}).get("Kilograms", 0),
        "weight_lb": data.get("Weight", {}).get("Pounds", 0),
        "evolutions": data.get("Evolutions", [])
    }

def parse_stat_range(stat_range):
    """Parse stat range from 'min/max' format in new data."""
    min_stat, max_stat = map(int, stat_range.split("/"))
    return (min_stat, max_stat)

def parse_moves_new(moves):
    """Parse moves in the new data format, which are already structured by rank."""
    return {rank: moves[rank] for rank in moves}

def parse_moves_old(moves):
    """Parse moves in the old data format, applying rank mapping."""
    parsed_moves = {"Bronze": [], "Silver": [], "Gold": [], "Platinum": [], "Diamond": []}
    for move in moves:
        old_rank = move.get("Learned", "")
        new_rank = RANK_MAPPING.get(old_rank, "Bronze")  # Default to Bronze if not in mapping
        parsed_moves[new_rank].append(move.get("Name"))
    return parsed_moves
