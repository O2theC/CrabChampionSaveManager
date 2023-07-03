import os
import re
import shutil
import time
import subprocess
import sys
import requests
from os import path


def extract_numbers(input_string):
    """Converts the input string to an integer if possible, otherwise returns -1."""
    try:
        return int(input_string)
    except:
        return -1
    
def is_valid_folder_name(folder_name):
    """Checks if the folder name is valid based on certain criteria.
    
    The folder name should not contain any of the characters \\/:*?\"<>|,
    should not end in a period or consist of only spaces and periods,
    and should not be any of the reserved folder names (SaveGames, Logs, Config).
    
    Returns True if the folder name is valid, False otherwise.
    """
    pattern = r'^[^\\/:*?"<>|]+$'
    return bool(re.match(pattern, folder_name)) and not folder_name.strip(" .") == "" and not folder_name == "SaveGames" and not folder_name == "Logs" and not folder_name == "Config"
    
def backupSave():
    """Performs the backup of the save game.
    
    Asks the user for the backup name, validates it, and creates a backup
    by copying the SaveGames folder to the specified backup location.
    If a backup with the same name already exists, prompts for overwrite confirmation.
    """

    current_directory = os.getcwd()
    folders = getBackups()
    confirm = False
    while(not confirm):
        saveName = input("What should the backup be named\nName can not contain any of these characters \\/:*?\"<>|\ncan not end in a period or consist of only spaces and periods\ncan not be any of the games folder (SaveGames , Logs , Config)\nEnter None to not make a backup\n")
        while(not is_valid_folder_name(saveName)):
            print("Invalid Backup name, try again\nName can not contain any of these characters \\/:*?\"<>|\ncan not end in a period or consist of only spaces and periods\ncan not be any of the games folder (SaveGames , Logs , Config)\nEnter None to not make a backup\n")
            saveName = input()
        if(not saveName in folders):
            confirm = True
        else:
            print("There is already a backup by that name. Overwrite? (Y/N)")
            ans = input("")
            if("y" in ans.lower()):
                confirm = True
            else:
                print("Not restoring any backup")
                time.sleep(1)
                return
    if(saveName == "None"):
        print("Not restoring any backup")
        time.sleep(1)
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, saveName)
    try:
        shutil.rmtree(backupName,ignore_errors=True)
        shutil.copytree(saveGame, backupName)
        print("Backup Made - ",saveName)
        time.sleep(1)
    except Exception as error:
        print("Could not make backup. Error below:\n")
        print(error)
        input("Press Enter to continue . . .")
    
def restoreBackup():
    """Restores a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it replaces the current SaveGames folder
    with the contents of the chosen backup.
    """

    current_directory = os.getcwd()
    folders = getBackups()
    print("Choose Backup to restore")
    print("0 - don't restore any backup")
    for i in range(len(folders)):
        print((i+1),"-",folders[i])
    choice = input("")
    choice = extract_numbers(choice)
    while(int(choice)<0 or int(choice)>len(folders)):
        print("\nInvalid choice. Valid choices are")
        print("0 - don't restore any backup")
        for i in range(len(folders)):
            print((i+1),"-",folders[i])
        choice = input("")
    if(extract_numbers(choice) == 0):
        print("Not restoring any backup")
        time.sleep(1)
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    try:
        shutil.rmtree(saveGame,ignore_errors=True)
        shutil.copytree(backupName, saveGame)
        print("Backup Restored - ",folders[extract_numbers(choice)-1])
        time.sleep(1)
    except Exception as error:
        print("Could not restore backup. Error below:\n")
        print(error)
        input("Press Enter to continue . . .")

def editBackup(isExe):

    """Edits a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it opens the SaveSlot.sav file for editing
    using the uesave tool. Two backup copies (SaveSlotBackupA.sav and SaveSlotBackupB.sav)
    are created before editing.
    """

    current_directory = os.getcwd()
    folders = getBackups()
    print("Choose Backup to edit")
    print("0 - don't edit any backup")
    print("1 - edit current save")
    for i in range(len(folders)):
        print((i+2),"-",folders[i])
    choice = input("")
    choice = extract_numbers(choice)
    while(int(choice)<0 or int(choice)>(len(folders)+1)):
        print("\nInvalid choice. Valid choices are")
        print("0 - don't edit any backup")
        print("1 - edit current save")
        for i in range(len(folders)):
            print((i+2),"-",folders[i])
        choice = input("")
    if(extract_numbers(choice) == 0):
        print("Not editing any backup")
        time.sleep(1)
        return
    saveFile = ""
    if(extract_numbers(choice) == 1):
        saveFile = os.path.join(current_directory,"SaveGames")
    else:
        saveFile = os.path.join(current_directory,str(folders[extract_numbers(choice)-2]))
    saveFile = os.path.join(saveFile,"SaveSlot.sav")
    saveBackA = saveFile.replace("SaveSlot.sav","SaveSlotBackupA.sav")
    saveBackB = saveFile.replace("SaveSlot.sav","SaveSlotBackupB.sav")
    sf = saveFile
    saveFile = "\""+saveFile+"\""
    if(isExe):
        file = __file__
        bundle_dir = path.abspath(path.dirname(file)) 
        path_to_dat = path.join(bundle_dir, 'uesave.exe')
        subprocess.run(str(path_to_dat)+" edit "+str(saveFile))
    else:
        #%APPDATA%/../../.cargo/bin
        uesaveExe = os.path.expandvars("%APPDATA%/../../.cargo/bin")
        
        if(os.path.exists(os.path.join(uesaveExe,"uesave.exe"))):
            uesaveExe = os.path.join(uesaveExe,"uesave.exe")
        elif(os.path.exists("uesave.exe")):
            uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
        else:
            print("no copy of uesave.exe could be found")
            print("either place your copy of it in the same place as this script/exe")
            perm = input("or allow for it to be downloaded(Y - allow download/N - don't allow download)\n")
            if("y" in perm.lower()):
                downURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/uesave.exe"
                response = requests.get(downURL)
                with open(__file__[:__file__.rindex("\\")+1]+"uesave.exe", 'wb') as file:
                    file.write(response.content)
                uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
            else:
                print("no permission given to download uesave, no uesave found\nreturning to main menu")
                input("Press Enter to continue . . .")
                return
        subprocess.run(str(uesaveExe)+" edit "+str(saveFile))

    try:
        os.remove(saveBackA)
        os.remove(saveBackB)
    except:
        None
    shutil.copy(sf, saveBackA)
    shutil.copy(sf, saveBackB)
    
def deleteBackup():
    """Deletes a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it permanently deletes the corresponding backup folder.
    """
    
    current_directory = os.getcwd()
    folders = getBackups()
    print("Choose Backup to delete")
    print("0 - don't delete any backup")
    for i in range(len(folders)):
        print((i+1),"-",folders[i])
    choice = input("")
    choice = extract_numbers(choice)
    while(int(choice)<0 or int(choice)>len(folders)):
        print("\nInvalid choice. Valid choices are")
        print("0 - don't delete any backup")
        for i in range(len(folders)):
            print((i+1),"-",folders[i])
        choice = input("")
    if(extract_numbers(choice) == 0):
        print("Not deleting any backup")
        time.sleep(1)
        return
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    try:
        shutil.rmtree(backupName)
        print("Deleted Backup - ",folders[extract_numbers(choice)-1])
        time.sleep(1)
    except Exception as error:
        print("Could not delete backup. Error below:\n")
        print(error)
        input("Press Enter to continue . . .")

def listBackups():
    """Lists all the available backups of the save game.
    
    Retrieves the list of backup folders and displays them to the user.
    """
    
    current_directory = os.getcwd()
    items = os.listdir(current_directory)
    folders = getBackups()
    print("Current Backups:")
    for i in folders:
        print(i)
    print(len(folders),"Backups stored")
    input("Press Enter to continue . . .")

def getBackups():
    """Retrieves the list of backup folders.
    
    Searches the current directory for backup folders and returns a list of their names.
    """
    
    current_directory = os.getcwd()
    items = os.listdir(current_directory)
    try:
        items.remove("SaveGames")
        items.remove("Config")
        items.remove("Logs")
    except:
        None
    folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]
    folders = [item for item in items if os.path.isfile(os.path.join(os.path.join(current_directory, item),"SaveSlot.sav"))]
    return folders

def currentDirCheck():
    """Checks if the required folders are present in the current directory.
    
    Checks if the folders SaveGames, Logs, and Config exist in the current directory.
    Returns True if any of the folders is missing, indicating a directory check failure.
    Returns False if all the required folders are present.
    """
    
    folder_names = ["SaveGames", "Logs", "Config"]
    for folder_name in folder_names:
        folder_path = os.path.join(os.getcwd(), folder_name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            None
        else:
            return True
    return False              

def updateBackup():
    current_directory = os.getcwd()
    folders = getBackups()
    print("Choose Backup to update")
    print("0 - don't update any backup")
    for i in range(len(folders)):
        print((i+1),"-",folders[i])
    choice = input("")
    choice = extract_numbers(choice)
    while(int(choice)<0 or int(choice)>len(folders)):
        print("\nInvalid choice. Valid choices are")
        print("0 - don't update any backup")
        for i in range(len(folders)):
            print((i+1),"-",folders[i])
        choice = input("")
    if(extract_numbers(choice) == 0):
        print("Not updating any backup")
        time.sleep(1)
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    try:
        shutil.rmtree(backupName,ignore_errors=True)
        shutil.copytree(saveGame, backupName)
        print("Backup Updated - ",folders[extract_numbers(choice)-1])
        time.sleep(1)
    except Exception as error:
        print("Could not update backup. Error below:\n")
        print(error)
        input("Press Enter to continue . . .")

def versionToValue(version):
    try:
        value = 0
        points = version.split(".")
        value = int(points[0])*1000000
        value += int(points[1])*1000
        value += int(points[2])
        return int(value)
    except:
        return -1

def updateScript(isExe):
    print("There is a newer version available")
    perm = input("would you like to update to the latest version?(Y/N)\n")
    if("y" in perm.lower()):
        if(isExe):
            downloadLatestURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.exe"
        else:
            downloadLatestURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.py"
        try:
            updaterURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManagerUpdater.exe"
            
            response = requests.get(downloadLatestURL)
            path = os.path.join(os.getcwd(),downloadLatestURL[downloadLatestURL.rindex("/")+1:])
            path = path.replace("CrabChampionSaveManager.exe","CrabChampionSaveManagerUpdated.exe")
            with open(path, 'wb') as file:
                file.write(response.content)
            if(isExe):
                response = requests.get(updaterURL)
                path = os.path.join(os.getcwd(),updaterURL[updaterURL.rindex("/")+1:])
                with open(path, 'wb') as file:
                    file.write(response.content)
                print("due to this being a exe , a seperate program will update this")
                print("when ready press enter")
                input("Press Enter to continue . . .")
                subprocess.Popen(["CrabChampionSaveManagerUpdater.exe"], shell=True)
                return
        except:
            print("Could not download latest version, exiting script")
            input("Press Enter to continue . . .")
            exit(1)
        print("Latest Version succesfully downloaded")
        print("Please restart script for changes to show")
        input("Press Enter to continue . . .")
        exit(0)
    else:
        print("no permission given")
        input("Press Enter to continue . . .")
        return
 
def uesaveCheck(isEXE):
    if(isExe):
        return ""
    else:
        return "(requires uesave.exe)"


            

Version = "1.2.3"
isExe = False

if (getattr(sys, 'frozen', False)):
    isExe = True
    
LatestVersion = Version
latestReleaseURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest"
try:
    response = requests.get(latestReleaseURL)
    final_url = response.url
    final_url = final_url.removeprefix("https://github.com/O2theC/CrabChampionSaveManager/releases/tag/")
    LatestVersion = final_url
except:
    None
    
    
print("Current Version : ",Version)
print("Latest Version : ",LatestVersion)
VersionValue = versionToValue(Version)
LatestValue = versionToValue(LatestVersion)

print()
if(LatestValue == -1):
    print("Could not get latest version")
elif(VersionValue < LatestValue):
    updateScript(isExe)
    exit(0)
elif(VersionValue > LatestValue):
    print("ooohh , you have a version that isn't released yet, nice")
else:
    print("You have the latest version")




            
if(currentDirCheck()):
    try:
        new_dir = os.path.expandvars("%APPDATA%\\..\\Local\\CrabChampions\\Saved")
        os.chdir(new_dir)
    except:
        print("Could not find save game directory")
        print("You either don't have Crab Champions installed\n or you have it installed in a different spot than the default\n if it is installed in a different spot than the defualt then put this file in the equivalent of CrabChampions\Saved")






print("Welcome to Crab Champion Save Manager")
print("Made By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager")
while(True):
    choice = input("What do you want to do\n1 - Edit save game "+uesaveCheck(isExe)+"\n2 - Backup Save\n3 - Update backup\n4 - Restore Save from backup (Warning : Deletes current save)\n5 - Delete backup\n6 - List Backups\n7 - Info/How to use\n8 - Exit\n")
    choice = extract_numbers(choice)
    while(extract_numbers(choice)<1 or extract_numbers(choice)>8):
        choice = input("Invalid choice. Valid choices are\n1 - Edit save game "+uesaveCheck(isExe)+"\n2 - Backup Save\n3 - Update backup\n4 - Restore Save from backup (Warning : Deletes current save)\n5 - Delete backup\n6 - List Backups\n7 - Info/How to use\n8 - Exit\n")
    choice = extract_numbers(choice)
    if(choice == 1):
        editBackup(isExe)
        print("\n")
    elif(choice == 2):
        backupSave()
        print("\n")
    elif(choice == 3):
        updateBackup()
        print("\n")
    elif(choice == 4):
        restoreBackup()
        print("\n")
    elif(choice == 5):
        deleteBackup()
        print("\n")
    elif(choice == 6):
        listBackups()
        print("\n")
    elif(choice == 7):
        print("Crab Champion Save Manager\n")
        print("Welcome to Crab Champion Save Manager, a script designed to help you manage your save files for the game Crab Champion.")
        print("Made By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager")
        print("This program provides the following options:\n")
        
        print("1. Edit Save Game:")
        print("   - This option allows you to edit your save game using the uesave tool.")
        print("   - Before choosing this option, make sure you have the uesave tool (https://github.com/trumank/uesave-rs)")
        print("   - Select a backup to edit, and the tool will open the SaveSlot.sav file for editing.")
        print("   - Two backup copies (SaveSlotBackupA.sav and SaveSlotBackupB.sav) will be created before editing.")
        print("   - Note: Editing the save game can lead to unexpected behavior or corrupt saves, so proceed with caution.")

        print("\n2. Backup Save:")
        print("   - This option allows you to create a backup of your current save game.")
        print("   - When prompted, enter a name for the backup folder.")
        print("   - The backup name must be a valid folder name and should not already exist.")
        print("   - If a valid backup name is provided, the SaveGames folder will be copied to the backup location.")

        print("\n3. Update backup:")
        print("   - This option allows you to update a backup using your current save game.")
        print("   - When prompted, choose a backup to be updated.")

        print("\n4. Restore Save from Backup:")
        print("   - This option allows you to restore a backup of your save game.")
        print("   - Select a backup from the available options.")
        print("   - The current SaveGames folder will be deleted, and the selected backup will be copied to the SaveGames location.")
        print("   - Caution: Restoring a backup will overwrite your current save game, so choose the backup carefully.")

        print("\n5. Delete Backup:")
        print("   - This option allows you to delete a backup of your save game.")
        print("   - Select a backup from the available options.")
        print("   - The selected backup folder will be permanently deleted.")
        print("   - Note: Deleting a backup cannot be undone, so be careful when removing backups.")

        print("\n6. List Backups:")
        print("   - This option displays the available backups of your save game.")
        print("   - It shows the names of the backup folders and the total count of backups.")

        print("\n7. Info/How to use:")
        print("   - This option provides a brief description of each functionality and how to use them.")
        print("   - It gives an overview of the script's purpose and directs you to the GitHub repository for reporting issues and suggestions.")

        print("\n8. Exit:")
        print("   - This option allows you to exit the program.")
        
        print("Note that for this script to edit save files it need uesave from https://github.com/trumank/uesave-rs\n it is written in rust so you will need to get that")
        print("Report issues and suggestions to https://github.com/O2theC/CrabChampionSaveManager")
        print("Note that this info section and most of the code comments were made by chatgpt , if it did something wrong, make an issue at https://github.com/O2theC/CrabChampionSaveManager")
        print("\nthis script does have a version checker and auto updater that requires internet to work, the rest of the script will still work without internet")
        input("\nPress Enter to continue . . .")
    elif(choice == 8):
        print("Exiting...")
        break
