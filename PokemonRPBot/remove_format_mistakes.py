import os
import json

# Define the mapping from the incorrect move strings to the correct ones.
move_mapping = {
    "Smoke Screen": "Smokescreen",
}

def remove_duplicates_preserve_order(seq):
    """Remove duplicates from a list while preserving order."""
    seen = set()
    new_seq = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            new_seq.append(item)
    return new_seq

def process_file(file_path):
    """Load a JSON file, fix move names, remove duplicates, and return the updated data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # If there is a moves section, process each category within it.
    if "moves" in data:
        for category, moves_list in data["moves"].items():
            updated_moves = []
            for move in moves_list:
                # Replace the move name if it is found in our mapping.
                if move in move_mapping:
                    updated_moves.append(move_mapping[move])
                else:
                    updated_moves.append(move)
            # Remove duplicates and update the category.
            updated_moves = remove_duplicates_preserve_order(updated_moves)
            # Double-check: assert that no duplicates remain.
            if len(updated_moves) != len(set(updated_moves)):
                print(f"Warning: duplicates still found in category '{category}' for file {file_path}")
            data["moves"][category] = updated_moves

    return data

def main():
    # Update this folder path to point to the location of your JSON files.
    folder_path = r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\movelists"

    # Iterate over every file in the folder.
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            updated_data = process_file(file_path)
            # Write the updated JSON back to the file, pretty-printing with an indent.
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=4)
            print(f"Processed {filename} successfully.")

if __name__ == '__main__':
    main()
