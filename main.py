import copy
import os
import re
import shutil
import time
import subprocess
import sys
import json
import platform
import curses
import requests
import helper
from os import path
            
screen = helper.makeScreen()
            
# 30 x 120
Version = "1.3.0"

    
LatestVersion = Version
latestReleaseURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest"
try:
    response = requests.get(latestReleaseURL)
    final_url = response.url
    final_url = final_url.removeprefix("https://github.com/O2theC/CrabChampionSaveManager/releases/tag/")
    LatestVersion = final_url
except:
    None
    

mainMenuPrompt = "Current Version : "+str(Version)
mainMenuPrompt += "\nLatest Version : "+str(LatestVersion)
VersionValue = helper.versionToValue(Version)
LatestValue = helper.versionToValue(LatestVersion)

if(LatestValue == -1):
    mainMenuPrompt += "\n\nCould not get latest version"
elif(VersionValue < LatestValue):
    helper.updateScript(is_exe)
    helper.exit_helper(0)
elif(VersionValue > LatestValue):
    mainMenuPrompt += "\n\n***BETA WARNING***"
else:
    mainMenuPrompt += "\n\nYou have the latest version"



            
if(helper.currentDirCheck()):
    try:
        new_dir = os.path.expandvars("%APPDATA%\\..\\Local\\CrabChampions\\Saved")
        os.chdir(new_dir)
    except:
        helper.infoScreen("Could not find save game directory\nYou either don't have Crab Champions installed\n or you have it installed in a different spot than the default\n if it is installed in a different spot than the defualt then put this file in the equivalent of CrabChampions\Saved\nPress any key to continue . . .")
        screen.getch()
        helper.exit_helper(0)




mainMenuPrompt += "\n\nWelcome to Crab Champion Save Manager"
mainMenuPrompt += "\nMade By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager\nWhat do you want to do\n"
while(True):
    options = f"""Edit save game {helper.uesaveCheck()}
    Backup Save
    Update backup
    Restore Save from backup (Warning : Deletes current save)
    Delete backup\nList Backups
    Info/How to use
    Exit"""

    choice = helper.scrollSelectMenu(mainMenuPrompt,options,-1,1)+1
    if(choice == 1):
        helper.editBackup() # turned to curse
    elif(choice == 2):
        helper.backupSave()
    elif(choice == 3):
        helper.updateBackup() # turned to curse
    elif(choice == 4):
        helper.restoreBackup()# turned to curse
    elif(choice == 5):
        helper.deleteBackup() # turned to curse
    elif(choice == 6):
        helper.listBackups()
    elif(choice == 7):
        infolist = """
        ____ ____ ____  __  __ 
        / ___/ ___/ ___||  \/  |
        | |  | |   \___ \| |\/| |
        | |__| |___ ___) | |  | |
        \____\____|____/|_|  |_|
        
        Welcome to CCSM, a script designed to help you manage your save files for Crab Champion.
        Made By O2C
        This program provides the following options:"

        1. Edit Save Game:
           - This option allows you to edit your save game using the uesave tool.
           - This option uses the uesave tool for editing the .sav file, the selection of the backup is done by the script

        2. Backup Save:
           - This option allows you to create a backup of your current save game.
           - When prompted, enter a name for the backup folder.
           - The backup name must be a valid folder name and should not already exist.
           - If a valid backup name is provided, the SaveGames folder will be copied to the backup location.

        3. Update backup:
           - This option allows you to update a backup using your current save game.
           - When prompted, choose a backup to be updated.

        4. Restore Save from Backup:
            - This option allows you to restore a backup of your save game.
            - Select a backup from the available options.
            - The uesave tool will be used to turn both the backup .sav file and the current save's .sav file into json
            - This program then takes in the json and takes the autosave from the backup and copys it over to the current save json
            - The json with the restored save is then saved to a file and the uesave tool turns that back to .sav and the backup copies are made
            - Caution: Restoring a backup will overwrite your current save game, so choose the backup carefully.

        5. Delete Backup:
           - This option allows you to delete a backup of your save game.
           - Select a backup from the available options.
           - The selected backup folder will be permanently deleted.
           - Note: Deleting a backup cannot be undone, so be careful when removing backups.

        6. List Backups:
           - This option displays the available backups of your save game.
           - It shows the names of the backup folders and the total count of backups.

        7. Info/How to use:
           - This option provides a brief description of each functionality and how to use them.
           - It gives an overview of the script's purpose and directs you to the GitHub repository for reporting issues and suggestions.

        8. Exit:
           - This option allows you to exit the program.

        Report issues and suggestions to https://github.com/O2theC/CrabChampionSaveManager
        
        ***CREDITS***
        This script uses uesave-rs, a project made by Trumank. (https://github.com/trumank/uesave-rs)"""

        helper.scrollInfoMenu(helper.infoList,-1)
    elif(choice == 8):
        break
    
helper.exit_helper(0)