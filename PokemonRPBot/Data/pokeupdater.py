import os
import json
import glob
import requests

def get_ability_english_name(ability_url, cache):
    """
    Retrieve the ability's English name from its detailed API endpoint.
    Uses a cache to avoid repeat requests.
    """
    if ability_url in cache:
        return cache[ability_url]
    
    response = requests.get(ability_url)
    if response.status_code != 200:
        # Fallback: use the ability slug from the URL
        name = ability_url.split('/')[-2] if ability_url.endswith('/') else ability_url.split('/')[-1]
        cache[ability_url] = name
        return name
    
    ability_data = response.json()
    english_name = None
    for name_entry in ability_data.get('names', []):
        if name_entry.get('language', {}).get('name') == 'en':
            english_name = name_entry.get('name')
            break

    # Fallback to the default "name" field if English name not found.
    if not english_name:
        english_name = ability_data.get('name')
    
    cache[ability_url] = english_name
    return english_name

def update_pokemon_json(folder_path):
    # List to track Pokémon that weren't found via the API.
    not_found = []
    # Cache for ability details to avoid duplicate API requests.
    ability_cache = {}

    # Find all JSON files in the specified folder.
    json_files = glob.glob(os.path.join(folder_path, '*.json'))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        # Use the Pokémon name to query the API. We use lower case for the API URL.
        pokemon_name = data.get('name')
        if not pokemon_name:
            print(f"Skipping {file_path}: 'name' field not found.")
            continue

        api_url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}'
        response = requests.get(api_url)
        
        if response.status_code != 200:
            print(f"Error retrieving data for {pokemon_name} (Status code: {response.status_code}). Adding empty keys.")
            not_found.append(pokemon_name)
            types = []
            abilities = {"normal": [], "hidden": []}
        else:
            poke_data = response.json()
            
            # Extract types. We'll capitalize the first letter of each type.
            types = [t['type']['name'].capitalize() for t in poke_data.get('types', [])]

            # Extract abilities and separate them into normal and hidden using detailed API info.
            normal_abilities = []
            hidden_abilities = []
            for ability in poke_data.get('abilities', []):
                ability_url = ability['ability']['url']
                # Get the proper English name for the ability.
                english_name = get_ability_english_name(ability_url, ability_cache)
                if ability.get('is_hidden'):
                    hidden_abilities.append(english_name)
                else:
                    normal_abilities.append(english_name)
            abilities = {
                "normal": normal_abilities,
                "hidden": hidden_abilities
            }

        # Rebuild the JSON so that "types" and "abilities" appear before "moves"
        new_data = {}
        inserted = False
        for key, value in data.items():
            if key == "moves" and not inserted:
                new_data["types"] = types
                new_data["abilities"] = abilities
                inserted = True
            new_data[key] = value
        
        # If no "moves" key was found, just append the new keys at the end.
        if not inserted:
            new_data["types"] = types
            new_data["abilities"] = abilities

        # Write the updated data back to the file.
        try:
            with open(file_path, 'w') as f:
                json.dump(new_data, f, indent=4)
            print(f"Updated {file_path}")
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")

    # Save the not found Pokémon list to a new file.
    if not_found:
        not_found_file = os.path.join(folder_path, "not_found.json")
        try:
            with open(not_found_file, 'w') as f:
                json.dump(not_found, f, indent=4)
            print(f"Saved not found Pokémon to {not_found_file}")
        except Exception as e:
            print(f"Error writing not found file: {e}")

if __name__ == '__main__':
    folder_path = input("Enter the folder path containing Pokémon JSON files: ").strip()
    if os.path.isdir(folder_path):
        update_pokemon_json(folder_path)
    else:
        print("The provided path is not a valid directory.")
