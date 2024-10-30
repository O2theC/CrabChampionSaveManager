import json
import pathlib, SavConverter
from textwrap import indent
from SavConverter import get_object_by_path
from SavConverter.SavReader import SavReader


""" 
read file
use sav converter to get json
parse json to format to CCSM memory




there is
Weapons
Abilities
Melee Weapons

Weapon Mods
Ability Mods
Melee Mods
Perks
Relics
"""
Biomes = ["Tropical", "Arctic", "Desert", "Volcanic"]
Islands = dict()

Islands["Tropical"] = [f"Tropical_Arena_{i:02}" for i in range(1, 12)]
Islands["Tropical"].extend(["Tropical_Arena_TEST02", "Tropical_Arena_TEST04"])
Islands["Tropical"].extend([f"Tropical_Boss_{i:02}" for i in range(1, 3)])
Islands["Tropical"].extend([f"Tropical_Horde_{i:02}" for i in range(1, 9)])
Islands["Tropical"].extend([f"Tropical_Parkour_{i:02}" for i in range(1, 2)])
Islands["Tropical"].append("Tropical_Shop_01")

Islands["Arctic"] = [f"Arctic_Arena_{i:02}" for i in range(1, 8)]
Islands["Arctic"].extend([f"Arctic_Boss_{i:02}" for i in range(1, 4)])
Islands["Arctic"].extend([f"Arctic_Horde_{i:02}" for i in range(1, 9)])
Islands["Arctic"].extend([f"Arctic_Parkour_{i:02}" for i in range(1, 2)])
Islands["Arctic"].append("Arctic_Shop_01")

Islands["Desert"] = [f"Desert_Arena_{i:02}" for i in range(1, 13)]
# Islands["Desert"].extend([f"Desert_Boss_{i:02}" for i in range(1,3)])
# Islands["Desert"].extend([f"Desert_Horde_{i:02}" for i in range(1,9)])
# Islands["Desert"].extend([f"Desert_Parkour_{i:02}" for i in range(1,2)])
Islands["Desert"].append("Desert_Shop_01")

Islands["Volcanic"] = [f"Volcanic_Arena_{i:02}" for i in range(1, 8)]
# Islands["Volcanic"].extend(["Volcanic_Arena_TEST02","Volcanic_Arena_TEST04"])
Islands["Volcanic"].extend([f"Volcanic_Boss_{i:02}" for i in range(1, 2)])
Islands["Volcanic"].extend([f"Volcanic_Horde_{i:02}" for i in range(1, 6)])
# Islands["Volcanic"].extend([f"Volcanic_Parkour_{i:02}" for i in range(1,2)])
Islands["Volcanic"].append("Volcanic_Shop_01")

Islands["Minigame"] = ["Arcade", "Duel", "Holdout"]

Islands["Other"] = [
    "Animation",
    "DebugPersistent",
    "IconLightroom",
    "IconLightroom_Neutral",
    "IconLightroomEpicTest",
    "IconLightroomLegendaryTest",
    "IconLightroomRedTest",
]

IslandTypes = [
    "Boss",
    "Challenge",
    "Defense",
    "Elite",
    "CrabIsland",
    "Arena",
    "Rush",
    "Horde",
    "Shop",
    "Treasure",
    "Parkour",
    "Waves",
    "Arcade",
    "Demolition",
    "Duel",
    "Harvest",
    "Holdout",
]

Blessings = ["Flawless", "Rush"]

LootPool = [
    "Economy",
    "Elemental",
    "Skill",
    "Health",
    "Random",
    "Upgrade",
    "Critical",
    "Greed",
    "Speed",
    "Damage",
    "Luck",
    "Relic",
]


def getValue(data, name):
    return get_object_by_path(data, [{"name": name}, "value"])


def removePrefix(string):
    return string[string.rindex(":") + 1 :]


def parsePath(path):
    return path[path.rindex("_") + 1 :]


def parseItem(itemObject, itemNameSpace):
    # print(itemObject)
    name: str = getValue(itemObject, itemNameSpace)
    quality = name[name.rindex("/", 0, name.rindex("/")) + 1 : name.rindex("/")]
    name = name[name.rindex("_") + 1 :]
    level = getValue(getValue(itemObject, "InventoryInfo"), "Level")
    enhancements = getValue(getValue(itemObject, "InventoryInfo"), "Enhancements")
    enhancements = [removePrefix(enhance) for enhance in enhancements]
    accumulatedBuff = getValue(getValue(itemObject, "InventoryInfo"), "AccumulatedBuff")
    return {
        "Name": name,
        "Quality": quality,
        "Enhancements": enhancements,
        "AccumulatedBuff": accumulatedBuff,
    }


def readRun(path: pathlib.Path):
    runRawJson: dict = SavConverter.sav_to_json(
        SavReader(path.read_bytes()).read_whole_buffer()
    )
    runRawJson: dict = getValue(runRawJson, "AutoSave")
    runJson = dict()

    currentIsland = dict()

    currentIsland["Biome"] = removePrefix(
        getValue(getValue(runRawJson, "NextIslandInfo"), "Biome")
    )
    currentIsland["Number"] = getValue(
        getValue(runRawJson, "NextIslandInfo"), "CurrentIsland"
    )
    currentIsland["Name"] = getValue(
        getValue(runRawJson, "NextIslandInfo"), "IslandName"
    )
    currentIsland["Type"] = removePrefix(
        getValue(getValue(runRawJson, "NextIslandInfo"), "IslandType")
    )

    stats = dict()
    stats["RunLength"] = getValue(runRawJson, "CurrentTime")
    stats["Points"] = getValue(runRawJson, "Points")
    stats["ComboCounter"] = getValue(runRawJson, "ComboCounter")
    stats["Combo"] = getValue(runRawJson, "Combo")
    stats["Eliminations"] = getValue(runRawJson, "Eliminations")
    stats["ShotsFired"] = getValue(runRawJson, "ShotsFired")
    stats["DamageDealt"] = getValue(runRawJson, "DamageDealt")
    stats["HighestDamageDealt"] = getValue(runRawJson, "HighestDamageDealt")
    stats["DamageTaken"] = getValue(runRawJson, "DamageTaken")
    stats["FlawlessIslandsCount"] = getValue(runRawJson, "NumFlawlessIslands")

    runJson["Stats"] = stats

    runJson["CurrentIsland"] = currentIsland

    runJson["Health"] = getValue(getValue(runRawJson, "HealthInfo"), "CurrentHealth")
    runJson["MaxHealth"] = getValue(
        getValue(runRawJson, "HealthInfo"), "CurrentMaxHealth"
    )
    runJson["ArmorPlates"] = getValue(
        getValue(runRawJson, "HealthInfo"), "CurrentArmorPlates"
    )
    runJson["ArmorPlateHealth"] = getValue(
        getValue(runRawJson, "HealthInfo"), "CurrentArmorPlateHealth"
    )
    runJson["OldHealth"] = getValue(
        getValue(runRawJson, "HealthInfo"), "PreviousHealth"
    )
    runJson["OldMaxHealth"] = getValue(
        getValue(runRawJson, "HealthInfo"), "PreviousMaxHealth"
    )
    runJson["MaxHealthMultiplier"] = getValue(runRawJson, "MaxHealthMultiplier")
    runJson["DamageMultiplier"] = getValue(runRawJson, "DamageMultiplier")
    runJson["EquipedWeapon"] = parsePath(getValue(runRawJson, "WeaponDA"))
    runJson["EquipedAbility"] = parsePath(getValue(runRawJson, "AbilityDA"))
    runJson["EquipedMelee"] = parsePath(getValue(runRawJson, "MeleeDA"))
    runJson["WeaponModSlotCount"] = getValue(runRawJson, "NumWeaponModSlots")
    runJson["AbilityModSlotCount"] = getValue(runRawJson, "NumAbilityModSlots")
    runJson["MeleeModSlotCount"] = getValue(runRawJson, "NumMeleeModSlots")
    runJson["PerkSlotCount"] = getValue(runRawJson, "NumPerkSlots")
    # runJson["RelicSlotCount"] = getValue(runRawJson, "NumFlawlessIslands")

    items = []
    for item in getValue(runRawJson, "WeaponMods"):
        items.append(parseItem(item, "WeaponModDA"))
    runJson["WeaponMods"] = items

    items = []
    for item in getValue(runRawJson, "AbilityMods"):
        items.append(parseItem(item, "AbilityModDA"))
    runJson["AbilityMods"] = items

    items = []
    for item in getValue(runRawJson, "MeleeMods"):
        items.append(parseItem(item, "MeleeModDA"))
    runJson["MeleeMods"] = items

    items = []
    for item in getValue(runRawJson, "Perks"):
        items.append(parseItem(item, "PerkDA"))
    runJson["Perks"] = items

    items = []
    for item in getValue(runRawJson, "Relics"):
        items.append(parseItem(item, "RelicDA"))
    runJson["Relics"] = items

    """ Key/Legend


    
    RunLength - int - 
    CurrentIsland - dict
    - Biome - Enum
    - Number - int
    - Name - Enum
    - Type - Enum
    Stats - dict
    - Points - int
    - ComboCounter - int
    - Combo - float
    - Eliminations - int
    - ShotsFired - int
    - DamageDealt - int
    - HighestDamageDealt - int
    - DamageTaken - int
    - FlawlessIslandsCount - int

    Health - float
    MaxHealth - float
    ArmorPlates - int
    ArmorPlateHealth - float
    OldHealth - float
    OldMaxHealth - float
    MaxHealthMultiplier - float
    DamageMultiplier - float
    EquipedWeapon - Enum
    EquipedAbility - Enum
    EquipedMelee - Enum

    WeaponModSlotCount - int
    WeaponMods - array
    WeaponModsItem
    - Name - Enum
    - Level - int
    - Enchancements - array
    - AccumlatedBuff - float

    AbilityModSlotCount - int
    AbilityMods - array
    AbilityModsItem
    - Name - Enum
    - Level - int
    - Enchancements - array
    - AccumlatedBuff - float

    MeleeModSlotCount - int
    MeleeMods - array
    MeleeModsItem
    - Name - Enum
    - Level - int
    - Enchancements - array
    - AccumlatedBuff - float

    PerkSlotCount - int
    Perks - array
    PerksItem
    - Name - Enum
    - Level - int
    - Enchancements - array
    - AccumlatedBuff - float


    Relics - array
    RelicsItem
    - Name - Enum
    - Level - int
    - Enchancements - array
    - AccumlatedBuff - float


    
    
    
    """
    return runJson


if __name__ == "__main__":
    print(json.dumps(readRun(pathlib.Path("./testing/SaveSlot.sav")), indent=2))
    # print(parseItem([{
    #           "type": "ObjectProperty",
    #           "name": "WeaponModDA",
    #           "value": "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_MoneyShot.DA_WeaponMod_MoneyShot"
    #         },]))
    # print(json.dumps(Islands, indent=2))
