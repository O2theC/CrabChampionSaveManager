"""
This script is for extracting and formating unlocked items from a save file, this allows for getting all items in the game (assuming all items are unlocked in the save file)

the json file made should be used when CCSM needs to know what items exist,

"""



from SavConverter import sav_to_json,read_sav,get_object_by_path

import json

def getValue(data, name):
    return get_object_by_path(data, [{"name": name}, "value"])

saveFileName = "./dev/SaveSlot.sav"
exportJsonName = "./dev/KnownItems.json"
knownItems = dict()

saveData = sav_to_json(read_sav(saveFileName))

weaponmodsData = getValue(saveData,"UnlockedWeaponMods")

weaponmods = {}
for mod in weaponmodsData:
    quality = mod[mod.rindex("/", 0, mod.rindex("/")) + 1 : mod.rindex("/")]
    name = mod[mod.rindex("_") + 1 :]
    # weaponmods.append({"Name":name,"Quality":quality})
    weaponmods[name]=quality

knownItems["WeaponMods"] = weaponmods



AbilityModsData = getValue(saveData,"UnlockedAbilityMods")

AbilityMods = {}
for mod in AbilityMods:
    quality = mod[mod.rindex("/", 0, mod.rindex("/")) + 1 : mod.rindex("/")]
    name = mod[mod.rindex("_") + 1 :]
    # weaponmods.append({"Name":name,"Quality":quality})
    AbilityMods[name]=quality

knownItems["AbilityMods"] = AbilityMods



MeleeModsData = getValue(saveData,"UnlockedMeleeMods")

MeleeMods = {}
for mod in MeleeModsData:
    quality = mod[mod.rindex("/", 0, mod.rindex("/")) + 1 : mod.rindex("/")]
    name = mod[mod.rindex("_") + 1 :]
    # weaponmods.append({"Name":name,"Quality":quality})
    MeleeMods[name]=quality

knownItems["MeleeMods"] = MeleeMods



PerksData = getValue(saveData,"UnlockedPerks")

Perks = {}
for mod in PerksData:
    quality = mod[mod.rindex("/", 0, mod.rindex("/")) + 1 : mod.rindex("/")]
    name = mod[mod.rindex("_") + 1 :]
    # weaponmods.append({"Name":name,"Quality":quality})
    Perks[name]=quality

knownItems["Perks"] = Perks



RelicsData = getValue(saveData,"UnlockedRelics")

Relics = {}
for mod in RelicsData:
    quality = mod[mod.rindex("/", 0, mod.rindex("/")) + 1 : mod.rindex("/")]
    name = mod[mod.rindex("_") + 1 :]
    # weaponmods.append({"Name":name,"Quality":quality})
    Relics[name]=quality

knownItems["Relics"] = Relics



print(json.dumps(knownItems,indent=2))

with open(exportJsonName,"w") as f:
    f.write(json.dumps(knownItems,indent=2))