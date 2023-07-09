import copy
import hashlib
import os
import shutil
import time
import subprocess
import sys
import json
from os import path
import threading

def closeScreen():
    global screen
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()

def exiting(var):
    try:
        closeScreen()
        saveSettings()
    except:
        None
    exit(var)
    
try:
    import requests
    import curses
except:
    print("Not all libraries are installed")
    perm = input("Permission to download libraries? [y/N]\n")
    if("y" in perm.lower()):
        os.system("pip install windows-curses")
        os.system("pip install requests")
        import requests
        import curses
    else:
        print("no permission given, script can't start")
        exiting(0)



def parseInt(input_string):
    """Converts the input string to an integer if possible, otherwise returns -1."""
    try:
        return int(input_string)
    except:
        return -1

def isValidFolderName(folder_name):
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
        for i , prom in enumerate(prompt):
            screen.addstr(i, 0, prom)
        screen.addstr(len(prompt)-1, 0, prompt[len(prompt)-1]+": "+folder_name)
        screen.refresh()
        key = screen.getch()

        if key == curses.KEY_BACKSPACE or key in [127, 8]:
            folder_name = folder_name[:-1]
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            if(folder_name == ""):
                return ""
            elif isValidFolderName(folder_name):
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
        saveName = backupNameMenu("Enter nothing to go back to the main menu\nEnter backup name")
        if(not saveName in folders):
            confirm = True
        else:
            ans = yornMenu("There is already a backup by that name. Overwrite?")
            if(ans):
                confirm = True
            else:
                confirm = False
    if(saveName == ""):
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
    for i in range(len(folders)):
        options+="\n"+str(folders[i])
    choice = scrollSelectMenu(prompt,options,-1,1)
    if(parseInt(choice) == 0):
        return
    start = time.time()
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[parseInt(choice)-1])
    uesavePath = ""
    if(isExe):
        file = __file__
        bundle_dir = path.abspath(path.dirname(file)) 
        path_to_dat = path.join(bundle_dir, 'uesave.exe')
        uesavePath = path_to_dat
    else:
        #%APPDATA%/../../.cargo/bin
        uesaveExe = os.path.expandvars("%APPDATA%/../../.cargo/bin")
        
        if(os.path.exists(os.path.join(uesaveExe,"uesave.exe"))):
            uesaveExe = os.path.join(uesaveExe,"uesave.exe")
        elif(os.path.exists("uesave.exe")):
            uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
        else:
            prompt = "uesave.exe could not be found\nPermission to download uesave?"
            perm = yornMenu(prompt)
            if("y" in perm.lower()):
                downURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/uesave.exe"
                response = requests.get(downURL)
                with open(__file__[:__file__.rindex("\\")+1]+"uesave.exe", 'wb') as file:
                    file.write(response.content)
                uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
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
    infoScreen("Backup Restored - "+str(folders[parseInt(choice)-1]))
    stop = time.time()
    #print("it took",round(stop-start,3)," seconds")
    return

def editBackup(isExe):

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
    for i in range(len(folders)):
        options+="\n"+str(folders[i])
    choice = scrollSelectMenu(prompt,options,-1,1)
    if(choice == 0):
        return
    saveFile = ""
    if(choice == 1):
        saveFile = os.path.join(current_directory,"SaveGames")
    else:
        saveFile = os.path.join(current_directory,str(folders[parseInt(choice)-2]))
    saveFile = os.path.join(saveFile,"SaveSlot.sav")
    saveBackA = saveFile.replace("SaveSlot.sav","SaveSlotBackupA.sav")
    saveBackB = saveFile.replace("SaveSlot.sav","SaveSlotBackupB.sav")
    sf = saveFile
    
    infoScreen("close window opened by uesave to continue\nBackup Opened : "+saveFile[saveFile.rindex("\\",0,saveFile.rindex("\\"))+1:saveFile.rindex("\\")].replace("SaveGames","Current Save"))
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
            prompt = "uesave.exe could not be found\nPermission to download uesave?"
            perm = yornMenu(prompt)
            if("y" in perm.lower()):
                downURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/uesave.exe"
                response = requests.get(downURL)
                with open(__file__[:__file__.rindex("\\")+1]+"uesave.exe", 'wb') as file:
                    file.write(response.content)
                uesaveExe = __file__[:__file__.rindex("\\")+1]+"uesave.exe"
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
    if(parseInt(choice) == 0):
        return
    backupName = os.path.join(current_directory, folders[parseInt(choice)-1])
    try:
        shutil.rmtree(backupName)
    except Exception as error:
        scrollInfoMenu("Could not delete backup. Error below:\n"+str(error),-1)

def listBackups():
    global screen
    """Lists all the available backups of the save game.
    
    Retrieves the list of backup folders and displays them to the user.
    """
    
    # current time in seconds - ["root"]["properties"]["AutoSave"]["Struct"]["value"]["Struct"]["CurrentTime"]["Int"]["value"]
    
    loadCache()
    current_directory = os.getcwd()
    folders = getBackups()
    prompt = str(len(folders))+" Backups Stored\nCurrent Backups\n"
    backups = "Go back to main menu\n"
    maxLength = 0
    for i in range(len(folders)):
       maxLength = max(maxLength,len(folders[i]))
    for i,name in enumerate(folders):
        if(i == 0):
            backups += str(name)+backupListInfo(name,maxLength)
        else:
            backups += "\n"+str(name)+backupListInfo(name,maxLength)
            
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
        options+="\n"+str(folders[i])
    choice = scrollSelectMenu(prompt,options,-1,1)
    if(parseInt(choice) == 0):
        return
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[parseInt(choice)-1])
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

def updateScript(isExe):
    perm = yornMenu("There is a newer version available\nWould you like to update to the latest version?")
    if(perm):
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
                subprocess.Popen(["CrabChampionSaveManagerUpdater.exe"], shell=True)
                return
        except:
            infoScreen("Could not download latest version\nThis program may be corrupted\npress any key to continue")
            screen.getch()
            exiting(1)
        infoScreen("Latest Version succesfully downloaded\nRestart required for changes to take effect\npress any key to continue")
        screen.getch()
        exiting(0)
    else:
        return

def makeScreen():
    global screen
    screen = curses.initscr()
    curses.noecho()  # Don't display user input
    curses.cbreak()  # React to keys immediately without Enter
    screen.keypad(True)  # Enable special keys (e.g., arrow keys)

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

def userInputMenuNum(prompt,errorMessage,lowLimit = -2000000000,highLimit = 2000000000):
    global screen

    if(type(prompt) == type("")):
        prompt = prompt.split("\n")

    curstate = curses.curs_set(1)
    num = ""
    while True:
        screen.clear()
        for i , prom in enumerate(prompt):
            screen.addstr(i, 0, prom)
        screen.addstr(len(prompt)-1, 0, prompt[len(prompt)-1]+": "+num)
        screen.refresh()
        key = screen.getch()

        if key == curses.KEY_BACKSPACE or key in [127, 8]:
            num = num[:-1]
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            if (int(num)<highLimit and int(num)>lowLimit):
                return int(num)
            else:
                infoScreen(errorMessage)
                screen.refresh()
                curses.napms(2000)  # Display the error message for 2 seconds
                folder_name = ""
        else:
            if(key in range(48,58)):
                num += chr(key)
 
def settings():
    global configJSON
    global TermHeight
    global TermWidth
    defaultJSON = "{\"Start_Up\":{\"Terminal_Size\":{\"Height\":30,\"Width\":120}}}"
    relative_path = "CrabChampionSaveManager/config.json"

    # Create the directory if it doesn't exist
    directory = os.path.dirname(relative_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file = open("CrabChampionSaveManager/config.json","r+")
    try:
        configJSON = json.loads(file.read())
    except:
        configJSON = json.loads(defaultJSON)
        
    prompt = "Select setting to edit"
    options = "Back to main menu\nStart Up Settings"
    while True:
        choice = scrollSelectMenu(prompt,options)
        if(choice == 0):
            break
        elif(choice == 1):
            promptSUS = "Select setting to edit"
            optionsSUS = "Back\nTerminal Size"
            while True:
                choice = scrollSelectMenu(promptSUS,optionsSUS)
                if(choice == 0):
                    break
                elif(choice == 1):
                    promptTS = "Select setting to edit"
                      
                    while True:
                        height = configJSON["Start_Up"]["Terminal_Size"]["Height"]
                        width = configJSON["Start_Up"]["Terminal_Size"]["Width"]
                        optionsTS = f"Back\nHeight - {height}\nWidth - {width}\nManuel"
                        choice = scrollSelectMenu(promptTS,optionsTS)
                        if(choice == 0):
                            break
                        elif(choice == 1):
                            prompt = f"Enter new height for terminal at start up (Currently at {TermHeight})\nIt is not recommend to go below 30"
                            configJSON["Start_Up"]["Terminal_Size"]["Height"] = userInputMenuNum(prompt,"Invaild number, number must be greater than or equal to 1",0)
                            saveSettings()
                        elif(choice == 2):
                            prompt = f"Enter new width for terminal at start up (Currently at {TermWidth})\nIt is not recommend to go below 120"
                            configJSON["Start_Up"]["Terminal_Size"]["Width"] = userInputMenuNum(prompt,"Invaild number, number must be greater than or equal to 1",0)
                            saveSettings()
                        elif(choice == 3):
                            screen.nodelay(True)
                            curstate = curses.curs_set(0)
                            while(True):
                                screen.clear()
                                
                                screen.addstr(0,0,"Change your terminal size to what you want")
                                screen.addstr(1,0,"Current Width : "+str(screen.getmaxyx()[1]))
                                screen.addstr(2,0,"Current Height : "+str(screen.getmaxyx()[0]))
                                screen.addstr(3,0,"Press enter when you want to save the terminal size")
                                
                                screen.refresh()
                                key = screen.getch()
                                
                                if(key in [13,10] or key == curses.KEY_ENTER):
                                    break
                            screen.nodelay(False)
                            curses.curs_set(curstate)
                            configJSON["Start_Up"]["Terminal_Size"]["Width"] = screen.getmaxyx()[1]
                            configJSON["Start_Up"]["Terminal_Size"]["Height"] = screen.getmaxyx()[0]
                            saveSettings()
                        
def loadSettings():
    global configJSON
    global TermHeight
    global TermWidth
    defaultJSON = "{\"Start_Up\":{\"Terminal_Size\":{\"Height\":30,\"Width\":120}}}"
    relative_path = "CrabChampionSaveManager/config.json"

    # Create the directory if it doesn't exist
    directory = os.path.dirname(relative_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # while(not os.path.exists(directory)):
    #     time.sleep(.1)
    
    try:
        file = open("CrabChampionSaveManager/config.json","r+")
    except:
        file = open("CrabChampionSaveManager/config.json","w")
        file.close()
        file = open("CrabChampionSaveManager/config.json","r+")
    try:
        configJSON = json.loads(file.read())
    except Exception as e:
        configJSON = json.loads(defaultJSON)
        
    try:
        TermHeight = configJSON["Start_Up"]["Terminal_Size"]["Height"]
        TermHeight = max(TermHeight,15)
    except:
        configJSON["Start_Up"]["Terminal_Size"]["Height"] = 30
        TermHeight = 30
        
    try:
        TermWidth = configJSON["Start_Up"]["Terminal_Size"]["Width"]
        TermWidth = max(TermWidth,120)
    except:
        configJSON["Start_Up"]["Terminal_Size"]["Width"] = 120  
        TermWidth = 120
    file.seek(0)
    file.write(json.dumps(configJSON,indent=4))
    file.truncate()
    file.close()

def saveSettings():
    relative_path = "CrabChampionSaveManager/config.json"
    global configJSON
    directory = os.path.dirname(relative_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file = open("CrabChampionSaveManager/config.json","w")
    file.write(json.dumps(configJSON,indent=4))

def getChecksum(file_path):
    # Get the absolute path of the file
    absolute_path = os.path.abspath(file_path)

    # Open the file in binary mode and read it in chunks
    with open(absolute_path, 'rb') as file:
        # Create a SHA-512 hash object
        sha512_hash = hashlib.sha512()

        # Read the file in chunks to avoid loading the entire file into memory
        for chunk in iter(lambda: file.read(4096), b''):
            # Update the hash object with the current chunk
            sha512_hash.update(chunk)

    # Get the hexadecimal representation of the hash
    checksum = sha512_hash.hexdigest()

    return checksum

def loadCache():
    global lock
    lock = threading.Lock()
    global cacheJSON
    backups = getBackups()
    cachePath = "CrabChampionSaveManager/backupDataCache.json"
    
    # Create the directory if it doesn't exist
    directory = os.path.dirname(cachePath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # while(not os.path.exists(directory)):
    #     time.sleep(.1)
    
    try:
        file = open("CrabChampionSaveManager/backupDataCache.json","r+")
    except:
        file = open("CrabChampionSaveManager/backupDataCache.json","w")
        file.close()
        file = open("CrabChampionSaveManager/backupDataCache.json","r+")
    try:
        cacheJSON = json.loads(file.read())
    except:
        cacheJSON = json.loads("{}")
    threads = []
    for backup in backups:
        currentCS = getChecksum(backup+"/SaveSlot.sav")
        try:
            cacheCS = cacheJSON["BackupData"][backup]["CheckSum"]
        except:
            cacheCS = ""
        if(currentCS != cacheCS):
            t = threading.Thread(target=genBackupData, args=(backup,))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()
    file.seek(0)
    file.write(json.dumps(cacheJSON,indent=4))
        
def spaceBeforeUpper(string):
    result = string[0]  # The first uppercase letter should not have a space before it
    for char in string[1:]:
        if char.isupper():
            result += ' ' + char  # Insert a space before the uppercase letter
        else:
            result += char  # Append lowercase letters as they are
    return result
 
def parseDiffMods(mods):
    for i in range(len(mods)):
        mods[i] = spaceBeforeUpper(str(mods[i][25:]))
    return mods
            
def genBackupData(backupName):
    global lock
    global cacheJSON
    savFilePath = ""+backupName+"/SaveSlot.sav"
    savFile = savFilePath
    #print(savFile)
    #print(savFile.replace("SaveSlot.sav","data.json"))
    proc = subprocess.Popen("uesave to-json -i \""+savFile+"\" -o \""+savFile.replace("SaveSlot.sav","data.json")+"\"")
    proc.wait()
    saveFile = open(savFile.replace("SaveSlot.sav","data.json"),"r")
    saveJSON = json.loads(saveFile.read())
    saveFile.close()
    os.remove(savFile.replace("SaveSlot.sav","data.json"))
    try:
        saveJSON = saveJSON["root"]["properties"]["AutoSave"]["Struct"]["value"]["Struct"]
    except:
        lock.acquire()
        cacheJSON["BackupData"][backupName] = {}
        cacheJSON["BackupData"][backupName]["CheckSum"] = getChecksum(backupName+"/SaveSlot.sav")
        cacheJSON["BackupData"][backupName]["NoSave"] = True
        lock.release()
        return
    backupJSON = json.loads("{}")
    #saveJSON = saveJSON["AutoSave"]
    #run time in seconds (int) ["CurrentTime"]["Int"]["value"]
    #score                     ["Points"]["Int"]["value"]
    #difficulty                ["Difficulty"]["Enum"]["value"] , vaild values are ECrabDifficulty::Easy and ECrabDifficulty::Nightmare , it seems that for normal, the value is not there, this suggests the games uses normal as a default and this value in the .sav file is an override 
    #island num                ["NextIslandInfo"]["Struct"]["value"]["Struct"]["CurrentIsland"]["Int"]["value"]
    # diff mods                ["DifficultyModifiers"]["Array"]["value"]["Base"]["Enum"]
    backupJSON[backupName] = {}
    backupJSON[backupName]["RunTime"] = saveJSON["CurrentTime"]["Int"]["value"]
    backupJSON[backupName]["Score"] = saveJSON["Points"]["Int"]["value"]
    try:
        diff = saveJSON["Difficulty"]["Enum"]["value"]
        diff = diff[diff.index("::")+2:]
    except:
        diff = "Normal"
    backupJSON[backupName]["Diff"] = diff
    backupJSON[backupName]["IslandNum"] = saveJSON["NextIslandInfo"]["Struct"]["value"]["Struct"]["CurrentIsland"]["Int"]["value"]
    try:
        backupJSON[backupName]["DiffMods"] = parseDiffMods(saveJSON["DifficultyModifiers"]["Array"]["value"]["Base"]["Enum"])
    except:
        backupJSON[backupName]["DiffMods"] = []
    backupJSON[backupName]["CheckSum"] = getChecksum(backupName+"/SaveSlot.sav")
    backupJSON[backupName]["NoSave"] = False
    lock.acquire()
    try:
        cacheJSON["BackupData"][backupName] = backupJSON[backupName]
    except:
        cacheJSON["BackupData"] = {}
        cacheJSON["BackupData"][backupName] = backupJSON[backupName]
    lock.release()

def formatTime(s):
    if(s%60<10):
        z = "0"
    else:
        z = ""
    if(s//60%60<10):
        zz = "0"
    else:
        zz = ""
    if(s//60//60%24<10):
        zzz = "0"
    else:
        zzz = ""
    
    if(s>=60*60*24):
        return str(s//60//60//24)+":"+str(zzz)+str(s//60//60%24)+":"+str(zz)+str(s//60%60)+":"+str(z)+str(s%60)
    elif(s>=60*60):
        return str(s//60//60)+":"+str(zz)+str(s//60%60)+":"+str(z)+str(s%60)
    elif(s>=60):
        return str(s//60)+":"+str(z)+str(s%60)
    else:
        return s
        
def backupListInfo(backupName,maxLength):
    infoString = ""
    for _ in range(maxLength-len(backupName)):
        infoString+=" "
    infoString += " - "
    try:
        noSave = cacheJSON["BackupData"][backupName]["NoSave"]
        if(not noSave):
            score = cacheJSON["BackupData"][backupName]["Score"]
            diff = cacheJSON["BackupData"][backupName]["Diff"]
            islandNum = cacheJSON["BackupData"][backupName]["IslandNum"]
            runtime = cacheJSON["BackupData"][backupName]["RunTime"]
            runtime = formatTime(runtime)
            infoString+=f"Time: {runtime}\tDiff: {diff}\tIsland: {islandNum}\tScore: {score}"
            return infoString
    except:
        None
    return ""
    
    
    


loadSettings()

start = time.time()
loadCache()
stop = time.time()
print(round(stop-start,2))
#exiting(0)
makeScreen()

curses.resize_term(TermHeight,TermWidth)  
            
# 30 x 120
Version = "2.1.1"
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

mainMenuPrompt = "Current Version : "+str(Version)
mainMenuPrompt += "\nLatest Version : "+str(LatestVersion)
VersionValue = versionToValue(Version)
LatestValue = versionToValue(LatestVersion)

if(LatestValue == -1):
    mainMenuPrompt += "\n\nCould not get latest version"
elif(VersionValue < LatestValue):
    updateScript(isExe)
elif(VersionValue > LatestValue):
    mainMenuPrompt += "\n\nooohh , you have a version that isn't released yet, nice"
else:
    mainMenuPrompt += "\n\nYou have the latest version"



            
if(currentDirCheck()):
    try:
        new_dir = os.path.expandvars("%APPDATA%\\..\\Local\\CrabChampions\\Saved")
        os.chdir(new_dir)
    except:
        infoScreen("Could not find save game directory\nYou either don't have Crab Champions installed\n or you have it installed in a different spot than the default\n if it is installed in a different spot than the defualt then put this file in the equivalent of CrabChampions\Saved\nPress any key to continue . . .")
        screen.getch()
        exiting(0)




mainMenuPrompt += "\n\nWelcome to Crab Champion Save Manager"
mainMenuPrompt += "\nMade By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager\nWhat do you want to do\n"
while(True):
    options = "Edit save game\nBackup Save\nUpdate backup\nRestore Save from backup (Warning : Deletes current save)\nDelete backup\nList Backups\nInfo/How to use\nSettings\nExit"
    choice = scrollSelectMenu(mainMenuPrompt,options,-1,1)+1
    if(choice == 1):
        editBackup(isExe) # turned to curse
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
        infoList = """Crab Champion Save Manager
        Welcome to Crab Champion Save Manager, a script designed to help you manage your save files for the game Crab Champion.
        Made By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager
        This program provides the following options:\n

\nEdit Save Game:
    - Uses uesave to allow the user to edit the SaveSlot.sav file in a backup or your current save

 \nBackup Save:
    - backup up your current save with a custom name

 \nUpdate backup:
    - Update a already made backup with the current saved run

 \nRestore Save from Backup:
    - Restores a run from a backup

 \nDelete Backup:
    - Deletes a backup
    - Note: Deleting a backup cannot be undone, so be careful when removing backups.

 \nList Backups:
    - Lists all backups and trys to list some info about the run

 \nInfo/How to use:
    - provides info about the program and how to use it

 \Settings:
    - Change program settings

 \nExit:
    - Exits the program.

 This script uses uesave from https://github.com/trumank/uesave-rs, all credit for this goes to trumank,their
 program is in my opinion very well made and works very well
 Report issues and suggestions to https://github.com/O2theC/CrabChampionSaveManager
 This script has some elements that require access to the internet, this includes:
 Version Checking
 Downloading an updater for the .exe version of the program
 Downloading uesave"""
        scrollInfoMenu(infoList,-1)
    elif(choice == 8):
        settings()
    elif(choice == 9):
        break
    
exiting(0)
