# ITEM_CATEGORIES, UI_SLOTS, ARMOR_TYPES, WEAPON_TYPES, DICE_BADGE_TYPES, DICE_BADGE_SUBTYPES

ICON_CATEGORIES = [
    {"id": -1, "name": "undefined"},
    {"id":  0, "name": "head"     },
    {"id":  1, "name": "torso"    },
    {"id":  2, "name": "hands"    },
    {"id":  3, "name": "legs"     },
    {"id":  4, "name": "horse"    },
    {"id":  5, "name": "weapon"   },
    {"id":  6, "name": "dice"     },
    {"id":  7, "name": "misc"     },
]

# Set to -1 to ensure error is thrown later and I look at it
# Logic will be needed to equalize icons to icon categories later
ITEM_CATEGORIES = [
    {"id": -1, "name": "undefined", "iconCategory": -1},
    {"id":  0, "name": "head",      "iconCategory": -1},
    {"id":  1, "name": "jewelry",   "iconCategory": -1},
    {"id":  2, "name": "dagger",    "iconCategory": -1},
    {"id":  3, "name": "belt",      "iconCategory": -1},
    {"id":  4, "name": "torso",     "iconCategory": -1},
    {"id":  5, "name": "hands",     "iconCategory": -1},
    {"id":  6, "name": "legs",      "iconCategory": -1},
    {"id":  7, "name": "pouch",     "iconCategory": -1},
    {"id":  8, "name": "horse",     "iconCategory": -1},
    {"id":  9, "name": "melee",     "iconCategory": -1},
    {"id": 10, "name": "ranged",    "iconCategory": -1},
    {"id": 11, "name": "shield",    "iconCategory": -1},
    {"id": 12, "name": "die",       "iconCategory": -1},
    {"id": 13, "name": "diceBadge", "iconCategory": -1},    
]


'''
The currently proposed icon categories are as follows:
ITEM_CATEGORIES = [
    {"id": -1, "name": "undefined", "iconCategory": -1},
    {"id":  0, "name": "head",      "iconCategory":  0},
    {"id":  1, "name": "jewelry",   "iconCategory":  7},
    {"id":  2, "name": "dagger",    "iconCategory":  7},
    {"id":  3, "name": "belt",      "iconCategory":  7},
    {"id":  4, "name": "torso",     "iconCategory":  1},
    {"id":  5, "name": "hands",     "iconCategory":  2},
    {"id":  6, "name": "legs",      "iconCategory":  3},
    {"id":  7, "name": "pouch",     "iconCategory":  7},
    {"id":  8, "name": "horse",     "iconCategory":  4},
    {"id":  9, "name": "melee",     "iconCategory":  5},
    {"id": 10, "name": "ranged",    "iconCategory":  5},
    {"id": 11, "name": "shield",    "iconCategory":  5},
    {"id": 12, "name": "die",       "iconCategory":  6},
    {"id": 13, "name": "diceBadge", "iconCategory":  6},
]
'''


UI_SLOTS = [
    {"id": -1, "name": "undefined",     "uiCategory": -1, "tooltip": "Undefined"                    },
    {"id": 0,  "name": "cap",           "uiCategory": 0,  "tooltip": "Head — Cap or Helmet"         },
    {"id": 1,  "name": "coif",          "uiCategory": 0,  "tooltip": "Head — Coif or Padded Coif"   },
    {"id": 2,  "name": "hood",          "uiCategory": 0,  "tooltip": "Head — Hood"                  },
    {"id": 3,  "name": "collar",        "uiCategory": 0,  "tooltip": "Head — Collar"                },
    {"id": 4,  "name": "ring",          "uiCategory": 1,  "tooltip": "Jewelry — Ring"               },
    {"id": 5,  "name": "necklace",      "uiCategory": 1,  "tooltip": "Jewelry — Necklace"           },
    {"id": 6,  "name": "dagger",        "uiCategory": 2,  "tooltip": "Dagger — Dagger"              },
    {"id": 7,  "name": "belt",          "uiCategory": 3,  "tooltip": "Belt — Belt"                  },
    {"id": 8,  "name": "plate",         "uiCategory": 4,  "tooltip": "Body — Plate"                 },
    {"id": 9,  "name": "coat",          "uiCategory": 4,  "tooltip": "Body — Coat"                  },
    {"id": 10, "name": "cloth",         "uiCategory": 4,  "tooltip": "Body — Tunic or Gambeson"     },
    {"id": 11, "name": "chainmail",     "uiCategory": 4,  "tooltip": "Body — Chainmail"             },
    {"id": 12, "name": "gloves",        "uiCategory": 5,  "tooltip": "Hands — Gloves"               },
    {"id": 13, "name": "sleeves",       "uiCategory": 5,  "tooltip": "Hands — Sleeves"              },
    {"id": 14, "name": "trousers",      "uiCategory": 6,  "tooltip": "Legs — Hose or Padded Hose"   },
    {"id": 15, "name": "legArmor",      "uiCategory": 6,  "tooltip": "Legs — Cuisses"               },
    {"id": 16, "name": "boot",          "uiCategory": 6,  "tooltip": "Legs — Shoes"                 },
    {"id": 17, "name": "spur",          "uiCategory": 6,  "tooltip": "Legs — Spurs"                 },
    {"id": 18, "name": "pouch",         "uiCategory": 7,  "tooltip": "Body — Pouch"                 },
    {"id": 19, "name": "horseHead",     "uiCategory": 8,  "tooltip": "Tack — Bridle"                },
    {"id": 20, "name": "horseTorso",    "uiCategory": 8,  "tooltip": "Tack — Torso"                 },
    {"id": 21, "name": "horseSaddle",   "uiCategory": 8,  "tooltip": "Tack — Saddle"                },
    {"id": 22, "name": "horseshoe",     "uiCategory": 8,  "tooltip": "Tack — Horseshoe"             },
    {"id": 23, "name": "weaponMelee",   "uiCategory": 9,  "tooltip": "Weapon — Melee"               },
    {"id": 24, "name": "weaponRanged",  "uiCategory": 10, "tooltip": "Weapon — Ranged"              },
    {"id": 25, "name": "shield",        "uiCategory": 11, "tooltip": "Weapon — Shield"              },
]

ARMOR_TYPES = [
    {"id": -1, "name": "undefined",          "uiSlot": -1, "filters": []                                                                                                               },
    {"id": 0,  "name": "headCap",            "uiSlot": 0,  "filters": ["Cap", "F_Hood", "F_Bonnet", "F_CapAndWimple", "F_Hat", "F_HoodOpen", "F_Veil", "F_VeilAndWimple", "LeatherCap"]},
    {"id": 1,  "name": "headHelmet",         "uiSlot": 0,  "filters": ["KettleHat", "SkullCap", "BascinetOpen", "BascinetVisor"]                                                       },
    {"id": 2,  "name": "headCoif",           "uiSlot": 1,  "filters": ["CoifCap"]                                                                                                      },
    {"id": 3,  "name": "headCoifPadded",     "uiSlot": 1,  "filters": ["CoifSmall", "CoifLarge", "CoifMail"]                                                                           },
    {"id": 4,  "name": "headHood",           "uiSlot": 2,  "filters": ["Hood"]                                                                                                         },
    {"id": 5,  "name": "collar",             "uiSlot": 3,  "filters": ["Collar"]                                                                                                       },
    {"id": 6,  "name": "ring",               "uiSlot": 4,  "filters": ["Ring"]                                                                                                         },
    {"id": 7,  "name": "necklace",           "uiSlot": 5,  "filters": ["Necklace"]                                                                                                     },
    {"id": 8,  "name": "belt",               "uiSlot": 7,  "filters": ["Belt"]                                                                                                         },
    {"id": 9,  "name": "bodyPlate",          "uiSlot": 8,  "filters": ["Brigandine", "Cuirass"]                                                                                        },
    {"id": 10, "name": "bodyCoat",           "uiSlot": 9,  "filters": ["Coat"]                                                                                                         },
    {"id": 11, "name": "bodyCloth",          "uiSlot": 10, "filters": ["TunicShort", "TunicLong", "F_SimpleDress", "F_Smock", "LeatherApron"]                                          },
    {"id": 12, "name": "bodyClothPadded",    "uiSlot": 10, "filters": ["GambesonShort", "GambesonLong", "Caftan", "Pourpoint"]                                                         },
    {"id": 13, "name": "bodyChainmail",      "uiSlot": 11, "filters": ["MailShort", "MailLong"]                                                                                        },
    {"id": 14, "name": "gloves",             "uiSlot": 12, "filters": ["Gloves"]                                                                                                       },
    {"id": 15, "name": "sleeves",            "uiSlot": 13, "filters": ["ArmBrigandine", "ArmPlate"]                                                                                    },
    {"id": 16, "name": "legTrousers",        "uiSlot": 14, "filters": ["HoseJoined", "HoseLoose", "HoseSeparate"]                                                                      },
    {"id": 17, "name": "legTrousersPadded",  "uiSlot": 14, "filters": ["LegsPadded", "LegsChain"]                                                                                      },
    {"id": 18, "name": "legArmor",           "uiSlot": 15, "filters": ["LegsBrigandine", "LegsPlate"]                                                                                  },
    {"id": 19, "name": "boot",               "uiSlot": 16, "filters": ["Boot"]                                                                                                         },
    {"id": 20, "name": "spur",               "uiSlot": 17, "filters": ["Spurs"]                                                                                                        },
    {"id": 21, "name": "pouch",              "uiSlot": 18, "filters": ["Pouch"]                                                                                                        },
    {"id": 22, "name": "horseHead",          "uiSlot": 19, "filters": ["Bridle", "Chanfron"]                                                                                           },
    {"id": 23, "name": "horseTorso",         "uiSlot": 20, "filters": ["Caparison", "Harness"]                                                                                         },
    {"id": 24, "name": "horseSaddle",        "uiSlot": 21, "filters": ["Saddle"]                                                                                                       },
    {"id": 25, "name": "horseShoe",          "uiSlot": 22, "filters": ["HorseShoe"]                                                                                                    },
]

WEAPON_TYPES = [
    {"id": -1, "name": "undefined",       "type": "MeleeWeapon",   "skill": "fencing",         "uiSlot": -1                                                },
    {"id": 0,  "name": "dagger",          "type": "MeleeWeapon",   "skill": "weaponDagger",    "uiSlot": 6                                                 },
    {"id": 1,  "name": "sword",           "type": "MeleeWeapon",   "skill": "weaponSword",     "uiSlot": 23                                                },
    {"id": 2,  "name": "sabre",           "type": "MeleeWeapon",   "skill": "weaponSword",     "uiSlot": 23                                                },
    {"id": 3,  "name": "axe",             "type": "MeleeWeapon",   "skill": "heavyWeapons",    "uiSlot": 23                                                },
    {"id": 4,  "name": "longsword",       "type": "MeleeWeapon",   "skill": "weaponSword",     "uiSlot": 23                                                },
    {"id": 5,  "name": "mace",            "type": "MeleeWeapon",   "skill": "heavyWeapons",    "uiSlot": 23                                                },
    {"id": 6,  "name": "flail",           "type": "MeleeWeapon",   "skill": "weaponLarge",     "uiSlot": 23                                                },
    {"id": 7,  "name": "halberd",         "type": "MeleeWeapon",   "skill": "weaponLarge",     "uiSlot": 23                                                },
    {"id": 8,  "name": "shield",          "type": "MeleeWeapon",   "skill": "weaponShield",    "uiSlot": 25                                                },
    {"id": 9,  "name": "bow",             "type": "MissileWeapon", "skill": "marksmanship",    "uiSlot": 24, "ammo": "arrow"                               },
    {"id": 10, "name": "crossbowLight",   "type": "MissileWeapon", "skill": "marksmanship",    "uiSlot": 24, "ammo": "bolt"                                },
    {"id": 11, "name": "torch",           "type": "MeleeWeapon",   "skill": "weaponDagger",    "uiSlot": -1                                                },
    {"id": 12, "name": "unarmed",         "type": "MeleeWeapon",   "skill": "weaponUnarmed",   "uiSlot": -1                                                },
    {"id": 13, "name": "rifle",           "type": "MissileWeapon", "skill": "marksmanship",    "uiSlot": 24, "ammo": ["ball", "shotgun"]                   },
    {"id": 14, "name": "crossbowMedium",  "type": "MissileWeapon", "skill": "marksmanship",    "uiSlot": 24, "ammo": "bolt"                                },
    {"id": 15, "name": "crossbowHeavy",   "type": "MissileWeapon", "skill": "marksmanship",    "uiSlot": 24, "ammo": "bolt"                                },
    {"id": 16, "name": "huntingSword",    "type": "MeleeWeapon",   "skill": "weaponSword",     "uiSlot": 23                                                },
    {"id": 17, "name": "shieldBroken",    "type": "MeleeWeapon",   "skill": "weaponShield",    "uiSlot": -1                                                },
]

DIE_SIDE_VALUES = [
    {0: "1"},
    {1: "2"},
    {2: "3"},
    {3: "4"},
    {4: "5"},
    {5: "6"},
    {6: "Devil"},
]

DICE_BADGE_TYPES = [
    {"id": -1, "name": "undefined"},
    {"id": 0,  "name": "plumb"},
    {"id": 1,  "name": "silver"},
    {"id": 2,  "name": "gold"}
]
 
DICE_BADGE_SUBTYPES = [
    {"id": 0,  "name": "Headstart"},
    {"id": 1,  "name": "Formations"},
    {"id": 2,  "name": "Null"},
    {"id": 3,  "name": "ExtraValue"},
    {"id": 4,  "name": "Antibust"},
    {"id": 5,  "name": "DoubleTake"},
    {"id": 6,  "name": "Multiplier"},
    {"id": 7,  "name": "ExtraDice"},
    {"id": 8,  "name": "RerollDice"},
    {"id": 9,  "name": "SetDice"},
    {"id": 10, "name": "RerollPips"}
]