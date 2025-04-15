import tkinter as tk
import json
import os
from tkinter import messagebox

# Mapping of radio button labels to the specified folder paths.
FOLDER_CHOICES = {
    "Abilities": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\abilities",
    "Items": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\items",
    "Legend Moves": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\legend_moves",
    "Moves": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\moves",
    "Potions": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\potions",
    "Rules": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\rules",
    "Status": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\status",
    "Weather": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\weather",
    "Z Moves": r"C:\Users\Bahamut\Desktop\PokeBotPython\PokemonRPBot\PokemonRPBot\Data\z_moves"
}

class FileSaverApp:
    def __init__(self, master):
        self.master = master
        master.title("JSON File Saver")

        # Label for the text field.
        self.label = tk.Label(master, text="Enter your JSON below:")
        self.label.pack(pady=(10, 0))

        # Multiline text field for JSON input.
        self.text_field = tk.Text(master, height=10, width=50)
        self.text_field.pack(padx=10, pady=10)

        # Frame for the radio buttons.
        self.radio_frame = tk.Frame(master)
        self.radio_frame.pack(padx=10, pady=5, anchor='w')

        # Label for folder selection.
        self.radio_label = tk.Label(self.radio_frame, text="Select destination folder:")
        self.radio_label.pack(anchor='w')

        # Tkinter variable for holding the selected folder path.
        self.selected_folder = tk.StringVar(value=list(FOLDER_CHOICES.values())[0])
        
        # Create a radio button for each folder option.
        for label, folder in FOLDER_CHOICES.items():
            radio = tk.Radiobutton(self.radio_frame, text=label, variable=self.selected_folder, value=folder)
            radio.pack(anchor='w')

        # Save button.
        self.save_button = tk.Button(master, text="Save", command=self.save_file)
        self.save_button.pack(pady=(5, 15))

    def save_file(self):
        # Retrieve and strip text from the text field.
        text_content = self.text_field.get("1.0", tk.END).strip()

        # Validate that the input is valid JSON.
        try:
            data = json.loads(text_content)
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON input. Please enter valid JSON.\n{e}")
            return

        # Check for the presence of the "name" key.
        if "name" not in data:
            messagebox.showerror("Error", "JSON must include a 'name' key for the filename.")
            return

        # Ensure the "name" value is a string.
        if not isinstance(data["name"], str):
            messagebox.showerror("Error", "The 'name' key must be a string.")
            return

        # Use the "name" key to construct the file name.
        filename = data["name"]
        if not filename.endswith(".json"):
            filename += ".json"

        # Get the selected folder path.
        folder = self.selected_folder.get()
        
        # Ensure the target folder exists; create it if it doesn't.
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder '{folder}': {e}")
                return

        # Define the full file path.
        file_path = os.path.join(folder, filename)
        
        # Save the JSON data to the file.
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            # Clear the text field after saving without showing a confirmation message.
            self.text_field.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSaverApp(root)
    root.mainloop()
