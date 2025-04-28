import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from decimal import Decimal, ROUND_HALF_UP

# --- Helper Functions ---
def round_half_up(x):
    """Round x to the nearest integer with .5 rounding up."""
    return int(Decimal(x).to_integral_value(rounding=ROUND_HALF_UP))

def calc_hp(raw_hp):
    """
    Calculate base_hp: formula is (raw_hp/20 + 1) with round-half-up.
    Returns an integer.
    """
    try:
        raw_hp = float(raw_hp)
    except ValueError:
        return None
    return round_half_up(raw_hp / 20 + 1)

def calc_stat_ratio(raw_stat):
    """
    Calculate the stat ratio based on the rule:
    - Denom = round_half_up(raw_stat/20 + 1)
    - Numerator = half of denom (using integer division)
    Returns a string in the format "numerator/denom".
    """
    try:
        raw_stat = float(raw_stat)
    except ValueError:
        return None
    denom = round_half_up(raw_stat / 20 + 1)
    numerator = denom // 2  # integer division for rounding down
    return f"{numerator}/{denom}"

# --- Main Application Class ---
class PokemonDataEntryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pokémon Data Entry")
        self.geometry("800x600")
        self.moves_data = {
            "bronze": [],
            "silver": [],
            "gold": [],
            "platinum": [],
            "diamond": [],
            "tm": [],
            "tutor": [],
            "egg": [],
            "level1_g3_7": []
        }
        self.create_widgets()

    def create_widgets(self):
        # Notebook for organizing different sections
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Frame for Basic Info & Stats
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="General & Stats")
        
        # Frame for Moves
        moves_frame = ttk.Frame(notebook)
        notebook.add(moves_frame, text="Moves")
        
        # --- Basic Info & Stats Section ---
        # General Information Frame
        info_frame = ttk.LabelFrame(basic_frame, text="General Information")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Pokémon number
        ttk.Label(info_frame, text="Number:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entry_number = ttk.Entry(info_frame)
        self.entry_number.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Pokémon name
        ttk.Label(info_frame, text="Name:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entry_name = ttk.Entry(info_frame)
        self.entry_name.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Pokémon types (comma separated)
        ttk.Label(info_frame, text="Types (comma separated):").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.entry_types = ttk.Entry(info_frame, width=50)
        self.entry_types.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Abilities frame
        abilities_frame = ttk.LabelFrame(info_frame, text="Abilities")
        abilities_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        # Normal Abilities
        ttk.Label(abilities_frame, text="Normal (comma separated):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entry_normal_abilities = ttk.Entry(abilities_frame, width=50)
        self.entry_normal_abilities.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        # Hidden Abilities
        ttk.Label(abilities_frame, text="Hidden (comma separated):").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entry_hidden_abilities = ttk.Entry(abilities_frame, width=50)
        self.entry_hidden_abilities.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(basic_frame, text="Stats (Enter base values)")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        # HP
        ttk.Label(stats_frame, text="HP:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entry_hp = ttk.Entry(stats_frame, width=10)
        self.entry_hp.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(stats_frame, text="Converted Base HP:").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        self.label_hp_conv = ttk.Label(stats_frame, text="N/A")
        self.label_hp_conv.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Attack → Strength
        ttk.Label(stats_frame, text="Attack:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entry_attack = ttk.Entry(stats_frame, width=10)
        self.entry_attack.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(stats_frame, text="Converted Strength:").grid(row=1, column=2, sticky="e", padx=5, pady=2)
        self.label_attack_conv = ttk.Label(stats_frame, text="N/A")
        self.label_attack_conv.grid(row=1, column=3, sticky="w", padx=5, pady=2)
        
        # Defense → Vitality
        ttk.Label(stats_frame, text="Defense:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.entry_defense = ttk.Entry(stats_frame, width=10)
        self.entry_defense.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(stats_frame, text="Converted Vitality:").grid(row=2, column=2, sticky="e", padx=5, pady=2)
        self.label_defense_conv = ttk.Label(stats_frame, text="N/A")
        self.label_defense_conv.grid(row=2, column=3, sticky="w", padx=5, pady=2)
        
        # SpAtk → Special
        ttk.Label(stats_frame, text="Sp. Atk:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.entry_spatk = ttk.Entry(stats_frame, width=10)
        self.entry_spatk.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(stats_frame, text="Converted Special:").grid(row=3, column=2, sticky="e", padx=5, pady=2)
        self.label_spatk_conv = ttk.Label(stats_frame, text="N/A")
        self.label_spatk_conv.grid(row=3, column=3, sticky="w", padx=5, pady=2)
        
        # SpDef → Insight
        ttk.Label(stats_frame, text="Sp. Def:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.entry_spdef = ttk.Entry(stats_frame, width=10)
        self.entry_spdef.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(stats_frame, text="Converted Insight:").grid(row=4, column=2, sticky="e", padx=5, pady=2)
        self.label_spdef_conv = ttk.Label(stats_frame, text="N/A")
        self.label_spdef_conv.grid(row=4, column=3, sticky="w", padx=5, pady=2)
        
        # Speed → Dexterity
        ttk.Label(stats_frame, text="Speed:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.entry_speed = ttk.Entry(stats_frame, width=10)
        self.entry_speed.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(stats_frame, text="Converted Dexterity:").grid(row=5, column=2, sticky="e", padx=5, pady=2)
        self.label_speed_conv = ttk.Label(stats_frame, text="N/A")
        self.label_speed_conv.grid(row=5, column=3, sticky="w", padx=5, pady=2)
        
        # Button to update converted stats
        update_btn = ttk.Button(stats_frame, text="Update Stat Conversions", command=self.update_stats)
        update_btn.grid(row=6, column=0, columnspan=4, pady=5)
        
        # --- Moves Section ---
        moves_top_frame = ttk.Frame(moves_frame)
        moves_top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(moves_top_frame, text="Select move category:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.move_category = tk.StringVar(value="bronze")
        categories = ["bronze", "silver", "gold", "platinum", "diamond", "tm", "tutor", "egg", "level1_g3_7"]
        col = 1
        for cat in categories:
            rb = ttk.Radiobutton(moves_top_frame, text=cat, variable=self.move_category, value=cat)
            rb.grid(row=0, column=col, padx=2, pady=2)
            col += 1
        
        # Entry to add a move
        ttk.Label(moves_top_frame, text="Move:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.entry_move = ttk.Entry(moves_top_frame, width=40)
        self.entry_move.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="w")
        add_move_btn = ttk.Button(moves_top_frame, text="Add Move", command=self.add_move)
        add_move_btn.grid(row=1, column=4, padx=5, pady=2)
        
        # Listbox to show moves for the currently selected category
        self.moves_listbox = tk.Listbox(moves_frame, height=8)
        self.moves_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.move_category.trace_add("write", lambda *args: self.update_moves_listbox())
        
        # --- Bottom Section: Generate JSON ---
        gen_frame = ttk.Frame(self)
        gen_frame.pack(fill="x", padx=10, pady=10)
        gen_btn = ttk.Button(gen_frame, text="Generate JSON", command=self.generate_json)
        gen_btn.pack(side="left", padx=5)
        save_btn = ttk.Button(gen_frame, text="Save JSON to File", command=self.save_json)
        save_btn.pack(side="left", padx=5)
        
        # Output text area to show JSON
        self.json_text = tk.Text(self, height=10)
        self.json_text.pack(fill="both", expand=True, padx=10, pady=5)
        
    def update_stats(self):
        """Recalculate converted stats and update the labels."""
        # Update HP conversion
        hp_val = self.entry_hp.get()
        base_hp = calc_hp(hp_val)
        self.label_hp_conv.config(text=str(base_hp) if base_hp is not None else "N/A")
        
        # Non-HP stats use calc_stat_ratio without a bonus parameter:
        atk_val = self.entry_attack.get()
        strength = calc_stat_ratio(atk_val)
        self.label_attack_conv.config(text=strength if strength is not None else "N/A")
        
        def_val = self.entry_defense.get()
        vitality = calc_stat_ratio(def_val)
        self.label_defense_conv.config(text=vitality if vitality is not None else "N/A")
        
        spatk_val = self.entry_spatk.get()
        special = calc_stat_ratio(spatk_val)
        self.label_spatk_conv.config(text=special if special is not None else "N/A")
        
        spdef_val = self.entry_spdef.get()
        insight = calc_stat_ratio(spdef_val)
        self.label_spdef_conv.config(text=insight if insight is not None else "N/A")
        
        speed_val = self.entry_speed.get()
        dexterity = calc_stat_ratio(speed_val)
        self.label_speed_conv.config(text=dexterity if dexterity is not None else "N/A")
        
    def add_move(self):
        """Add a move to the selected category."""
        move = self.entry_move.get().strip()
        if move:
            category = self.move_category.get()
            self.moves_data[category].append(move)
            self.entry_move.delete(0, tk.END)
            self.update_moves_listbox()
        else:
            messagebox.showwarning("Input Error", "Please type a move before adding.")
            
    def update_moves_listbox(self):
        """Update the moves listbox for the current category."""
        category = self.move_category.get()
        self.moves_listbox.delete(0, tk.END)
        for move in self.moves_data.get(category, []):
            self.moves_listbox.insert(tk.END, move)
    
    def generate_json(self):
        """Gather all the data and generate JSON output."""
        try:
            number = int(self.entry_number.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Number must be an integer.")
            return
        name = self.entry_name.get().strip()
        types = [t.strip() for t in self.entry_types.get().split(",") if t.strip()]
        abilities = {
            "normal": [a.strip() for a in self.entry_normal_abilities.get().split(",") if a.strip()],
            "hidden": [a.strip() for a in self.entry_hidden_abilities.get().split(",") if a.strip()]
        }
        # Compute stats using our helper functions:
        base_hp = calc_hp(self.entry_hp.get())
        strength = calc_stat_ratio(self.entry_attack.get())
        vitality = calc_stat_ratio(self.entry_defense.get())
        special = calc_stat_ratio(self.entry_spatk.get())
        insight = calc_stat_ratio(self.entry_spdef.get())
        dexterity = calc_stat_ratio(self.entry_speed.get())
        
        pokemon_data = {
            "number": number,
            "name": name,
            "types": types,
            "abilities": abilities,
            "base_hp": base_hp,
            "strength": strength,
            "vitality": vitality,
            "special": special,
            "insight": insight,
            "dexterity": dexterity,
            "moves": self.moves_data
        }
        
        json_output = json.dumps(pokemon_data, indent=4)
        self.json_text.delete("1.0", tk.END)
        self.json_text.insert(tk.END, json_output)
        
    def save_json(self):
        """Save the generated JSON to a file."""
        self.generate_json()
        json_str = self.json_text.get("1.0", tk.END).strip()
        if not json_str:
            messagebox.showwarning("No Data", "Generate the JSON first.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, "w") as f:
                f.write(json_str)
            messagebox.showinfo("Saved", f"JSON saved to {file_path}")

# --- Run the Application ---
if __name__ == "__main__":
    app = PokemonDataEntryApp()
    app.mainloop()
