# File Structure
## CrabChampions/Saved
### ./CCSM/Saves
folders in here are saves of runs, they are stored as a folder with the save name, and a SaveSlot.sav in the folder
### ./CCSM/backupDataCache.json
stores info about saves and other things, including hashs so it can be checked and updated if needed
info is stored in a format that is easyer than what SavConverter gets







# Data
some game data needs to be set, either in code or in an external file, such as what blessings, challenges and the like exist , descriptions for them, how should they be displayed to the user vs what should be used in code, i'm leaning toward an external data file, make the program more data driven, so the code isn't as cluttered up with data
## static data
### Blessings
### Challenges (island modifiers to make it harder)
### Difficulity mods (to make a run harder)
### Island types 
### island names
### island biomes 

### config data for stuff like colors and other settings

## dynamic data
### Weapon mods
### grenade mods
### perks
### relics
