import os
import json
import csv

# Define paths to data folders and CSV files
POKEMON_NEW_FOLDER = "Data/pokemon_new"
POKEMON_OLD_FOLDER = "Data/pokemon_old"
MOVES_CSV = os.path.join("Data/csv", "moves.csv")
POKEMON_CSV = os.path.join("Data/csv", "pokemon.csv")
POKEMON_MOVES_CSV = os.path.join("Data/csv", "pokemon_moves.csv")
POKEMON_MOVE_METHODS_CSV = os.path.join("Data/csv", "pokemon_move_methods.csv")

# Rank mapping dictionary
RANK_MAPPING = {
    "Starter": "Bronze",
    "Beginner": "Bronze",
    "Amateur": "Silver",
    "Ace": "Gold",
    "Pro": "Platinum",
    "Master": "Diamond",
    "Champion": "Diamond"
}

# Data storage dictionaries
moves_data = {}
pokemon_moves_data = {}
pokemon_move_methods_data = {}
pokemon_base_data = {}

def load_csv_data():
    """Load data from CSV files into dictionaries."""
    # Load pokemon.csv
    with open(POKEMON_CSV, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row["identifier"].replace('-', ' ').title()
            pokemon_base_data[row["id"]] = {
                "name": name,
                "species_id": row["species_id"],
                "height": float(row["height"]) / 10,  # Convert to meters
                "weight": float(row["weight"]) / 10,  # Convert to kg
                "number": row["id"]
            }

    # Load moves.csv
    with open(MOVES_CSV, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            moves_data[row["id"]] = {
                "name": row["identifier"].replace('-', ' ').title(),
                "type_id": row["type_id"],
                "power": row["power"],
                "pp": row["pp"],
                "accuracy": row["accuracy"]
            }

    # Load pokemon_moves.csv
    with open(POKEMON_MOVES_CSV, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            pokemon_id = row["pokemon_id"]
            if pokemon_id not in pokemon_moves_data:
                pokemon_moves_data[pokemon_id] = []
            pokemon_moves_data[pokemon_id].append({
                "move_id": row["move_id"],
                "method_id": row["pokemon_move_method_id"],
                "level": row.get("level")
            })

    # Load pokemon_move_methods.csv
    with open(POKEMON_MOVE_METHODS_CSV, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            pokemon_move_methods_data[row["id"]] = row["identifier"].replace('-', ' ').title()

# Load all CSV data on import
load_csv_data()

def load_pokemon_data(pokemon_name):
    """Loads Pokémon data from JSON files or base CSV, then adds moves."""
    # Find Pokémon ID from base data
    pokemon_id = None
    base_pokemon_data = None
    for pid, pdata in pokemon_base_data.items():
        if pdata["name"].lower() == pokemon_name.lower():
            pokemon_id = pid
            base_pokemon_data = pdata
            break

    if pokemon_id is None:
        return None  # Return if Pokémon ID not found in CSV

    # Define file paths for new and old formats using the exact Pokémon name
    new_file_path = os.path.join(POKEMON_NEW_FOLDER, f"{pokemon_name}.json")
    old_file_path = os.path.join(POKEMON_OLD_FOLDER, f"{pokemon_name}.json")

    # Load JSON data if available
    new_data = None
    old_data = None
    if os.path.exists(new_file_path):
        with open(new_file_path, "r") as file:
            new_data = json.load(file)
    if os.path.exists(old_file_path):
        with open(old_file_path, "r") as file:
            old_data = json.load(file)

    # Combine JSON data with base data from CSV
    combined_data = combine_pokemon_data(new_data, old_data, base_pokemon_data)

    # Add learnable moves by rank from CSV data
    combined_data["learnable_moves"] = get_rank_based_moves(pokemon_id)
    return combined_data

def combine_pokemon_data(new_data, old_data, base_data):
    """Combine new/old Pokémon JSON data with base CSV data."""
    # Use base data as the starting point
    if new_data and not old_data:
        return {**base_data, **format_new_data(new_data)}
    if old_data and not new_data:
        return {**base_data, **format_old_data(old_data)}

    # Merge all, prioritizing new_data, then old_data, then base_data
    formatted_new_data = format_new_data(new_data) if new_data else {}
    formatted_old_data = format_old_data(old_data) if old_data else {}
    return {**base_data, **formatted_old_data, **formatted_new_data}

def format_new_data(data):
    """Format new JSON data to match our expected structure."""
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
        "type": data.get("type", ["Electric"]),  # Default example type
        "height_m": data.get("height_m", 0),
        "height_ft": data.get("height_ft", 0),
        "weight_kg": data.get("weight_kg", 0),
        "weight_lb": data.get("weight_lb", 0),
        "evolutions": data.get("evolutions", [])
    }

def format_old_data(data):
    """Format old JSON data to match our expected structure, with rank mappings."""
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

def get_rank_based_moves(pokemon_id):
    """Retrieve moves by rank from CSV data using the provided Pokémon ID."""
    parsed_moves = {rank: [] for rank in RANK_MAPPING.values()}
    parsed_moves["Other"] = []  # Ensure "Other" key is always present

    move_entries = pokemon_moves_data.get(pokemon_id, [])
    for entry in move_entries:
        move_name = moves_data.get(entry["move_id"], {}).get("name", "Unknown Move")
        method = pokemon_move_methods_data.get(entry["method_id"], "Other")

        if method in RANK_MAPPING:
            rank = RANK_MAPPING[method]
            parsed_moves[rank].append(move_name)
        else:
            parsed_moves["Other"].append(move_name)

    return parsed_moves

# Additional helper functions
def get_additional_moves_from_csv(pokemon_id):
    """Retrieve TM, Egg, and Tutor moves from CSV data for a given Pokémon ID."""
    moves = {
        "TM Moves": [],
        "Egg Moves": [],
        "Tutor": [],
        "Other": []
    }

    move_entries = pokemon_moves_data.get(pokemon_id, [])
    for entry in move_entries:
        move_name = moves_data.get(entry["move_id"], {}).get("name", "Unknown Move")
        method = pokemon_move_methods_data.get(entry["method_id"], "Other")

        if method == "Machine":
            moves["TM Moves"].append(move_name)
        elif method == "Egg":
            moves["Egg Moves"].append(move_name)
        elif method == "Tutor":
            moves["Tutor"].append(move_name)
        else:
            moves["Other"].append(move_name)

    return moves

def get_pokemon_moves(pokemon_name):
    """Retrieve and format moves for a Pokémon categorized by method, including missing level-up moves."""
    # Find Pokémon ID based on name
    pokemon_id = None
    for pid, pdata in pokemon_base_data.items():
        if pdata["name"].lower() == pokemon_name.lower():
            pokemon_id = pid
            break

    if pokemon_id is None:
        return f"Pokémon '{pokemon_name}' not found in pokemon.csv."

    # Retrieve moves for this Pokémon from CSV
    move_entries = pokemon_moves_data.get(pokemon_id, [])
    if not move_entries:
        return f"No move entries found for Pokémon '{pokemon_name}'."

    # Load moves from JSON data for this Pokémon
    pokemon_data = load_pokemon_data(pokemon_name)
    json_moves = {move for rank_moves in pokemon_data.get("moves", {}).values() for move in rank_moves}

    # Prepare sets for each relevant move category to avoid duplicates within each category
    moves = {
        "TM Moves": set(),
        "Egg Moves": set(),
        "Tutor Moves": set()
    }
    missing_level_up_moves = set()

    # Sort moves into categories and track missing level-up moves
    for entry in move_entries:
        move_name = moves_data.get(entry["move_id"], {}).get("name", "Unknown Move")
        method_name = pokemon_move_methods_data.get(entry["method_id"], "Other")

        # Categorize moves by method
        if method_name == "Machine":
            moves["TM Moves"].add(move_name)
        elif method_name == "Egg":
            moves["Egg Moves"].add(move_name)
        elif method_name == "Tutor":
            moves["Tutor Moves"].add(move_name)
        elif method_name == "Level Up" and move_name not in json_moves:
            # Only include "Level Up" moves missing in JSON
            missing_level_up_moves.add(move_name)

    # Start building formatted sections and add to message list to avoid splitting categories
    messages = []
    current_message = f"### {pokemon_name.title()} [#{pokemon_id}]\n"

    # Add each section with the appropriate emoji and formatted moves, checking for length
    if moves["TM Moves"]:
        tm_section = "\n:cd: **TM Moves**\n" + "  |  ".join(sorted(moves["TM Moves"]))
        if len(current_message) + len(tm_section) > 2000:
            messages.append(current_message)
            current_message = tm_section
        else:
            current_message += tm_section

    if moves["Egg Moves"]:
        egg_section = "\n\n:egg: **Egg Moves**\n" + "  |  ".join(sorted(moves["Egg Moves"]))
        if len(current_message) + len(egg_section) > 2000:
            messages.append(current_message)
            current_message = egg_section
        else:
            current_message += egg_section

    if moves["Tutor Moves"]:
        tutor_section = "\n\n:teacher: **Tutor**\n" + "  |  ".join(sorted(moves["Tutor Moves"]))
        if len(current_message) + len(tutor_section) > 2000:
            messages.append(current_message)
            current_message = tutor_section
        else:
            current_message += tutor_section

    if missing_level_up_moves:
        missing_section = "\n\n:question: **Learned in Game through level up, but not here**\n" + "  |  ".join(sorted(missing_level_up_moves))
        if len(current_message) + len(missing_section) > 2000:
            messages.append(current_message)
            current_message = missing_section
        else:
            current_message += missing_section

    # Append the last message
    if current_message:
        messages.append(current_message)

    return messages


def parse_stat_range(stat_range):
    """Parse stat range from 'min/max' format in new data."""
    min_stat, max_stat = map(int, stat_range.split("/"))
    return min_stat, max_stat

def parse_moves_new(moves):
    """Parse moves from the new JSON format."""
    return {rank: moves[rank] for rank in moves}

def parse_moves_old(moves):
    """Parse moves in the old data format, applying rank mapping."""
    parsed_moves = {"Bronze": [], "Silver": [], "Gold": [], "Platinum": [], "Diamond": []}
    for move in moves:
        old_rank = move.get("Learned", "")
        new_rank = RANK_MAPPING.get(old_rank, "Bronze")
        parsed_moves[new_rank].append(move.get("Name"))
    return parsed_moves

# Example usage
print(get_pokemon_moves("Abomasnow"))  # Replace "Abomasnow" with any Pokémon name as needed
