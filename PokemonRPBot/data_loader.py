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

VALID_RANKS = {"Bronze", "Silver", "Gold", "Platinum", "Diamond"}

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

RANK_EMOJIS = {
    "Bronze": "<:badgebronze:1272532685197152349>",
    "Silver": "<:badgesilver:1272533590697185391>",
    "Gold": "<:badgegold:1272532681992962068>",
    "Platinum": "<:badgeplatinum:1272533593750507570>",
    "Diamond": "<:badgediamond:1272532683431481445>"
}

# Data storage dictionaries
moves_data = {}
pokemon_moves_data = {}
pokemon_move_methods_data = {}
pokemon_base_data = {}
pokemon_name_to_id_map = {}
evolution_chains = {}

# Manual override for evolution chain specific to certain forms
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
            if species_id in pokemon_base_data:
                pokemon_base_data[species_id]["evolves_from"] = evolves_from

# Load all CSV data on import
load_csv_data()

def load_pokemon_data(pokemon_name):
    """Loads Pokémon data from JSON files or base CSV, then adds moves."""
    # Find Pokémon ID from base data
    normalized_name = pokemon_name.lower().replace(' ', '-')
    pokemon_id = pokemon_name_to_id_map.get(normalized_name)

    if pokemon_id is None:
        return None  # Return if Pokémon ID not found in CSV

    base_pokemon_data = pokemon_base_data.get(pokemon_id)

    # Define file paths for new and old formats using the exact Pokémon name
    new_file_path = os.path.join(POKEMON_NEW_FOLDER, f"{pokemon_name}.json")
    old_file_path = os.path.join(POKEMON_OLD_FOLDER, f"{pokemon_name}.json")

    # Load JSON data if available
    new_data = None
    old_data = None
    if os.path.exists(new_file_path):
        with open(new_file_path, "r", encoding="utf-8") as file:
            new_data = json.load(file)
    if os.path.exists(old_file_path):
        with open(old_file_path, "r", encoding="utf-8") as file:
            old_data = json.load(file)

    # Combine JSON data with base data from CSV
    combined_data = combine_pokemon_data(new_data, old_data, base_pokemon_data)

    # Only add learnable moves from CSV if moves are not present
    if not combined_data.get("moves"):
        combined_data["moves"] = get_rank_based_moves(pokemon_id)
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
    parsed_moves = {rank: [] for rank in VALID_RANKS}
    parsed_moves["Other"] = []  # Ensure "Other" key is always present

    move_entries = pokemon_moves_data.get(pokemon_id, [])
    for entry in move_entries:
        move_name = moves_data.get(entry["move_id"], {}).get("name", "Unknown Move")
        method = pokemon_move_methods_data.get(entry["method_id"], "Other")

        if method in RANK_MAPPING:
            rank = RANK_MAPPING[method]
            if rank in VALID_RANKS:
                parsed_moves[rank].append(move_name)
            else:
                parsed_moves["Other"].append(move_name)
        else:
            parsed_moves["Other"].append(move_name)

    return parsed_moves

def get_additional_moves(pokemon_name):
    """Retrieve and format additional moves (TM, Egg, Tutor, Other Level Up Moves) for a Pokémon."""
    # Normalize the input name
    normalized_name = pokemon_name.lower().replace(' ', '-')
    pokemon_id = pokemon_name_to_id_map.get(normalized_name)

    if pokemon_id is None:
        return [f"Pokémon '{pokemon_name}' not found in pokemon.csv."]

    # Load Pokémon data to get rank-based moves
    pokemon_data = load_pokemon_data(pokemon_name)
    specific_moves = pokemon_data.get("moves", {})
    # Collect all moves from rank-based moves into a set
    rank_moves_set = set()
    for rank_moves in specific_moves.values():
        rank_moves_set.update(rank_moves)

    # Initialize move categories
    moves = {"TM Moves": set(), "Egg Moves": set(), "Tutor Moves": set()}
    missing_level_up_moves = set()

    # Collect moves from CSV data
    evolution_chain = get_evolution_chain(pokemon_id)
    move_sources = [pokemon_id] + [evo_id for evo_id in evolution_chain if evo_id != pokemon_id]
    for evo_id in move_sources:
        move_entries = pokemon_moves_data.get(evo_id, [])
        for entry in move_entries:
            move_name = moves_data.get(entry["move_id"], {}).get("name", "Unknown Move")
            method_id = entry["method_id"]
            method_name = pokemon_move_methods_data.get(method_id, "other").lower()

            if method_name == "machine":
                moves["TM Moves"].add(move_name)
            elif method_name == "egg":
                moves["Egg Moves"].add(move_name)
            elif method_name == "tutor":
                moves["Tutor Moves"].add(move_name)
            elif method_name == "level up":
                # Only add level-up moves not in rank_moves_set
                if move_name not in rank_moves_set:
                    missing_level_up_moves.add(move_name)

    # Build the message
    messages = []
    current_message = f"### {pokemon_name.title()} [#{pokemon_id}]\n"

    # Adjust the formatting to include double spaces
    separator = "  |  "

    # Add each section with appropriate emoji and formatted moves
    if moves["TM Moves"]:
        tm_section = "\n:cd: **TM Moves**\n" + separator.join(sorted(moves["TM Moves"]))
        if len(current_message) + len(tm_section) > 2000:
            messages.append(current_message)
            current_message = tm_section
        else:
            current_message += tm_section

    if moves["Egg Moves"]:
        egg_section = "\n\n:egg: **Egg Moves**\n" + separator.join(sorted(moves["Egg Moves"]))
        if len(current_message) + len(egg_section) > 2000:
            messages.append(current_message)
            current_message = egg_section
        else:
            current_message += egg_section

    if moves["Tutor Moves"]:
        tutor_section = "\n\n:teacher: **Tutor Moves**\n" + separator.join(sorted(moves["Tutor Moves"]))
        if len(current_message) + len(tutor_section) > 2000:
            messages.append(current_message)
            current_message = tutor_section
        else:
            current_message += tutor_section

    if missing_level_up_moves:
        missing_section = "\n\n:question: **Learned in Game through level up, but not here**\n" + separator.join(sorted(missing_level_up_moves))
        if len(current_message) + len(missing_section) > 2000:
            messages.append(current_message)
            current_message = missing_section
        else:
            current_message += missing_section

    # Append the final message
    if current_message:
        messages.append(current_message)

    return messages





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
        if chain_id and pokemon_id in evolution_chain:
            evolution_chain = evolution_chain[:evolution_chain.index(pokemon_id) + 1]
        else:
            evolution_chain = []

    print(f"Evolution chain for Pokémon ID {pokemon_id}: {evolution_chain}")  # Debugging
    return evolution_chain

def reload_data():
    """Reloads CSV data into memory."""
    global moves_data, pokemon_moves_data, pokemon_move_methods_data, pokemon_base_data, evolution_chains
    moves_data.clear()
    pokemon_moves_data.clear()
    pokemon_move_methods_data.clear()
    pokemon_base_data.clear()
    evolution_chains.clear()
    load_csv_data()

def get_pokemon_moves(pokemon_name):
    """Retrieve and format rank moves for a Pokémon."""
    # Normalize the input name
    normalized_name = pokemon_name.lower().replace(' ', '-')
    pokemon_id = pokemon_name_to_id_map.get(normalized_name)

    if pokemon_id is None:
        return [f"Pokémon '{pokemon_name}' not found in pokemon.csv."]

    # Load Pokémon data
    pokemon_data = load_pokemon_data(pokemon_name)
    specific_moves = pokemon_data.get("moves", {})

    # Build the initial message
    messages = []
    current_message = f"### {pokemon_name.title()} [#{pokemon_id}]\n"

    # Include rank-based moves from new data
    if specific_moves:
        for rank in VALID_RANKS:
            rank_moves = specific_moves.get(rank, [])
            if rank_moves:
                emoji = RANK_EMOJIS.get(rank, "")
                rank_section = f"\n{emoji} **{rank}**\n" + " | ".join(sorted(rank_moves))
                if len(current_message) + len(rank_section) > 2000:
                    messages.append(current_message)
                    current_message = rank_section
                else:
                    current_message += rank_section
    else:
        # Handle Pokémon without new data format (old data or CSV)
        current_message += "\nNo rank-based moves available."

    # Append the final message
    if current_message:
        messages.append(current_message)

    return messages

def parse_stat_range(stat_range):
    """Parse stat range from 'min/max' format in new data."""
    min_stat, max_stat = map(int, stat_range.split("/"))
    return min_stat, max_stat

def parse_moves_new(moves):
    """Parse moves from the new JSON format and ensure rank names are consistent."""
    parsed_moves = {}
    for rank, move_list in moves.items():
        # Convert rank to title case to standardize (e.g., 'bronze' to 'Bronze')
        mapped_rank = rank.title()
        # Map the rank using RANK_MAPPING if necessary
        mapped_rank = RANK_MAPPING.get(mapped_rank, mapped_rank)
        # Check if the mapped rank is valid
        if mapped_rank not in VALID_RANKS:
            continue  # Skip unknown ranks
        parsed_moves.setdefault(mapped_rank, []).extend(move_list)
    return parsed_moves

def parse_moves_old(moves):
    """Parse moves in the old data format, applying rank mapping."""
    parsed_moves = {rank: [] for rank in VALID_RANKS}
    for move in moves:
        old_rank = move.get("Learned", "")
        new_rank = RANK_MAPPING.get(old_rank, "Bronze")
        if new_rank in VALID_RANKS:
            parsed_moves[new_rank].append(move.get("Name"))
        else:
            parsed_moves["Bronze"].append(move.get("Name"))
    return parsed_moves

# Example usage (for testing purposes)
if __name__ == "__main__":
    reload_data()
    # Get rank moves
    rank_moves_messages = get_pokemon_moves("Sneasler")
    print("\n".join(rank_moves_messages))
    # Get additional moves
    additional_moves_messages = get_additional_moves("Sneasler")
    print("\n".join(additional_moves_messages))
