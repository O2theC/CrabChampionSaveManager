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
    # Define the regular expression pattern for a valid folder name
    pattern = r'^[^\\/:*?"<>|]+$'

    # Check if the folder name matches the pattern and is not empty or made of only spaces/periods
    return bool(re.match(pattern, folder_name)) and not folder_name.strip(" .") == "" and not folder_name == "SaveGames" and not folder_name == "Logs" and not folder_name == "Config"

def copy_folder(original_folder_path, new_folder_name):
    # Get the current directory
    current_directory = os.getcwd()

    # Create the full path for the original folder
    original_folder_full_path = os.path.join(current_directory, original_folder_path)

    # Create the full path for the new folder
    new_folder_full_path = os.path.join(current_directory, new_folder_name)

    # Copy the original folder to the new folder
    shutil.copytree(original_folder_full_path, new_folder_full_path)
    
def backupSave():
    current_directory = os.getcwd()
    # List all the items in the current directory
    items = os.listdir(current_directory)

    # Filter out only the folders 
    folders = [item for item in items if os.path.isdir(os.path.join(current_directory, item))]
    confirm = False
    while(not confirm):
        saveName = input("What should the backup be named\nName can not contain any of these characters \\/:*?\"<>|\ncan not end in a period or consist of only spaces and periods\ncan not be any of the games folder (SaveGames , Logs , Config)\nEnter None to not make a backup\n")
        while(not is_valid_folder_name(saveName)):
            print("Invaild Backup name, try again\nName can not contain any of these characters \\/:*?\"<>|\ncan not end in a period or consist of only spaces and periods\ncan not be any of the games folder (SaveGames , Logs , Config)\nEnter None to not make a backup\n")
            saveName = input()
        if(not saveName in folders):
            confirm = True
        else:
            print("There is already a backup by that name, Overwrite?(Y/N)")
            ans = input("")
            if("y" in ans.lower()):
                confirm = True
            else:
                print("Not restoring any backup")
                time.sleep(2)
                return
    if(saveName == "None"):
        print("Not restoreing any backup")
        time.sleep(2)
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, saveName)
    try:
        shutil.copytree(saveGame, backupName)
        print("Backup Made - ",saveName)
        time.sleep(2)
    except Exception as error:
        print("Could not make backup, Error below\n")
        print(error)
        input("Press Enter to continue . . .")
    

def restoreBackup():
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
        print("\nInvaild choice, valid choices are")
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
        print("Could not restore backup, Error below\n")
        print(error)
        input("Press Enter to continue . . .")

def editBackup():
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
        print("\nInvaild choice, valid choices are")
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
        print("\nInvaild choice, valid choices are")
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
        print("Could not delete backup, Error below\n")
        print(error)
        input("Press Enter to continue . . .")

print("Welcome to Crab Champion Save Manager")
while(True):
    choice = input("What do you want to do\n1 - Edit save game (requires https://github.com/trumank/uesave-rs with Rust installed)\n2 - Backup save\n3 - Restore save from backup (Warning : Deletes current save)\n4 - Delete backup\n5 - Info/How to use\n6 - Exit\n")
    choice = extract_numbers(choice)
    while(extract_numbers(choice)<1 or extract_numbers(choice)>6):
        choice = input("Invalid choice, valid choices are\n1 - Edit save game (requires https://github.com/trumank/uesave-rs with Rust installed\n2 - Backup Save\n3 - Restore Save from backup (Warning : Deletes current save)\n4 - Delete backup\n5 - Info/How to use\n6 - Exit\n")
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
    elif(choice == 5):
        print("\nInfo:\nSteam Cloud might break this when changing active saves\nif it causing problems, try turning it off and then starting the game\nthen shut game off and turn it back on\n\nthis just looks for folders other than the ones used by the game and treats them like save games,\nif you tell it to it will \"restore\" a backup that is not a backup, wiping the current save and not replacing it with anything\nWarning - this script deletes the current same game when restoring from a backup\nMade by O2C\n Github repo at ")
        input("Press Enter to continue . . .")
        print("\n")
    elif(choice == 6):
        exit(0)