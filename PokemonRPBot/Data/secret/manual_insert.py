import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
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
            "bronze": [], "silver": [], "gold": [], "platinum": [],
            "diamond": [], "tm": [], "tutor": [], "egg": [],
            "level1_g3_7": []
        }
        self.create_widgets()

    def create_widgets(self):
        # Notebook for organizing different sections
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Basic Info & Stats Section ---
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="General & Stats")

        info_frame = ttk.LabelFrame(basic_frame, text="General Information")
        info_frame.pack(fill="x", padx=10, pady=5)
        # Number, Name, Types...
        ttk.Label(info_frame, text="Number:").grid(row=0, column=0, sticky="e", padx=5)
        self.entry_number = ttk.Entry(info_frame); self.entry_number.grid(row=0, column=1)
        ttk.Label(info_frame, text="Name:").grid(row=1, column=0, sticky="e", padx=5)
        self.entry_name = ttk.Entry(info_frame); self.entry_name.grid(row=1, column=1)
        ttk.Label(info_frame, text="Types (comma separated):").grid(row=2, column=0, sticky="e", padx=5)
        self.entry_types = ttk.Entry(info_frame, width=50); self.entry_types.grid(row=2, column=1)

        abilities_frame = ttk.LabelFrame(info_frame, text="Abilities")
        abilities_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Label(abilities_frame, text="Normal (comma separated):").grid(row=0, column=0, sticky="e", padx=5)
        self.entry_normal_abilities = ttk.Entry(abilities_frame, width=50)
        self.entry_normal_abilities.grid(row=0, column=1)
        ttk.Label(abilities_frame, text="Hidden (comma separated):").grid(row=1, column=0, sticky="e", padx=5)
        self.entry_hidden_abilities = ttk.Entry(abilities_frame, width=50)
        self.entry_hidden_abilities.grid(row=1, column=1)

        stats_frame = ttk.LabelFrame(basic_frame, text="Stats (Enter base values)")
        stats_frame.pack(fill="x", padx=10, pady=5)
        # HP
        ttk.Label(stats_frame, text="HP:").grid(row=0, column=0, sticky="e", padx=5)
        self.entry_hp = ttk.Entry(stats_frame, width=10); self.entry_hp.grid(row=0, column=1)
        ttk.Label(stats_frame, text="Converted Base HP:").grid(row=0, column=2, sticky="e", padx=5)
        self.label_hp_conv = ttk.Label(stats_frame, text="N/A"); self.label_hp_conv.grid(row=0, column=3)
        # Attack → Strength
        ttk.Label(stats_frame, text="Attack:").grid(row=1, column=0, sticky="e", padx=5)
        self.entry_attack = ttk.Entry(stats_frame, width=10); self.entry_attack.grid(row=1, column=1)
        ttk.Label(stats_frame, text="Converted Strength:").grid(row=1, column=2, sticky="e", padx=5)
        self.label_attack_conv = ttk.Label(stats_frame, text="N/A"); self.label_attack_conv.grid(row=1, column=3)
        # Defense → Vitality
        ttk.Label(stats_frame, text="Defense:").grid(row=2, column=0, sticky="e", padx=5)
        self.entry_defense = ttk.Entry(stats_frame, width=10); self.entry_defense.grid(row=2, column=1)
        ttk.Label(stats_frame, text="Converted Vitality:").grid(row=2, column=2, sticky="e", padx=5)
        self.label_defense_conv = ttk.Label(stats_frame, text="N/A"); self.label_defense_conv.grid(row=2, column=3)
        # Sp. Atk → Special
        ttk.Label(stats_frame, text="Sp. Atk:").grid(row=3, column=0, sticky="e", padx=5)
        self.entry_spatk = ttk.Entry(stats_frame, width=10); self.entry_spatk.grid(row=3, column=1)
        ttk.Label(stats_frame, text="Converted Special:").grid(row=3, column=2, sticky="e", padx=5)
        self.label_spatk_conv = ttk.Label(stats_frame, text="N/A"); self.label_spatk_conv.grid(row=3, column=3)
        # Sp. Def → Insight
        ttk.Label(stats_frame, text="Sp. Def:").grid(row=4, column=0, sticky="e", padx=5)
        self.entry_spdef = ttk.Entry(stats_frame, width=10); self.entry_spdef.grid(row=4, column=1)
        ttk.Label(stats_frame, text="Converted Insight:").grid(row=4, column=2, sticky="e", padx=5)
        self.label_spdef_conv = ttk.Label(stats_frame, text="N/A"); self.label_spdef_conv.grid(row=4, column=3)
        # Speed → Dexterity
        ttk.Label(stats_frame, text="Speed:").grid(row=5, column=0, sticky="e", padx=5)
        self.entry_speed = ttk.Entry(stats_frame, width=10); self.entry_speed.grid(row=5, column=1)
        ttk.Label(stats_frame, text="Converted Dexterity:").grid(row=5, column=2, sticky="e", padx=5)
        self.label_speed_conv = ttk.Label(stats_frame, text="N/A"); self.label_speed_conv.grid(row=5, column=3)

        update_btn = ttk.Button(stats_frame, text="Update Stat Conversions", command=self.update_stats)
        update_btn.grid(row=6, column=0, columnspan=4, pady=5)

        # --- Moves Section ---
        moves_frame = ttk.Frame(notebook)
        notebook.add(moves_frame, text="Moves")

        moves_top = ttk.Frame(moves_frame)
        moves_top.pack(fill="x", padx=10, pady=5)
        ttk.Label(moves_top, text="Select move category:").grid(row=0, column=0, sticky="w", padx=5)
        self.move_category = tk.StringVar(value="bronze")
        for idx, cat in enumerate(self.moves_data.keys(), start=1):
            ttk.Radiobutton(moves_top, text=cat, variable=self.move_category, value=cat).grid(row=0, column=idx, padx=2)

        ttk.Label(moves_top, text="Move:").grid(row=1, column=0, sticky="e", padx=5)
        self.entry_move = ttk.Entry(moves_top, width=40); self.entry_move.grid(row=1, column=1, columnspan=2, sticky="w")
        ttk.Button(moves_top, text="Add Move", command=self.add_move).grid(row=1, column=3, padx=5)
        ttk.Button(moves_top, text="Remove Move", command=self.remove_move).grid(row=1, column=4, padx=5)

        self.moves_listbox = tk.Listbox(moves_frame, height=8)
        self.moves_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.move_category.trace_add("write", lambda *args: self.update_moves_listbox())

        # --- Bottom Section: Generate & Save JSON ---
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=10)
        ttk.Button(bottom, text="Generate JSON", command=self.generate_json).pack(side="left", padx=5)
        ttk.Button(bottom, text="Save JSON to File", command=self.save_json).pack(side="left", padx=5)

        self.json_text = tk.Text(self, height=10)
        self.json_text.pack(fill="both", expand=True, padx=10, pady=5)

    def update_stats(self):
        hp_val = self.entry_hp.get()
        self.label_hp_conv.config(text=str(calc_hp(hp_val)) if calc_hp(hp_val) is not None else "N/A")
        for entry, label in [
            (self.entry_attack, self.label_attack_conv),
            (self.entry_defense, self.label_defense_conv),
            (self.entry_spatk, self.label_spatk_conv),
            (self.entry_spdef, self.label_spdef_conv),
            (self.entry_speed, self.label_speed_conv),
        ]:
            val = entry.get()
            conv = calc_stat_ratio(val)
            label.config(text=conv if conv is not None else "N/A")

    def add_move(self):
        move = self.entry_move.get().strip()
        if not move:
            messagebox.showwarning("Input Error", "Please type a move before adding.")
            return
        cat = self.move_category.get()
        self.moves_data[cat].append(move)
        self.entry_move.delete(0, tk.END)
        self.update_moves_listbox()

    def remove_move(self):
        sel = list(self.moves_listbox.curselection())
        if not sel:
            messagebox.showwarning("Input Error", "Select a move to remove.")
            return
        cat = self.move_category.get()
        # remove in reverse index order
        for i in reversed(sel):
            self.moves_data[cat].pop(i)
        self.update_moves_listbox()

    def update_moves_listbox(self):
        cat = self.move_category.get()
        self.moves_listbox.delete(0, tk.END)
        for mv in self.moves_data[cat]:
            self.moves_listbox.insert(tk.END, mv)

    def generate_json(self):
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
        data = {
            "number": number,
            "name": name,
            "types": types,
            "abilities": abilities,
            "base_hp": calc_hp(self.entry_hp.get()),
            "strength": calc_stat_ratio(self.entry_attack.get()),
            "vitality": calc_stat_ratio(self.entry_defense.get()),
            "special": calc_stat_ratio(self.entry_spatk.get()),
            "insight": calc_stat_ratio(self.entry_spdef.get()),
            "dexterity": calc_stat_ratio(self.entry_speed.get()),
            "moves": self.moves_data
        }
        out = json.dumps(data, indent=4)
        self.json_text.delete("1.0", tk.END)
        self.json_text.insert(tk.END, out)

    def save_json(self):
        # Regenerate JSON in the text widget
        self.generate_json()
        json_str = self.json_text.get("1.0", tk.END).strip()
        if not json_str:
            messagebox.showwarning("No Data", "Generate the JSON first.")
            return
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Please enter a Pokémon name before saving.")
            return

        # Always save to script's directory, named "<PokemonName>.json"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, f"{name}.json")
        try:
            with open(file_path, "w") as f:
                f.write(json_str)
            messagebox.showinfo("Saved", f"JSON saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file:\n{e}")

# --- Run the Application ---
if __name__ == "__main__":
    app = PokemonDataEntryApp()
    app.mainloop()
