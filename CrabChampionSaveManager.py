import os
import re
import shutil
import time

def extract_numbers(input_string):
    try:
        return int(input_string)
    except:
        return -1
    
def is_valid_folder_name(folder_name):
    """
    Checks if a folder name is valid.

    A valid folder name must satisfy the following conditions:
    1. Does not contain any of the characters \\/:*?\"<>|
    2. Does not end in a period or consist of only spaces and periods
    3. Is not one of the reserved folder names (SaveGames, Logs, Config)

    Args:
    - folder_name (str): The name of the folder

    Returns:
    - bool: True if the folder name is valid, False otherwise
    """
    # Define the regular expression pattern for a valid folder name
    pattern = r'^[^\\/:*?"<>|]+$'

    # Check if the folder name matches the pattern and is not empty or made of only spaces/periods
    return bool(re.match(pattern, folder_name)) and not folder_name.strip(" .") == "" and not folder_name == "SaveGames" and not folder_name == "Logs" and not folder_name == "Config"

def copy_folder(original_folder_path, new_folder_name):
    """
    Copies a folder to a new location.

    Args:
    - original_folder_path (str): The path of the original folder
    - new_folder_name (str): The name of the new folder

    Returns:
    - None
    """
    # Get the current directory
    current_directory = os.getcwd()

    # Create the full path for the original folder
    original_folder_full_path = os.path.join(current_directory, original_folder_path)

    # Create the full path for the new folder
    new_folder_full_path = os.path.join(current_directory, new_folder_name)

    # Copy the original folder to the new folder
    shutil.copytree(original_folder_full_path, new_folder_full_path)
    
def backupSave():
    """
    Creates a backup of the SaveGames folder.

    The function prompts the user to enter a name for the backup.
    The backup name must be a valid folder name and should not already exist.
    If a valid backup name is provided, the SaveGames folder is copied to the backup location.

    Returns:
    - None
    """
    current_directory = os.getcwd()
    # List all the items in the current directory
    items = os.listdir(current_directory)

    # Filter out only the folders 
    folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]
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
                time.sleep(2)
                return
    if(saveName == "None"):
        print("Not restoring any backup")
        time.sleep(2)
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, saveName)
    try:
        shutil.copytree(saveGame, backupName)
        print("Backup Made - ",saveName)
        time.sleep(2)
    except Exception as error:
        print("Could not make backup. Error below:\n")
        print(error)
        input("Press Enter to continue . . .")
    

def restoreBackup():
    """
    Restores a backup of the SaveGames folder.

    The function prompts the user to choose a backup to restore.
    If a valid backup is selected, the current SaveGames folder is deleted
    and the selected backup is copied to the SaveGames location.

    Returns:
    - None
    """
    current_directory = os.getcwd()
    # List all the items in the current directory
    items = os.listdir(current_directory)

    # Filter out only the folders
    folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]
    folders.remove("SaveGames")
    folders.remove("Config")
    folders.remove("Logs")
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
        time.sleep(2)
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    try:
        shutil.rmtree(saveGame)
        shutil.copytree(backupName, saveGame)
        print("Backup Restored - ",folders[extract_numbers(choice)-1])
        time.sleep(2)
    except Exception as error:
        print("Could not restore backup. Error below:\n")
        print(error)
        input("Press Enter to continue . . .")

def editBackup():
    """
    Edits a backup of the SaveGames folder.

    The function prompts the user to choose a backup to edit.
    If a valid backup is selected, the SaveSlot.sav file within the backup is edited using a third-party tool.
    Two backup copies (SaveSlotBackupA.sav and SaveSlotBackupB.sav) are created before editing.

    Returns:
    - None
    """
    current_directory = os.getcwd()
    # List all the items in the current directory
    items = os.listdir(current_directory)

    # Filter out only the folders
    folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]
    folders.remove("SaveGames")
    folders.remove("Config")
    folders.remove("Logs")
    print("Choose Backup to edit")
    print("0 - don't edit any backup")
    for i in range(len(folders)):
        print((i+1),"-",folders[i])
    choice = input("")
    choice = extract_numbers(choice)
    while(int(choice)<0 or int(choice)>len(folders)):
        print("\nInvalid choice. Valid choices are")
        print("0 - don't edit any backup")
        for i in range(len(folders)):
            print((i+1),"-",folders[i])
        choice = input("")
    if(extract_numbers(choice) == 0):
        print("Not editing any backup")
        time.sleep(2)
        return
    saveFile = os.path.join(current_directory,str(folders[extract_numbers(choice)-1]))
    saveFile = os.path.join(saveFile,"SaveSlot.sav")
    saveBackA = saveFile.replace("SaveSlot.sav","SaveSlotBackupA.sav")
    saveBackB = saveFile.replace("SaveSlot.sav","SaveSlotBackupB.sav")
    sf = saveFile
    saveFile = "\""+saveFile+"\""
    os.system("uesave edit "+saveFile)
    try:
        os.remove(saveBackA)
        os.remove(saveBackB)
    except:
        None
    shutil.copy(sf, saveBackA)
    shutil.copy(sf, saveBackB)
    
def deleteBackup():
    """
    Deletes a backup of the SaveGames folder.

    The function prompts the user to choose a backup to delete.
    If a valid backup is selected, the backup folder is deleted.

    Returns:
    - None
    """
    current_directory = os.getcwd()
    # List all the items in the current directory
    items = os.listdir(current_directory)

    # Filter out only the folders
    folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]
    folders.remove("SaveGames")
    folders.remove("Config")
    folders.remove("Logs")
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
        time.sleep(2)
        return
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    try:
        shutil.rmtree(backupName)
        print("Deleted Backup - ",folders[extract_numbers(choice)-1])
        time.sleep(2)
    except Exception as error:
        print("Could not delete backup. Error below:\n")
        print(error)
        input("Press Enter to continue . . .")

print("Welcome to Crab Champion Save Manager")
print("Made By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager")
while(True):
    choice = input("What do you want to do\n1 - Edit save game (requires https://github.com/trumank/uesave-rs with Rust installed)\n2 - Backup save\n3 - Restore save from backup (Warning : Deletes current save)\n4 - Delete backup\n5 - Info/How to use\n6 - Exit\n")
    choice = extract_numbers(choice)
    while(extract_numbers(choice)<1 or extract_numbers(choice)>6):
        choice = input("Invalid choice. Valid choices are\n1 - Edit save game (requires https://github.com/trumank/uesave-rs with Rust installed\n2 - Backup Save\n3 - Restore Save from backup (Warning : Deletes current save)\n4 - Delete backup\n5 - Info/How to use\n6 - Exit\n")
    choice = extract_numbers(choice)
    if(choice == 1):
        editBackup()
        print("\n")
    elif(choice == 2):
        backupSave()
        print("\n")
    elif(choice == 3):
        restoreBackup()
        print("\n")
    elif(choice == 4):
        deleteBackup()
        print("\n")
    elif(choice == 5):
        print("Crab Champion Save Manager\n")
        print("Made By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager")
        print("This program helps you manage your save files for the game Crab Champion.\n")
        print("1. Edit Save Game:")
        print("   - This option allows you to edit your save game using the uesave tool.")
        print("   - You will need to have the uesave tool (https://github.com/trumank/uesave-rs) and Rust installed.")
        print("   - Select a backup to edit, and the tool will open the SaveSlot.sav file for editing.")
        print("   - Two backup copies (SaveSlotBackupA.sav and SaveSlotBackupB.sav) will be created before editing.")
        print("   - Make sure to follow the uesave documentation for editing the save file.")
        print("   - Please note that editing the save game can lead to unexpected behavior or corrupt saves, so proceed with caution.")
        print("\n2. Backup Save:")
        print("   - This option allows you to create a backup of your current save game.")
        print("   - Enter a name for the backup folder when prompted.")
        print("   - The backup name must be a valid folder name and should not already exist.")
        print("   - If a valid backup name is provided, the SaveGames folder will be copied to the backup location.")
        print("\n3. Restore Save from Backup:")
        print("   - This option allows you to restore a backup of your save game.")
        print("   - Select a backup from the available options.")
        print("   - The current SaveGames folder will be deleted, and the selected backup will be copied to the SaveGames location.")
        print("   - Please note that this action will overwrite your current save game, so make sure to choose the correct backup.")
        print("\n4. Delete Backup:")
        print("   - This option allows you to delete a backup of your save game.")
        print("   - Select a backup from the available options.")
        print("   - The selected backup folder will be permanently deleted.")
        print("   - Please note that this action cannot be undone, so be careful when deleting backups.")
        print("\n5. Info/How to use:")
        print("   - This option provides a brief description of each functionality and how to use them.")
        print("\n6. Exit:")
        print("   - This option allows you to exit the program.")
        print("\n")
    elif(choice == 6):
        print("Exiting...")
        break
