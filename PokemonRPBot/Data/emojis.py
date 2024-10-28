# Define emojis for types
type_emojis = {
    "Grass": "<:typegrass:1272535959677960222>",
    "Fire": "<:typefire:1272535959677960223>",
    "Water": "<:typewater:1272535959677960224>",
    # Add other types as needed
}

# Define emojis for categories
category_emojis = {
    "Special": "<:movespecial:1272535937104220180>",
    "Physical": "<:movephysical:1272535937104220181>",
    "Status": "<:movestatus:1272535937104220182>",
    # Add other categories as needed
}

def get_type_emoji(type_name):
    """Get the emoji for a specific type."""
    return type_emojis.get(type_name, "")

def get_category_emoji(category_name):
    """Get the emoji for a specific move category."""
    return category_emojis.get(category_name, "")
