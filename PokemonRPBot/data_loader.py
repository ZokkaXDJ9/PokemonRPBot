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
POKEMON_SPECIES_CSV = os.path.join("Data/csv", "pokemon_species.csv")

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
pokemon_name_to_id_map = {}
evolution_chains = {}

# Manual override for evolution chain specific to Sneasler and Hisuian Sneasel
EVOLUTION_OVERRIDE = {
    # Hisuian Forms with Listed Pre-Evolutions
    "903": ["10235"],          # Sneasler inherits from Hisuian Sneasel
    "10230": ["10229"],        # Hisuian Arcanine inherits from Hisuian Growlithe
    "10232": ["10231"],        # Hisuian Electrode inherits from Hisuian Voltorb
    "10233": ["157"],          # Hisuian Typhlosion inherits from original Quilava
    "10236": ["503"],          # Hisuian Samurott inherits from original Dewott
    "10237": ["548"],          # Hisuian Lilligant inherits from original Petilil
    "10239": ["10238"],        # Hisuian Zoroark inherits from Hisuian Zorua
    "10242": ["10241"],        # Hisuian Goodra inherits from Hisuian Sliggoo
    "10241": ["705"],          # Hisuian Sliggoo inherits from original Goomy
    "10243": ["712"],          # Hisuian Avalugg inherits from original Bergmite
    "10244": ["724"],          # Hisuian Decidueye inherits from original Dartrix
    "904": ["10234"],          # Overqwil inherits from Hisuian Qwilfish

    # Alolan Forms with Listed Pre-Evolutions
    "10092": ["10091"],        # Alolan Raticate inherits from Alolan Rattata
    "10100": ["25"],           # Alolan Raichu inherits from original Pikachu
    "10102": ["10101"],        # Alolan Sandslash inherits from Alolan Sandshrew
    "10104": ["10103"],        # Alolan Ninetales inherits from Alolan Vulpix
    "10106": ["10105"],        # Alolan Dugtrio inherits from Alolan Diglett
    "10108": ["10107"],        # Alolan Persian inherits from Alolan Meowth
    "10111": ["10110"],        # Alolan Golem inherits from Alolan Graveler
    "10113": ["10112"],        # Alolan Muk inherits from Alolan Grimer
    "10114": ["102"],          # Alolan Exeggutor inherits from original Exeggcute
    "10115": ["104"],          # Alolan Marowak inherits from original Cubone
    "10110": ["10109"],        # Alolan Graveler inherits from Alolan Geodude

    # Galarian Forms with Listed Pre-Evolutions
    "10163": ["10162"],        # Galarian Rapidash inherits from Galarian Ponyta
    "10165": ["10164"],        # Galarian Slowbro inherits from Galarian Slowpoke
    "10167": ["109"],          # Galarian Weezing inherits from original Koffing
    "10172": ["10164"],        # Galarian Slowking inherits from Galarian Slowpoke
    "10175": ["10174"],        # Galarian Linoone inherits from Galarian Zigzagoon
    "862": ["10175"],          # Obstagoon inherits from Galarian Linoone
    "863": ["10161"],          # Perrserker inherits from Galarian Meowth
    "867": ["10179"],          # Runerigus inherits from Galarian Yamask
    "10177": ["10176"],        # Galarian Darmanitan (Standard) inherits from Galarian Darumaka
    "10178": ["10176"],        # Galarian Darmanitan (Zen) inherits from Galarian Darumaka
}



def load_csv_data():
    """Load data from CSV files into dictionaries, including alternate forms and evolution chains."""
    # Load pokemon.csv and map each entry by name to ID
    with open(POKEMON_CSV, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Get the identifier and normalize it for different name formats
            name = row["identifier"].replace('-', ' ').title()  # e.g., "Electrode Hisui"
            normalized_name = row["identifier"]  # e.g., "electrode-hisui"
            pokemon_id = row["id"]

            # Map both title-cased and exact CSV name to the Pokémon ID for flexibility
            pokemon_name_to_id_map[name.lower()] = pokemon_id
            pokemon_name_to_id_map[normalized_name] = pokemon_id

            # Store Pokémon data
            pokemon_base_data[pokemon_id] = {
                "name": name,
                "species_id": row["species_id"],
                "height": float(row["height"]) / 10,  # Convert to meters
                "weight": float(row["weight"]) / 10,  # Convert to kg
                "number": pokemon_id
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

    # Load pokemon_species.csv for evolution chain data
    with open(POKEMON_SPECIES_CSV, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            species_id = row["id"]
            evolves_from = row["evolves_from_species_id"]
            evolution_chain_id = row["evolution_chain_id"]

            # Build evolution chain mapping
            if evolution_chain_id not in evolution_chains:
                evolution_chains[evolution_chain_id] = []
            evolution_chains[evolution_chain_id].append(species_id)

            # Link species to evolution data
            pokemon_base_data[species_id]["evolves_from"] = evolves_from

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

def get_evolution_chain(pokemon_id):
    """Retrieve the evolution chain for a given Pokémon ID, with special handling for overrides."""
    # Use override if available, otherwise use regular evolution chain
    if pokemon_id in EVOLUTION_OVERRIDE:
        # Start with overrides for specific evolution chains
        evolution_chain = EVOLUTION_OVERRIDE[pokemon_id] + [pokemon_id]
        print(f"Applying evolution override for Pokémon ID {pokemon_id}: {evolution_chain}")  # Debugging
    else:
        # Find the evolution chain based on standard species evolution
        chain_id = next(
            (evo_chain_id for evo_chain_id, ids in evolution_chains.items() if pokemon_id in ids), None
        )
        evolution_chain = evolution_chains.get(chain_id, [])
        evolution_chain = evolution_chain[:evolution_chain.index(pokemon_id) + 1] if chain_id else []
    
    print(f"Evolution chain for Pokémon ID {pokemon_id}: {evolution_chain}")  # Debugging
    return evolution_chain


# Reload mechanism if needed for repeated testing
def reload_data():
    global moves_data, pokemon_moves_data, pokemon_move_methods_data, pokemon_base_data, evolution_chains
    moves_data.clear()
    pokemon_moves_data.clear()
    pokemon_move_methods_data.clear()
    pokemon_base_data.clear()
    evolution_chains.clear()
    load_csv_data()

def get_pokemon_moves(pokemon_name):
    """Retrieve and format moves for a Pokémon, prioritizing form-specific moves first."""
    # Normalize the input name to match format in `pokemon.csv` (e.g., "electrode-hisui")
    normalized_name = pokemon_name.lower().replace(' ', '-')
    pokemon_id = pokemon_name_to_id_map.get(normalized_name)
    
    if pokemon_id is None:
        return [f"Pokémon '{pokemon_name}' not found in pokemon.csv."]

    # First, retrieve moves specifically for the Pokémon form specified (e.g., Electrode Hisui)
    specific_moves = load_pokemon_data(pokemon_name).get("moves", {})
    
    # Then retrieve evolution chain with fallback to evolution-based moves
    evolution_chain = get_evolution_chain(pokemon_id)
    
    # Initialize move categories for the combined moves
    moves = {"TM Moves": set(), "Egg Moves": set(), "Tutor Moves": set()}
    missing_level_up_moves = set()

    # Collect moves across the primary Pokémon form, then add evolution chain moves
    move_sources = [(pokemon_id, specific_moves)] + [(evo_id, {}) for evo_id in evolution_chain if evo_id != pokemon_id]
    for evo_id, form_moves in move_sources:
        print(f"Processing moves for Pokémon ID {evo_id}")  # Debugging line
        move_entries = pokemon_moves_data.get(evo_id, [])
        
        # Collect JSON moves directly tied to the primary form
        json_moves = {move for rank_moves in form_moves.values() for move in rank_moves}

        for entry in move_entries:
            move_name = moves_data.get(entry["move_id"], {}).get("name", "Unknown Move")
            method_name = pokemon_move_methods_data.get(entry["method_id"], "Other")

            if method_name == "Machine":
                moves["TM Moves"].add(move_name)
            elif method_name == "Egg":
                moves["Egg Moves"].add(move_name)
            elif method_name == "Tutor":
                moves["Tutor Moves"].add(move_name)
            elif method_name == "Level Up" and move_name not in json_moves:
                missing_level_up_moves.add(move_name)

    # Build formatted sections for the output message
    messages = []
    current_message = f"### {pokemon_name.title()} [#{pokemon_id}]\n"

    # Add each section with appropriate emoji and formatted moves
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

    # Append the final message
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
reload_data()
print(get_pokemon_moves("Sneasler"))  # Replace "Sneasler" with any Pokémon name as needed
