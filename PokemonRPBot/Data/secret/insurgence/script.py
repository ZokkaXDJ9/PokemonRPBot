import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
import json
from decimal import Decimal, ROUND_HALF_UP
import re

# --- Helper Functions ---
def round_half_up(x):
    return int(Decimal(x).to_integral_value(rounding=ROUND_HALF_UP))

def calc_hp(raw_hp):
    try:
        raw = float(raw_hp)
    except (ValueError, TypeError):
        return None
    return round_half_up(raw / 20 + 1)

def calc_stat_ratio(raw_stat):
    try:
        raw = float(raw_stat)
    except (ValueError, TypeError):
        return None
    denom = round_half_up(raw / 20 + 1)
    numerator = denom // 2
    return f"{numerator}/{denom}"

# --- Scraping Logic ---
def scrape_pokemon(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Locate main infobox table
    info = soup.find('table', class_=lambda c: c and 'roundy' in c)
    if not info:
        raise ValueError("Could not find Pokémon infobox on the page.")

    data = {}
    # --- Name & Number ---
    header_big = info.find('big')
    data['name'] = header_big.find('b').text.strip() if header_big and header_big.find('b') else None
    num_span = info.find('span', string=re.compile(r"#\d+"))
    try:
        data['number'] = int(num_span.text.strip().lstrip('#')) if num_span else None
    except ValueError:
        data['number'] = None

    # --- Types ---
    types = []
    type_header = info.find('b', string=re.compile(r"Type"))
    if type_header:
        td = type_header.find_parent(['td', 'th'])
        if td:
            # outer table containing type icons
            outer_tbl = td.find('table', class_=lambda c: c and 'roundy' in c)
            if outer_tbl:
                # first <tr> holds each type cell
                row = outer_tbl.find('tr')
                if row:
                    for cell in row.find_all('td', recursive=False):
                        # skip hidden cells
                        style = cell.get('style', '') or ''
                        if 'display:none' in style.replace(' ', '').lower():
                            continue
                        # inner table for the icon/text
                        inner_tbl = cell.find('table', recursive=False)
                        if not inner_tbl:
                            continue
                        # pull the first <b> tag inside for the type name
                        b = inner_tbl.find('b')
                        if b:
                            t = b.text.strip()
                            if t and t.lower() != 'unknown':
                                types.append(t)
    data['types'] = list(dict.fromkeys(types))  # dedupe

    # --- Abilities ---
    abilities = {'normal': [], 'hidden': []}
    ab_header = info.find('b', string=re.compile(r"Ability"))
    if ab_header:
        td = ab_header.find_parent('td')
        if td:
            ab_table = td.find('table') or td.find_next_sibling('table')
            if ab_table:
                for cell in ab_table.select('td'):
                    if 'display:none' in (cell.get('style') or '').lower():
                        continue
                    a_tag = cell.find('a')
                    if not a_tag:
                        continue
                    name = a_tag.text.strip()
                    small = cell.find('small')
                    if small and 'hidden' in small.text.lower():
                        abilities['hidden'].append(name)
                    else:
                        abilities['normal'].append(name)
    data['abilities'] = abilities

    # --- Stats ---
    stats = {}
    stat_th = soup.find(lambda tag: tag.name == 'th' and tag.get_text(strip=True).startswith('Stat'))
    if stat_th:
        stat_table = stat_th.find_parent('table')
        rows = stat_table.find_all('tr')
        for row in rows[2:8]:  # HP, Atk, Def, Sp.Atk, Sp.Def, Speed
            inner_td = row.find('td')
            nested = inner_td.find('table') if inner_td else None
            if nested:
                cells = nested.find_all('th')
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).rstrip(':').lower()
                    stats[key] = cells[1].get_text(strip=True)
    data['base_hp']   = calc_hp(stats.get('hp'))
    data['strength']  = calc_stat_ratio(stats.get('attack'))
    data['vitality']  = calc_stat_ratio(stats.get('defense'))
    data['special']   = calc_stat_ratio(stats.get('sp.atk') or stats.get('spatk') or stats.get('sp atk'))
    data['insight']   = calc_stat_ratio(stats.get('sp.def') or stats.get('spdef') or stats.get('sp def'))
    data['dexterity'] = calc_stat_ratio(stats.get('speed'))

    # --- Moves ---
    moves = {k: [] for k in ['bronze','silver','gold','platinum','diamond','tm','tutor','egg']}
    # Find the Moves section
    moves_section = soup.find('span', id=re.compile(r"Moves", re.I))
    if moves_section:
        current = moves_section.parent
        # traverse siblings until next major section
        while True:
            current = current.find_next_sibling()
            if not current or current.name in ['h2', 'h1']:
                break
            if current.name == 'table':
                # determine category from first header cell
                hdr = current.find('th')
                if hdr:
                    cat = hdr.get_text(strip=True).lower()
                    key = cat
                    # normalize to our keys
                    if 'bronze' in key or 'level-up' in key:
                        key = 'bronze'
                    elif 'silver' in key:
                        key = 'silver'
                    elif 'gold' in key:
                        key = 'gold'
                    elif 'platinum' in key:
                        key = 'platinum'
                    elif 'diamond' in key:
                        key = 'diamond'
                    elif 'tm' in key:
                        key = 'tm'
                    elif 'tutor' in key:
                        key = 'tutor'
                    elif 'egg' in key:
                        key = 'egg'
                    if key in moves:
                        for row in current.find_all('tr')[1:]:
                            cols = row.find_all(['td','th'])
                            if len(cols) >= 2:
                                mv = cols[1].get_text(strip=True)
                                if mv:
                                    moves[key].append(mv)
    data['moves'] = moves

    return data

# --- GUI Application ---
class PokeScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("P-Insurgence Pokémon JSON Scraper")
        self.geometry("750x550")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill='x', padx=10, pady=8)
        ttk.Label(frm, text="Wiki URL:").pack(side='left')
        self.url_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.url_var, width=60).pack(side='left', padx=5)
        ttk.Button(frm, text="Fetch JSON", command=self.on_fetch).pack(side='left')

        self.json_text = scrolledtext.ScrolledText(self, wrap='word', font=('Consolas', 10))
        self.json_text.pack(expand=True, fill='both', padx=10, pady=10)

    def on_fetch(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a Pokémon page URL.")
            return
        try:
            data = scrape_pokemon(url)
            self.json_text.delete('1.0', tk.END)
            self.json_text.insert(tk.END, json.dumps(data, indent=4))
        except Exception as e:
            messagebox.showerror("Scrape Error", f"Failed to scrape data: {e}")

if __name__ == '__main__':
    app = PokeScraperApp()
    app.mainloop()
