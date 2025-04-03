from utils.logger import logger
from config import ROOT_DIR, KCD2_DIR
from constants import ITEM_CATEGORIES, UI_SLOTS, ARMOR_TYPES, WEAPON_TYPES, DICE_BADGE_TYPES, DICE_BADGE_SUBTYPES
import json

data = {
    "version": {
        "Id": 0,
        "Name": ""
    },
    "categories": [],
    "ui_slots": [],
    "categories": [],
    "weapon_types": [],
    "armor_types": [],
    "dice_badges": {
        "types": [],
        "subtypes": [],
    },
    "items": {
        "head": [],
        "jewelry": [],
        "dagger": [],
        "belt": [],
        "torso": [],
        "hands": [],
        "legs": [],
        "pouch": [],
        "horse": [],
        "melee": [],
        "ranged": [],
        "shield": [],
        "die": [],
        "diceBadge": []
    }
}

# Populate all fields from constants
data["categories"] = ITEM_CATEGORIES
data["ui_slots"] = UI_SLOTS
data["weapon_types"] = WEAPON_TYPES
data["armor_types"] = ARMOR_TYPES
data["dice_badges"]["types"] = {str(t["id"]): t["name"] for t in DICE_BADGE_TYPES if t["id"] >= 0}
data["dice_badges"]["subtypes"] = {str(t["id"]): t["name"] for t in DICE_BADGE_SUBTYPES}

# Write the data dictionary to a text file in JSON format
with open("templates/data.template.txt", "w") as file:
    json.dump(data, file, indent=4)