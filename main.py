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
from os import path
            
def isLinux():
    if platform.system == "Linux":
        return True
    else:
        return False

def isExe():
    is_exe = False
    if (getattr(sys, 'frozen', False)):
        is_exe = True
    return is_exe

def closeScreen():
    global screen
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


def exit_helper(status):
    try:
        closeScreen()
    except:
        None
    exit(status)

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
    Additionally, it should not be any of the system-reserved names.
    
    Returns True if the folder name is valid, False otherwise.
    """
    invalid_characters = r'\\/:*?"<>|'
    reserved_names = ["SaveGames", "Logs", "Config"]

    # Check for invalid characters
    if any(char in folder_name for char in invalid_characters):
        return False

    # Check if the name ends in a period or consists of only spaces and periods
    if folder_name.endswith(".") or folder_name.strip(" .") == "":
        return False

    # Check if the name is a reserved folder name
    if folder_name in reserved_names:
        return False

    # Check if the name is a system-reserved name
    system_reserved_names = [
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
        "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    if folder_name.upper() in system_reserved_names:
        return False

    # Check if the name is a reserved name in Windows file system
    reserved_words = [
        "CON", "PRN", "AUX", "NUL", "COM", "LPT", "CONIN$", "CONOUT$", "PRN$",
        "AUX$", "NUL$", "COM1$", "COM2$", "COM3$", "COM4$", "COM5$", "COM6$",
        "COM7$", "COM8$", "COM9$", "LPT1$", "LPT2$", "LPT3$", "LPT4$", "LPT5$",
        "LPT6$", "LPT7$", "LPT8$", "LPT9$"
    ]
    if folder_name.upper() in reserved_words:
        return False

    return True

def backupNameMenu(prompt):
    global screen

    if(type(prompt) == type("")):
        prompt = prompt.split("\n")

    curstate = curses.curs_set(1)
    folder_name = ""
    while True:
        screen.clear()
        for i, prom in enumerate(prompt):
            screen.addstr(i, 0, prom)
        screen.addstr(len(prompt)-1, 0, prompt[len(prompt)-1]+": "+folder_name)
        screen.refresh()
        key = screen.getch()

        if key == curses.KEY_BACKSPACE or key in [127, 8]:
            folder_name = folder_name[:-1]
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            if is_valid_folder_name(folder_name):
                return folder_name
            else:
                infoScreen("Invaild backup name\nBackup name can not contain any of these characters \\ / : * ? \" < > | .")
                screen.refresh()
                curses.napms(2000)  # Display the error message for 2 seconds
                folder_name = ""
        else:
            folder_name += chr(key)
    
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
        saveName = backupNameMenu("Enter none to go back to the main menu\nEnter backup name")
        if(not saveName in folders):
            confirm = True
        else:
            ans = yornMenu("There is already a backup by that name. Overwrite?")
            if(ans):
                confirm = True
            else:
                confirm = False
    if(saveName.lower == "none"):
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, saveName)
    try:
        shutil.rmtree(backupName,ignore_errors=True)
        shutil.copytree(saveGame, backupName)
    except Exception as error:
        scrollInfoMenu("Could not make backup. Error below:\n"+str(error))
    
def restoreBackup():
    """Restores a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it replaces the current SaveGames folder
    with the contents of the chosen backup.
    """

    current_directory = os.getcwd()
    folders = getBackups()
    prompt = "Choose Backup to restore\n"
    options = "Go back to main menu"
    is_exe = isExe()
    linux = isLinux()

    for i in range(len(folders)):
        options+="\n"+str(folders[i])

    choice = scrollSelectMenu(prompt,options,-1,1)
    if(extract_numbers(choice) == 0):
        return
    
    start = time.time()
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    uesavePath = ""

    if(is_exe):
        file = __file__
        bundle_dir = path.abspath(path.dirname(file)) 
        if not linux:
            path_to_dat = path.join(bundle_dir, 'uesave.exe')
        else:
            path_to_dat = path.join(bundle_dir, 'uesave')
        uesavePath = path_to_dat
    else:
        if not linux:
            uesaveExe = os.path.expandvars("%APPDATA%/../../.cargo/bin")
        else:
            uesaveExe = os.path.expandvars("$HOME/.cargo/bin")
        
        if os.path.exists(os.path.join(uesaveExe,"uesave.exe")) or os.path.exists(os.path.join(uesaveExe,"uesave")):
            if not linux:
                uesaveExe = os.path.join(uesaveExe,"uesave.exe")
            else:
                uesaveExe = os.path.join(uesaveExe,"uesave")
        elif os.path.exists("uesave.exe") or os.path.exists("uesave"):
            if not linux:
                uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
            else:
                uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave"
        else:
            prompt = "uesave could not be found\nPermission to download uesave?"
            perm = yornMenu(prompt)
            if("y" in perm.lower()):
                if not linux:
                    downURL = "https://raw.githubusercontent.com/O2theC/CrabChampionSaveManager/main/uesave.exe"
                    response = requests.get(downURL)
                    with open(__file__[:__file__.rindex("\\")+1]+"uesave.exe", 'wb') as file:
                        file.write(response.content)
                    uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
                else:
                    downURL = "https://raw.githubusercontent.com/O2theC/CrabChampionSaveManager/main/uesave"
                    response = requests.get(downURL)
                    with open(__file__[:__file__.rindex("\\")+1]+"uesave", 'wb') as file:
                        file.write(response.content)
                    uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave"
            else:
                scrollInfoMenu("No copy of uesave could be found and no permission was given to download a copy\nRestore Backups requires uesave to work\nPress Enter to return to main menu",-1)
                return
        uesavePath = uesaveExe
    None
    saveGame+="\\SaveSlot.sav"
    backupName+="\\SaveSlot.sav"
    saveGame = "\""+saveGame+"\""
    backupName = "\""+backupName+"\""
    infoScreen("0/8")
    proc1 = subprocess.Popen(uesavePath+" to-json -i "+saveGame+" -o currentSave.json")
    infoScreen("1/8")
    proc1.wait()
    with open("currentSave.json") as JSON_File:
        saveJSON = json.load(JSON_File)
    os.remove("currentSave.json")
    infoScreen("2/8")
    proc2 = subprocess.Popen(uesavePath+" to-json -i "+backupName+" -o backupSave.json")    
    proc2.wait()
    with open("backupSave.json") as JSON_File:
        backupJSON = json.load(JSON_File)
    os.remove("backupSave.json")   
    infoScreen("3/8") 
    try:
        autoSaveJson = copy.deepcopy(backupJSON["root"]["properties"]["AutoSave"])
    except:
        scrollInfoMenu("Selected backup has no save\nPress Enter to return to main menu")
        return
    infoScreen("4/8")
    try:
        saveJSON["root"]["properties"]["AutoSave"] = autoSaveJson
    except Exception as error:
        scrollInfoMenu("Error when replacing autosave on current save, Error below\n"+str(error)+"\nPress Enter to return to main menu")
        input("Press Enter to continue . . .")
        return
    infoScreen("5/8")
    with open("restoredSave.json","w") as JSON_File:
        JSON_File.write(json.dumps(saveJSON, indent=4))
    infoScreen("6/8")
    proc1 = subprocess.Popen(uesavePath+" from-json -i restoredSave.json -o SaveGames/SaveSlot.sav")
    #proc2 = subprocess.Popen(uesavePath+" from-json -i restoredSave.json -o test/SaveSlot.sav")
    proc1.wait()
    os.remove("restoredSave.json")
    infoScreen("7/8")
    #proc2.wait()
    shutil.copyfile("SaveGames/SaveSlot.sav","SaveGames/SaveSlotBackupA.sav")
    shutil.copyfile("SaveGames/SaveSlot.sav","SaveGames/SaveSlotBackupB.sav")
    infoScreen("8/8")
    infoScreen("Backup Restored - "+str(folders[extract_numbers(choice)-1]))
    stop = time.time()
    #print("it took",round(stop-start,3)," seconds")
    return

def editBackup():

    """Edits a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it opens the SaveSlot.sav file for editing
    using the uesave tool. Two backup copies (SaveSlotBackupA.sav and SaveSlotBackupB.sav)
    are created before editing.
    """

    current_directory = os.getcwd()
    folders = getBackups()
    prompt = "Choose Backup to edit\n"
    options = "Go back to main menu\nEdit current save"
    is_exe = isExe()
    linux = isLinux()

    for i in range(len(folders)):
        options+="\n"+str(folders[i])
    choice = scrollSelectMenu(prompt,options,-1,1)
    if(choice == 0):
        return
    saveFile = ""
    if(choice == 1):
        saveFile = os.path.join(current_directory,"SaveGames")
    else:
        saveFile = os.path.join(current_directory,str(folders[extract_numbers(choice)-2]))
    saveFile = os.path.join(saveFile,"SaveSlot.sav")
    saveBackA = saveFile.replace("SaveSlot.sav","SaveSlotBackupA.sav")
    saveBackB = saveFile.replace("SaveSlot.sav","SaveSlotBackupB.sav")
    sf = saveFile
    
    infoScreen("close window opened by uesave to continue\nBackup Opened : "+saveFile[saveFile.rindex("\\",0,saveFile.rindex("\\"))+1:saveFile.rindex("\\")].replace("SaveGames","Current Save"))
    saveFile = "\""+saveFile+"\""
    if(is_exe):
        file = __file__
        bundle_dir = path.abspath(path.dirname(file)) 
        if not linux:
            path_to_dat = path.join(bundle_dir, 'uesave.exe')
        else:
            path_to_dat = path.join(bundle_dir, 'uesave')
        subprocess.run(str(path_to_dat)+" edit "+str(saveFile))
    else:
        if not linux:
            uesaveExe = os.path.expandvars("%APPDATA%/../../.cargo/bin")
        else:
            uesaveExe = os.path.expandvars("$HOME/.cargo/bin")
            
        if os.path.exists(os.path.join(uesaveExe,"uesave.exe")) or os.path.exists(os.path.join(uesaveExe,"uesave")):
            if not linux:
                uesaveExe = os.path.join(uesaveExe,"uesave.exe")
            else:
                uesaveExe = os.path.join(uesaveExe,"uesave")
        elif os.path.exists("uesave.exe") or os.path.exists("uesave"):
            if not linux:
                uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
            else:
                uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave"
        else:
            prompt = "uesave could not be found\nPermission to download uesave?"
            perm = yornMenu(prompt)
            if("y" in perm.lower()):
                if not linux:
                    downURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/uesave.exe"
                    response = requests.get(downURL)
                    with open(__file__[:__file__.rindex("\\")+1]+"uesave.exe", 'wb') as file:
                        file.write(response.content)
                    uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
                else:
                    downURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/uesave"
                    response = requests.get(downURL)
                    with open(__file__[:__file__.rindex("\\")+1]+"uesave", 'wb') as file:
                        file.write(response.content)
                    uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave"
            else:
                scrollInfoMenu("No copy of uesave could be found and no permission was given to download a copy\nEdit Backups requires uesave to work\nPress Enter to return to main menu")
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
    prompt = "Choose Backup to delete\n"
    options = "Go back to main menu"
    for i in range(len(folders)):
        options+="\n"+str(folders[i])
    choice = scrollSelectMenu(prompt,options,-1,1)
    if(extract_numbers(choice) == 0):
        return
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    try:
        shutil.rmtree(backupName)
    except Exception as error:
        scrollInfoMenu("Could not delete backup. Error below:\n"+str(error),-1)

def listBackups():
    """Lists all the available backups of the save game.
    
    Retrieves the list of backup folders and displays them to the user.
    """
    
    current_directory = os.getcwd()
    items = os.listdir(current_directory)
    folders = getBackups()
    prompt = str(len(folders))+" Backups Stored\nCurrent Backups\n"
    backups = "Go back to main menu\n"
    for i,name in enumerate(folders):
        if(i == 0):
            backups += str(name)
        else:
            backups += "\n"+str(name)
            
    scrollSelectMenu(prompt,backups)

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
    prompt = "Choose Backup to update\n"
    options = "Go back to main menu"

    for i in range(len(folders)):
        options += f"\n{ str(folders[i]) }"
    
    choice = scrollSelectMenu(prompt,options,-1,1)
    if(extract_numbers(choice) == 0):
        return
    
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[extract_numbers(choice)-1])
    try:
        shutil.rmtree(backupName,ignore_errors=True)
        shutil.copytree(saveGame, backupName)
        return
    except Exception as error:
        info = "Could not update backup. Error below:\n"
        info += str(error)
        scrollInfoMenu(info,-1)
        return

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

def updateScript(screen):
    is_exe = isExe()

    perm = yornMenu("There is a newer version available\nWould you like to update to the latest version?")
    if(perm):
        if(is_exe):
            downloadLatestURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.exe"
        else:
            downloadLatestURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.py"
        try:
            updaterURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/updater.exe"
            
            response = requests.get(downloadLatestURL)
            path = os.path.join(os.getcwd(),downloadLatestURL[downloadLatestURL.rindex("/")+1:])
            with open(path, 'wb') as file:
                file.write(response.content)

            if(is_exe):
                response = requests.get(updaterURL)
                path = os.path.join(os.getcwd(),updaterURL[updaterURL.rindex("/")+1:])
                with open(path, 'wb') as file:
                    file.write(response.content)
                subprocess.Popen(["updater.exe"], shell=True)
                return
        except:
            infoScreen("Could not download latest version\nThis program may be corrupted\npress any key to continue")
            screen.getch()
            exit_helper(1)
        infoScreen("Latest Version succesfully downloaded\nRestart required for changes to take effect\npress any key to continue")
        screen.getch()
        exit_helper(0)
    else:
        return
 
def uesaveCheck():
    is_exe = isExe()
    if not is_exe:
        return ""
    else:
        return "\n(requires uesave)"

def makeScreen():
    screen = curses.initscr()
    curses.noecho()  # Don't display user input
    curses.cbreak()  # React to keys immediately without Enter
    screen.keypad(True)  # Enable special keys (e.g., arrow keys)
    return screen

def scrollSelectMenu(prompt,options,window_height = -1,buffer_size = 1):
    global screen
    
    
    if(type(options) == type("")):
        options = options.split("\n")
    if(type(prompt) == type("")):
        prompt = prompt.split("\n")
    
    if(window_height == -1):
        autoSize = True
        window_height = 1000
    else:
        autoSize = False
    
        
    window_height = min(window_height,screen.getmaxyx()[0]-(3+len(prompt)))
    window_height = max(1,window_height)
    
    oBufSize = buffer_size
    
    buffer_size = min(buffer_size,window_height//2 - 1 + window_height % 2)
    buffer_size = max(buffer_size,0)
    
    selected_option = 0
    scroll_window = 0
    curstate = curses.curs_set(0)
    while True:
        screen.clear()
        
        # Display the main prompt
        for i, prom in enumerate(prompt):
            screen.addstr(i, 0, prom)
        
        # Display the options
        for i, option in enumerate(options):
            
            if(i>=scroll_window and i <scroll_window+window_height):
            
                if i == selected_option:
                    # Highlight the selected option
                    screen.addstr((i + len(prompt) - scroll_window), 1, "> " + option, curses.A_BOLD)
                else:
                    screen.addstr((i + len(prompt) - scroll_window), 1, " " + option)
        
        screen.addstr(min(window_height,len(options)) + len(prompt)+1, 0, "Use arrow keys to navigate options. Press Enter to select.")
        screen.refresh()
        key = screen.getch()
        
        if(autoSize):            
            window_height = screen.getmaxyx()[0]-(3+len(prompt))
            
            buffer_size = oBufSize
    
            buffer_size = min(buffer_size,window_height//2 - 1 + window_height % 2)
            buffer_size = max(buffer_size,0)
            
            
        
        

        if key == curses.KEY_UP and selected_option > 0:
            selected_option -= 1
        elif key == curses.KEY_DOWN and selected_option < len(options) - 1:
            selected_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            return selected_option
              
        #if the selected item goes out of the effective window then the scrolling window moves up or down to keep the selective item in the effective window, the effective window is in the center of the scrolling window and is scrolling_window_size-(buffer_size*2) = effective_window_size, and effective window size can not be smaller than 1 and not any larger than scrolling_window_size
        if(selected_option < scroll_window+buffer_size and scroll_window > 0):
            scroll_window-=1
        elif(selected_option > scroll_window+window_height-(1+buffer_size) and scroll_window < len(options)-window_height):
            scroll_window+=1

def scrollInfoMenu(info,window_height = -1):
    global screen


    if(type(info) == type("")):
        info = info.split("\n")
    if(window_height == -1):
        autoSize = True
        window_height = 1000
    else:
        autoSize = False
    window_height = min(window_height,screen.getmaxyx()[0]-4)
    window_height = max(1,window_height)
    
    scroll_window = 0
    curstate = curses.curs_set(0)
    while True:
        screen.clear()
        if(autoSize):
            window_height = screen.getmaxyx()[0]-4
        # Display the options
        for i, inf in enumerate(info):
            
            if(i>=scroll_window and i <scroll_window+window_height):
                screen.addstr((i - scroll_window)+1, 0, str(inf))
        
        screen.addstr(window_height +2, 0, "Use arrow keys to scroll up and down. Press Enter to go back to main menu.")
        screen.refresh()
        key = screen.getch()

        if key == curses.KEY_UP and scroll_window > 0:
            scroll_window -= 1
        elif key == curses.KEY_DOWN and scroll_window < len(info) - window_height:
            scroll_window += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            return

def yornMenu(prompt):
    global screen
    
    curstate = curses.curs_set(1)
    ans = ""
    while True:
        screen.clear()
        
        screen.addstr(0,0,prompt+" [Y/n]: "+str(ans))
        screen.refresh()
        key = screen.getch()

        if key == 121:
            ans = "y"
        elif key == 110:
            ans = "n"
        elif key == curses.KEY_BACKSPACE or key in [127,8]:
            ans = ""
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            if(ans == ""):
                return True
            elif(ans == "n"):
                return False
            elif(ans == "y"):
                return True
            
def infoScreen(info):
    curstate = curses.curs_set(0)
    screen.clear()
    screen.addstr(1,0,info)
    screen.refresh()
    curses.curs_set(curstate)

screen = makeScreen()
            
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
VersionValue = versionToValue(Version)
LatestValue = versionToValue(LatestVersion)

if(LatestValue == -1):
    mainMenuPrompt += "\n\nCould not get latest version"
elif(VersionValue < LatestValue):
    updateScript(isExe())
    exit_helper(0)
elif(VersionValue > LatestValue):
    mainMenuPrompt += "\n\n***BETA WARNING***"
else:
    mainMenuPrompt += "\n\nYou have the latest version"



            
if(currentDirCheck()):
    try:
        if not isLinux:
            new_dir = os.path.expandvars("%APPDATA%/../Local/CrabChampions/Saved")
        else:
            new_dir = os.path.expandvars("$HOME/.local/share/Steam/steamapps/compatdata/774801/pfx/drive_c/users/steamuser/AppData/Local/CrabChampions/Saved")
        os.chdir(new_dir)
    except:
        infoScreen("Could not find save game directory\nYou either don't have Crab Champions installed\n or you have it installed in a different spot than the default\n if it is installed in a different spot than the defualt then put this file in the equivalent of CrabChampions\Saved\nPress any key to continue . . .")
        screen.getch()
        exit_helper(0)




mainMenuPrompt += "\n\nWelcome to Crab Champion Save Manager"
mainMenuPrompt += "\nMade By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager\nWhat do you want to do\n"
while(True):
    options = f"""Edit save game {uesaveCheck()}
    Backup Save
    Update backup
    Restore Save from backup (Warning : Deletes current save)
    Delete backup\nList Backups
    Info/How to use
    Exit"""

    choice = scrollSelectMenu(mainMenuPrompt,options,-1,1)+1
    if(choice == 1):
        editBackup() # turned to curse
    elif(choice == 2):
        backupSave()
    elif(choice == 3):
        updateBackup() # turned to curse
    elif(choice == 4):
        restoreBackup()# turned to curse
    elif(choice == 5):
        deleteBackup() # turned to curse
    elif(choice == 6):
        listBackups()
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

        scrollInfoMenu(infoList,-1)
    elif(choice == 8):
        break
    
exit_helper(0)