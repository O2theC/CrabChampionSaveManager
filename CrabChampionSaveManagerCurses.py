import copy
import hashlib
import os
import shutil
import time
import subprocess
import platform
import sys
import json
from os import path
import threading


global isExe
global isLinux
global Version
isExe = False
isLinux = False

Version = "2.3.3"

if platform.system() == "Linux":
    isLinux =  True

if (getattr(sys, 'frozen', False)):
    isExe = True

def closeScreen():
    global screen
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()

def exiting(var):
    global screen
    try:
        screen.clear()
        closeScreen()
        saveSettings()
    except:
        None
    if(var == 0):
        sys.exit(0)
    elif(var == 1):
        sys.exit(1)
    
try:
    import requests
    import curses
except:
    print("Not all libraries are installed")
    perm = input("Permission to download libraries? [y/N]\n")
    if("y" in perm.lower()):
        if(not isLinux):
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
        infoScreen("Making backup\nThis might take a few seconds")
        shutil.rmtree(backupName,ignore_errors=True)
        shutil.copytree(saveGame, backupName)
        loadCache()
    except Exception as error:
        scrollInfoMenu("Could not make backup. Error below:\n"+str(error))
    
def restoreBackup():
    """Restores a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it replaces the current SaveGames folder
    with the contents of the chosen backup.
    """

    current_directory = os.getcwd()
    foldersInfo = getBackups(moreInfo=1)
    folders = getBackups()
    prompt = "Choose Backup to restore\n"
    options = "Go back to main menu"
    for i in range(len(foldersInfo)):
        options+="\n"+str(foldersInfo[i])
    choice = scrollSelectMenu(prompt,options,-1,1)
    if(parseInt(choice) == 0):
        return
    start = time.time()
    saveGame = os.path.join(current_directory, "SaveGames")
    backupName = os.path.join(current_directory, folders[parseInt(choice)-1])
    uesavePath = getUesavePath()
    if(uesavePath == ""):
        scrollInfoMenu("No copy of uesave could be found and no permission was given to download a copy\nPress Enter to return to main menu")
        return
    saveGame+="/SaveSlot.sav"
    backupName+="/SaveSlot.sav"
    saveGame = saveGame.replace("\\","/")
    backupName = backupName.replace("\\","/")
    saveGame = "\""+saveGame+"\""
    backupName = "\""+backupName+"\""
    infoScreen("0/8")
    proc1 = subprocess.Popen(uesavePath+" to-json -i "+saveGame+" -o currentSave.json",shell=True)
    infoScreen("1/8")
    proc1.wait()
    with open("currentSave.json") as JSON_File:
        saveJSON = json.load(JSON_File)
    os.remove("currentSave.json")
    infoScreen("2/8")
    proc2 = subprocess.Popen(uesavePath+" to-json -i "+backupName+" -o backupSave.json", shell=True)    
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
    proc1 = subprocess.Popen(uesavePath+" from-json -i restoredSave.json -o SaveGames/SaveSlot.sav", shell=True)
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

def editBackup():
    global isExe
    """Edits a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it opens the SaveSlot.sav file for editing
    using the uesave tool. Two backup copies (SaveSlotBackupA.sav and SaveSlotBackupB.sav)
    are created before editing.
    """

    current_directory = os.getcwd()
    foldersInfo = getBackups(moreInfo=1)
    folders = getBackups()
    prompt = "Choose Backup to edit\n"
    options = "Go back to main menu\nEdit current save"
    for i in range(len(foldersInfo)):
        options+="\n"+str(foldersInfo[i])
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
    saveFile = saveFile.replace("\\","/")
    infoScreen("close window opened by uesave to continue\nBackup Opened : "+saveFile[saveFile.rindex("/",0,saveFile.rindex("/"))+1:saveFile.rindex("/")].replace("SaveGames","Current Save"))
    saveFile = "\""+saveFile+"\""
    uesavePath = getUesavePath()
    if(uesavePath == ""):
        scrollInfoMenu("No copy of uesave could be found and no permission was given to download a copy\nPress Enter to return to main menu")
        return
    else:
        subprocess.run(uesavePath+" edit "+str(saveFile), shell=True)

    try:
        os.remove(saveBackA)
        os.remove(saveBackB)
    except:
        None
    shutil.copy(sf, saveBackA)
    shutil.copy(sf, saveBackB)
    
    #fix for terminal text editors like nano and vim
    curses.noecho()  # Don't display user input
    curses.cbreak()  # React to keys immediately without Enter
    screen.keypad(True)  # Enable special keys (e.g., arrow keys)
    
def deleteBackup():
    """Deletes a backup of the save game.
    
    Displays the available backups and prompts the user to choose one.
    If a backup is selected, it permanently deletes the corresponding backup folder.
    """
    
    current_directory = os.getcwd()
    foldersInfo = getBackups(moreInfo=1)
    folders = getBackups()
    prompt = "Choose Backup to delete\n"
    options = "Go back to main menu"
    for i in range(len(foldersInfo)):
        options+="\n"+str(foldersInfo[i])
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
    foldersInfo = getBackups(moreInfo=1)
    folders = getBackups()
    prompt = str(len(folders))+" Backups Stored\nCurrent Backups\n"
    backups = "Go back to main menu\n"
    for i,name in enumerate(foldersInfo):
        if(i == 0):
            backups += str(name)
        else:
            backups += "\n"+str(name)
            
    choice = scrollSelectMenu(prompt,backups,wrapMode=2)

def getBackups(moreInfo = 0):
    global cacheJSON
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
    if(moreInfo == 0):
        return folders
    else:
        #for the config json
    #run time seconds        - ["BackupData"][BackupName]["RunTime"]
    #score                   - ["BackupData"][BackupName]["Score"]
    #difficulty              - ["BackupData"][BackupName]["Diff"]
    #island num              - ["BackupData"][BackupName]["IslandNum"]
    #diff mods               - ["BackupData"][BackupName]["DiffMods"]
    #checksum                - ["BackupData"][BackupName]["CheckSum"]
    #nosave,if it has a save - ["BackupData"][BackupName]["NoSave"]
        ofold = folders
        try:
            loadCache()
            maxLenName = 0
            maxLenTime = 0
            maxLenDiff = 0
            maxLenIsland = 0
            maxLenScore = 0
            for name in folders:
                if(not cacheJSON["BackupData"][name]["NoSave"]):
                    maxLenName = max(maxLenName,len(name))
                    maxLenTime = max(maxLenTime,len(f"Time: {formatTime(cacheJSON['BackupData'][name]['RunTime'])}"))
                    maxLenDiff = max(maxLenDiff,len("Diff: "+str(cacheJSON["BackupData"][name]["Diff"])))
                    maxLenIsland = max(maxLenIsland,len("Island: "+str(cacheJSON["BackupData"][name]["IslandNum"])))
                    maxLenScore = max(maxLenScore,len("Score: "+str(cacheJSON["BackupData"][name]["Score"])))
            distance = 4
            maxLenTime += distance
            maxLenDiff += distance
            maxLenIsland += distance
            maxLenScore += distance
            for i in range(len(folders)):
                name = folders[i]
                if(not cacheJSON["BackupData"][name]["NoSave"]):
                    time = "Time: "+str(formatTime(cacheJSON['BackupData'][name]['RunTime']))
                    time = ensureLength(time,maxLenTime)
                    diff = "Diff: "+str(cacheJSON["BackupData"][name]["Diff"])
                    diff = ensureLength(diff,maxLenDiff)
                    islandnum = "Island: "+str(cacheJSON["BackupData"][name]["IslandNum"])
                    islandnum = ensureLength(islandnum,maxLenIsland)
                    score = "Score: "+str(cacheJSON["BackupData"][name]["Score"])
                    score = ensureLength(score,maxLenScore)
                    name = ensureLength(name,maxLenName)
                    folders[i] = name+" - "+time+diff+islandnum+score
            return folders
        except Exception as e:
            # import traceback
            # print(e)
            # traceback.print_exc()
            return ofold
            
def ensureLength(string,length):
    '''
    takes in a string and adds spaces to the end up it till it has the same length
    '''      
    while(len(string)<length):
        string +=" "
    return string    

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
    foldersInfo = getBackups(moreInfo=1)
    folders = getBackups()
    prompt = "Choose Backup to update with current save\n"
    options = "Go back to main menu"
    for i in range(len(foldersInfo)):
        options+="\n"+str(foldersInfo[i])
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

def updateScript():
    global isExe
    global owd
    perm = yornMenu("There is a newer version available\nWould you like to update to the latest version?")
    if(perm):
        if(isExe):
            downloadLatestURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.exe"
        else:
            downloadLatestURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.py"
        try:
            updaterURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManagerUpdater.exe"
            meow = False
            response = requests.get(downloadLatestURL)
            propath = os.path.join(owd,downloadLatestURL[downloadLatestURL.rindex("/")+1:])
            propath = propath.replace("CrabChampionSaveManager.exe","CrabChampionSaveManagerUpdated.exe")
            propath = propath.replace("\\","/")
            with open(propath, 'wb') as file:
                file.write(response.content)
            if(isExe):
                response = requests.get(updaterURL)
                propath = os.path.join(owd,updaterURL[updaterURL.rindex("/")+1:])
                with open(propath, 'wb') as file:
                    file.write(response.content)
                subprocess.Popen(["CrabChampionSaveManagerUpdater.exe"], shell=True)
                meow = True
        except:
            infoScreen("Could not download latest version\nThis program may be corrupted")
            time.sleep(2)
            exiting(1)
        if(meow):
            exiting(0)
        infoScreen("Latest Version succesfully downloaded\nRestart required for changes to take effect\npress any key to continue")
        exiting(0)
    else:
        return

def makeScreen():
    global screen
    screen = curses.initscr()
    curses.noecho()  # Don't display user input
    curses.cbreak()  # React to keys immediately without Enter
    screen.keypad(True)  # Enable special keys (e.g., arrow keys)

def scrollSelectMenu(prompt,options,win_height = -1,buffer_size = 1,wrapMode = 1,loop=False):
    global screen
    
    
    if(type(options) == type("")):
        options = options.split("\n")
    if(type(prompt) == type("")):
        prompt = prompt.split("\n")
    
    if(win_height == -1):
        autoSize = True
        win_height = 1000
    else:
        autoSize = False
    
        
    win_height = min(win_height,screen.getmaxyx()[0]-(3+len(prompt)))
    win_height = max(1,win_height)
    win_wid = screen.getmaxyx()[1]
    oBufSize = buffer_size
    
    buffer_size = min(buffer_size,win_height//2 - 1 + win_height % 2)
    buffer_size = max(buffer_size,0)
    
    selected_option = 0
    scroll_window = 0
    curstate = curses.curs_set(0)
    firstPass = False
    while True:
        screen.clear()
        win_wid = screen.getmaxyx()[1]
        # Display the main prompt
        for i, prom in enumerate(prompt):
            if(len(prom)>win_wid) and wrapMode == 2:
                prom = prom[:win_wid]
            screen.addstr(i, 0, prom)
        
        # Display the options
        for i, option in enumerate(options):
            
            if(i>=scroll_window and i <scroll_window+win_height):
                if i == selected_option:
                    # Highlight the selected option
                    if(len(option)+2>win_wid) and wrapMode == 2:
                        option = option[:win_wid]
                    screen.addstr((i + len(prompt) - scroll_window), 0, " > " + option, curses.A_BOLD)
                else:
                    if(len(option)+1>win_wid) and wrapMode == 2:
                        option = option[:win_wid]
                    screen.addstr((i + len(prompt) - scroll_window), 0, "  " + option)
        screen.addstr(min(win_height,len(options)) + len(prompt),0,"                                                                                                               ")
        screen.addstr(min(win_height,len(options)) + len(prompt)+1, 0, "Use arrow keys to navigate options. Press Enter to select.")
        screen.refresh()
        if(firstPass):
            key = screen.getch()
        else:
            key = -1
            firstPass = True
        
        if(autoSize):            
            win_height = screen.getmaxyx()[0]-(3+len(prompt))
            
            buffer_size = oBufSize
    
            buffer_size = min(buffer_size,win_height//2 - 1 + win_height % 2)
            buffer_size = max(buffer_size,0)
            
            
        
        

        if key == curses.KEY_UP and selected_option > 0:
            selected_option -= 1
        elif key == curses.KEY_DOWN and selected_option < len(options) - 1:
            selected_option += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            return selected_option
        elif(key == curses.KEY_UP and selected_option == 0 and loop):
            selected_option = len(options)-1
        elif(key == curses.KEY_DOWN and selected_option == len(options)-1 and loop):
            selected_option = 0
        #if the selected item goes out of the effective window then the scrolling window moves up or down to keep the selective item in the effective window, the effective window is in the center of the scrolling window and is scrolling_window_size-(buffer_size*2) = effective_window_size, and effective window size can not be smaller than 1 and not any larger than scrolling_window_size
        if(selected_option < scroll_window+buffer_size and scroll_window > 0):
            while(selected_option < scroll_window+buffer_size and scroll_window > 0):
                scroll_window-=1
        elif(selected_option > scroll_window+win_height-(1+buffer_size) and scroll_window < len(options)-win_height):
            while(selected_option > scroll_window+win_height-(1+buffer_size) and scroll_window < len(options)-win_height):
                scroll_window+=1
        if(scroll_window>len(options)-win_height):
            scroll_window = max(0,len(options)-win_height)

def scrollInfoMenu(info,window_height = -1,loop = False):
    global screen


    if(type(info) == type("")):
        info = info.split("\n")
    if(window_height == -1):
        autoSize = True
        window_height = 1000
    else:
        autoSize = False
    window_height = min(window_height,screen.getmaxyx()[0]-4)
    oinfo = info
    
    window_height = max(1,window_height)
    
    scroll_window = 0
    curstate = curses.curs_set(0)
    while True:
        screen.clear()
        if(autoSize):
            window_height = screen.getmaxyx()[0]-4
        win_width = screen.getmaxyx()[1]
        info = lengthLimit(oinfo,win_width)
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
    global owd
    defaultJSON = "{\"Start_Up\":{\"Terminal_Size\":{\"Height\":30,\"Width\":120}}}"
    configPath = owd+"/CrabChampionSaveManager/config.json"
    configPath = configPath.replace("\\","/")
    # Create the directory if it doesn't exist
    directory = os.path.dirname(configPath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file = open(configPath,"r+")
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
                            try:
                                prompt = f"Enter new height for terminal at start up (Currently at {TermHeight})\nIt is not recommend to go below 30"
                                configJSON["Start_Up"]["Terminal_Size"]["Height"] = userInputMenuNum(prompt,"Invaild number, number must be greater than or equal to 1",0)
                                saveSettings()
                            except:
                                None
                        elif(choice == 2):
                            try:
                                prompt = f"Enter new width for terminal at start up (Currently at {TermWidth})\nIt is not recommend to go below 120"
                                configJSON["Start_Up"]["Terminal_Size"]["Width"] = userInputMenuNum(prompt,"Invaild number, number must be greater than or equal to 1",0)
                                saveSettings()
                            except:
                                None
                        elif(choice == 3):
                            screen.nodelay(True)
                            curstate = curses.curs_set(0)
                            while(True):
                                time.sleep(.05) # limits loop speed , should fix terminal flickering noticed on linux
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
    global owd
    global TermWidth
    defaultJSON = "{\"Start_Up\":{\"Terminal_Size\":{\"Height\":30,\"Width\":120}}}"
    configPath = owd+"/CrabChampionSaveManager/config.json"
    
    configPath = configPath.replace("\\","/")
    # Create the directory if it doesn't exist
    directory = os.path.dirname(configPath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # while(not os.path.exists(directory)):
    #     time.sleep(.1)
    
    try:
        file = open(configPath,"r+")
    except:
        file = open(configPath,"w")
        file.close()
        file = open(configPath,"r+")
    try:
        configJSON = json.loads(file.read())
    except Exception as e:
        configJSON = json.loads(defaultJSON)
        
    try:
        TermHeight = configJSON["Start_Up"]["Terminal_Size"]["Height"]
        TermHeight = max(TermHeight,1)
    except:
        configJSON["Start_Up"]["Terminal_Size"]["Height"] = 30
        TermHeight = 30
        
    try:
        TermWidth = configJSON["Start_Up"]["Terminal_Size"]["Width"]
        TermWidth = max(TermWidth,1)
    except:
        configJSON["Start_Up"]["Terminal_Size"]["Width"] = 120  
        TermWidth = 120
    file.seek(0)
    file.write(json.dumps(configJSON,indent=4))
    file.truncate()
    file.close()

def saveSettings():
    global owd
    configPath = owd+"/CrabChampionSaveManager/config.json"
    configPath = configPath.replace("\\","/")
    global configJSON
    directory = os.path.dirname(configPath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file = open(configPath,"w")
    file.write(json.dumps(configJSON,indent=4))

def getChecksum(file_path):
    # Get the absolute path of the file
    absolute_path = os.path.abspath(file_path)
    absolute_path = absolute_path.replace("\\","/")
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
    global Version
    global owd
    lock = threading.Lock()
    global cacheJSON
    backups = getBackups()
    cachePath = owd+"/CrabChampionSaveManager/backupDataCache.json"
    cachePath = cachePath.replace("\\","/")
    # Create the directory if it doesn't exist
    directory = os.path.dirname(cachePath)
    noCache = False
    if not os.path.exists(directory):
        os.makedirs(directory)
        noCache = True
    # while(not os.path.exists(directory)):
    #     time.sleep(.1)
    
    try:
        file = open(cachePath,"r+")
    except:
        file = open(cachePath,"w")
        file.close()
        noCache = True
        file = open(cachePath,"r+")
    try:
        cacheJSON = json.loads(file.read())
    except:
        cacheJSON = json.loads("{}")
        noCache = True
    if(noCache):
        cacheJSON["BackupData"] = {}
    threads = []
    for backup in backups:
        currentCS = getChecksum(backup+"/SaveSlot.sav")
        try:
            cacheCS = cacheJSON["BackupData"][backup]["CheckSum"]
        except:
            cacheCS = ""
        try:
            cacheVersion = cacheJSON["BackupData"][backup]["Version"]
        except:
            cacheVersion = "0.0.0"
        if(currentCS != cacheCS or versionToValue(cacheVersion) < versionToValue(Version)):
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
    start = time.time()
    global lock
    global Version
    global cacheJSON
    savFilePath = ""+backupName+"/SaveSlot.sav"
    savFile = savFilePath
    #print(savFile)
    #print(savFile.replace("SaveSlot.sav","data.json"))
    uesavePath = getUesavePath()
    savFile = savFile.replace("\\","/")
    proc = subprocess.Popen(uesavePath+" to-json -i \""+savFile+"\" -o \""+savFile.replace("SaveSlot.sav","data.json")+"\"", shell=True)
    proc.wait()
    start3 = time.time()
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
        cacheJSON["BackupData"][backupName]["Version"] = Version
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
    # stat elmins              ["Eliminations"]["Int"]["value"]
    # stat shots fired         ["ShotsFired"]["Int"]["value"]
    # stat damage dealt        ["DamageDealt"]["Int"]["value"]
    # stat highest dmg delt    ["HighestDamageDealt"]["Int"]["value"]
    # stat damage Taken        ["DamageTaken"]["Int"]["value"]
    # stat flawless islands    ["NumFlawlessIslands"]["Int"]["value"]
    # stat Items Salvaged      ["NumTimesSalvaged"]["Int"]["value"]
    # stat Items Purchased     ["NumShopPurchases"]["Int"]["value"]
    # stat Shop Rerolls        ["NumShopRerolls"]["Int"]["value"]
    # stat Totems Destroyed    ["NumTotemsDestroyed"]["Int"]["value"]
    # Crystals                 ["Crystals"]["UInt32"]["value"]
    # Biome                    ["NextIslandInfo"]["Struct"]["value"]["Struct"]["Biome"]["Enum"]["value"]
    # Loot Type                ["NextIslandInfo"]["Struct"]["value"]["Struct"]["RewardLootPool"]["Enum"]["value"]
    
    #Weapon                    ["WeaponDA"]["Object"]["value"]  -  use parseWeapon() to get proper name
    
    #Items
    #Weapon Mod Slots           ["NumWeaponModSlots"]["Byte"]["value"]["Byte"]
    #Weapon Mod Array           ["WeaponMods"]["Array"]["value"]["Struct"]["value"]
    #Weapon Mod in array item   ["Struct"]["WeaponModDA"]["Object"]["value"] - use parseWeaponMod() to get parsed and formated name 
    #Weapon Mod in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]
    
    #Gernade Mod Slots           ["NumGrenadeModSlots"]["Byte"]["value"]["Byte"]
    #Gernade Mod Array           ["GrenadeMods"]["Array"]["value"]["Struct"]["value"]
    #Gernade Mod in array item   ["Struct"]["GrenadeModDA"]["Object"]["value"] - use parseGernadeMod() to get parsed and formated name 
    #Gernade Mod in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]

    #Perk Slots           ["NumPerkSlots"]["Byte"]["value"]["Byte"]
    #Perk Array           ["Perks"]["Array"]["value"]["Struct"]["value"]
    #Perk in array item   ["Struct"]["PerkDA"]["Object"]["value"] - use parsePerk() to get parsed and formated name 
    #Perk in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]
    
    
    
    #for the config json
    #run time seconds        - ["BackupData"][BackupName]["RunTime"]
    #score                   - ["BackupData"][BackupName]["Score"]
    #difficulty              - ["BackupData"][BackupName]["Diff"]
    #island num              - ["BackupData"][BackupName]["IslandNum"]
    #diff mods               - ["BackupData"][BackupName]["DiffMods"]
    #checksum                - ["BackupData"][BackupName]["CheckSum"]
    #nosave,if it has a save - ["BackupData"][BackupName]["NoSave"]
    #Version                 - ["BackupData"][BackupName]["Version"]
    #Stats                   - ["BackupData"][BackupName]["Stats"]
    #Eliminations            - ["BackupData"][BackupName]["Stats"]["Elimns"]
    #Shots Fired             - ["BackupData"][BackupName]["Stats"]["ShotsFired"]
    #Damage Dealt            - ["BackupData"][BackupName]["Stats"]["DmgDealt"]
    #Most Damage Dealt       - ["BackupData"][BackupName]["Stats"]["MostDmgDealt"]
    #Damage Taken            - ["BackupData"][BackupName]["Stats"]["DmgTaken"]
    #Flawless Islands        - ["BackupData"][BackupName]["Stats"]["FlawlessIslands"]
    #Items Salvaged          - ["BackupData"][BackupName]["Stats"]["ItemsSalvaged"]
    #Items Purchased         - ["BackupData"][BackupName]["Stats"]["ItemsPurchased"]
    #Shop Rerolls            - ["BackupData"][BackupName]["Stats"]["ShopRerolls"]
    #Totems Destroyed        - ["BackupData"][BackupName]["Stats"]["TotemsDestroyed"]
    #Current Biome           - ["BackupData"][BackupName]["Biome"]
    #Current Loot Type       - ["BackupData"][BackupName]["LootType"]
    
    #Inventory               - [backupName]["Inventory"]
    #Weapon                  - [backupName]["Inventory"]["Weapon"]
    
    #Weapon Mod Slots        - [backupName]["Inventory"]["WeaponMods"]["Slots"]
    #Weapon Mods             - [backupName]["Inventory"]["WeaponMods"]["Mods"]
    #Weapon Mod Name         - [backupName]["Inventory"]["WeaponMods"]["Mods"][index of WMod]["Name"]
    #Weapon Mod Rarity       - [backupName]["Inventory"]["WeaponMods"]["Mods"][index of WMod]["Rarity"]
    #Weapon Mod Level        - [backupName]["Inventory"]["WeaponMods"]["Mods"][index of WMod]["Level"]
    
    #Gernade Mod Slots       - [backupName]["Inventory"]["GernadeMods"]["Slots"]
    #Gernade Mods            - [backupName]["Inventory"]["GernadeMods"]["Mods"]
    #Gernade Mod Name        - [backupName]["Inventory"]["GernadeMods"]["Mods"][index of WMod]["Name"]
    #Gernade Mod Rarity      - [backupName]["Inventory"]["GernadeMods"]["Mods"][index of WMod]["Rarity"]
    #Gernade Mod Level       - [backupName]["Inventory"]["GernadeMods"]["Mods"][index of WMod]["Level"]
    
    #Perk Slots              - [backupName]["Inventory"]["Perks"]["Slots"]
    #Perks                   - [backupName]["Inventory"]["Perks"]["Perks"]
    #Perk Name               - [backupName]["Inventory"]["Perks"]["Perks"][index of WMod]["Name"]
    #Perk Rarity             - [backupName]["Inventory"]["Perks"]["Perks"][index of WMod]["Rarity"]
    #Perk Level              - [backupName]["Inventory"]["Perks"]["Perks"][index of WMod]["Level"]
    
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
    backupJSON[backupName]["Stats"] = {}
    backupJSON[backupName]["Stats"]["Elimns"] = saveJSON["Eliminations"]["Int"]["value"]
    backupJSON[backupName]["Stats"]["ShotsFired"] = saveJSON["ShotsFired"]["Int"]["value"]
    backupJSON[backupName]["Stats"]["DmgDealt"] = saveJSON["DamageDealt"]["Int"]["value"]
    backupJSON[backupName]["Stats"]["MostDmgDealt"] = saveJSON["HighestDamageDealt"]["Int"]["value"]
    backupJSON[backupName]["Stats"]["DmgTaken"] = saveJSON["DamageTaken"]["Int"]["value"]
    backupJSON[backupName]["Stats"]["FlawlessIslands"] = saveJSON["NumFlawlessIslands"]["Int"]["value"]
    
    try:
        backupJSON[backupName]["Stats"]["ItemsSalvaged"] = saveJSON["NumTimesSalvaged"]["Int"]["value"]
    except:
        backupJSON[backupName]["Stats"]["ItemsSalvaged"] = 0
    try:
        backupJSON[backupName]["Stats"]["ItemsPurchased"] = saveJSON["NumShopPurchases"]["Int"]["value"]
    except:
        backupJSON[backupName]["Stats"]["ItemsPurchased"] = 0
    try:
        backupJSON[backupName]["Stats"]["ShopRerolls"] = saveJSON["NumShopRerolls"]["Int"]["value"]
    except:
        backupJSON[backupName]["Stats"]["ShopRerolls"] = 0
    try:
        backupJSON[backupName]["Stats"]["TotemsDestroyed"] = saveJSON["NumTotemsDestroyed"]["Int"]["value"]
    except:
        backupJSON[backupName]["Stats"]["TotemsDestroyed"] = 0
    
    
    backupJSON[backupName]["Crystals"] = saveJSON["Crystals"]["UInt32"]["value"]
    
    diff = saveJSON["NextIslandInfo"]["Struct"]["value"]["Struct"]["Biome"]["Enum"]["value"]
    diff = diff[diff.index("::")+2:]
    backupJSON[backupName]["Biome"] = diff
    
    try:
        diff = saveJSON["NextIslandInfo"]["Struct"]["value"]["Struct"]["RewardLootPool"]["Enum"]["value"]
        diff = diff[diff.index("::")+2:]
    except:
        diff = "NewBiome"    
    backupJSON[backupName]["LootType"] = diff
    
    backupJSON[backupName]["Inventory"] = {}
    backupJSON[backupName]["Inventory"]["Weapon"] = parseWeapon(saveJSON["WeaponDA"]["Object"]["value"])
    
    backupJSON[backupName]["Inventory"]["WeaponMods"] = {}
    backupJSON[backupName]["Inventory"]["WeaponMods"]["Slots"] = saveJSON["NumWeaponModSlots"]["Byte"]["value"]["Byte"]
    backupJSON[backupName]["Inventory"]["WeaponMods"]["Mods"] = {}
    try:
        WeaponMods = saveJSON["WeaponMods"]["Array"]["value"]["Struct"]["value"]
        WeaponModArray = []
        while(len(WeaponModArray)<len(WeaponMods)):
            WeaponModArray.append("")
        for i,name in enumerate(WeaponMods):
            WeaponModArray[i] = json.loads("{}")
            WeaponModArray[i]["Name"] = parseWeaponMod(name["Struct"]["WeaponModDA"]["Object"]["value"])[0]
            WeaponModArray[i]["Rarity"] = parseWeaponMod(name["Struct"]["WeaponModDA"]["Object"]["value"])[1]
            WeaponModArray[i]["Level"] = name["Struct"]["Level"]["Byte"]["value"]["Byte"]
        backupJSON[backupName]["Inventory"]["WeaponMods"]["Mods"] = WeaponModArray
    except:
        backupJSON[backupName]["Inventory"]["WeaponMods"]["Mods"] = []
    
    
    backupJSON[backupName]["Inventory"]["GernadeMods"] = {}
    backupJSON[backupName]["Inventory"]["GernadeMods"]["Slots"] = saveJSON["NumGrenadeModSlots"]["Byte"]["value"]["Byte"]
    backupJSON[backupName]["Inventory"]["GernadeMods"]["Mods"] = {}
    try:
        GernadeMods = saveJSON["GrenadeMods"]["Array"]["value"]["Struct"]["value"]
        GernadeModArray = []
        while(len(GernadeModArray)<len(GernadeMods)):
            GernadeModArray.append("")
        for i,name in enumerate(GernadeMods):
            GernadeModArray[i] = json.loads("{}")
            GernadeModArray[i]["Name"] = parseGernadeMod(name["Struct"]["GrenadeModDA"]["Object"]["value"])[0]
            GernadeModArray[i]["Rarity"] = parseGernadeMod(name["Struct"]["GrenadeModDA"]["Object"]["value"])[1]
            GernadeModArray[i]["Level"] = name["Struct"]["Level"]["Byte"]["value"]["Byte"]
        backupJSON[backupName]["Inventory"]["GernadeMods"]["Mods"] = GernadeModArray
    except:
        backupJSON[backupName]["Inventory"]["GernadeMods"]["Mods"] = []
    
    
    backupJSON[backupName]["Inventory"]["Perks"] = {}
    backupJSON[backupName]["Inventory"]["Perks"]["Slots"] = saveJSON["NumPerkSlots"]["Byte"]["value"]["Byte"]
    backupJSON[backupName]["Inventory"]["Perks"]["Perks"] = {}
    try:
        WeaponMods = saveJSON["Perks"]["Array"]["value"]["Struct"]["value"]
        PerkArray = []
        while(len(PerkArray)<len(WeaponMods)):
            PerkArray.append("")
        for i,name in enumerate(WeaponMods):
            PerkArray[i] = json.loads("{}")
            PerkArray[i]["Name"] = parsePerk(name["Struct"]["PerkDA"]["Object"]["value"])[0]
            PerkArray[i]["Rarity"] = parsePerk(name["Struct"]["PerkDA"]["Object"]["value"])[1]
            PerkArray[i]["Level"] = name["Struct"]["Level"]["Byte"]["value"]["Byte"]
        backupJSON[backupName]["Inventory"]["Perks"]["Perks"] = PerkArray
    except:
        backupJSON[backupName]["Inventory"]["Perks"]["Perks"] = []
    
    
    backupJSON[backupName]["CheckSum"] = getChecksum(backupName+"/SaveSlot.sav")
    backupJSON[backupName]["NoSave"] = False
    backupJSON[backupName]["Version"] = Version
    lock.acquire()
    
    try:
        cacheJSON["BackupData"][backupName] = backupJSON[backupName]
    except:
        cacheJSON["BackupData"] = {}
        cacheJSON["BackupData"][backupName] = backupJSON[backupName]
    lock.release()
    stop = time.time()
    #print(backupName+str("  -  ")+str(round(stop-start,2))+str("  -add  ")+str(round(stop-start3,2)))

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
    
def getUesavePath():
    global isExe
    global isLinux
    global owd
    programDir = owd
    programDir = programDir.replace("\\","/")
    if(isLinux):
        uesavePath = programDir+"/uesave"
        if(os.path.exists(uesavePath)):
            return "\""+str(uesavePath)+"\""
    elif(isExe):
        return "\""+os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uesave.exe')+"\""
    else:
        uesavePath = programDir+"/uesave.exe"
        uesavePath = uesavePath.replace("\\","/")
        if(os.path.exists(uesavePath)):
            return "\""+str(uesavePath)+"\""
        
    
    
    if(isLinux):
        uesaveDownloadlink = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/uesave"
        uesave = "uesave"
    else:
        uesaveDownloadlink = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/uesave.exe"
        uesave = "uesave.exe"
    perm = yornMenu("uesave could not be found, permission to download?")
    
    if(perm):
        infoScreen("Downloading uesave\nThis might take a few min\nGoing to main menu when done")
        response = requests.get(uesaveDownloadlink)
        with open(programDir+"/"+uesave, 'wb') as file:
            file.write(response.content)
        return getUesavePath()
    else:
        return ""
    
def lengthLimit(dict , wid):
    None
    if(type(dict) == type("")):
        if(len(dict)<wid):
            return dict
        for i in range(wid,0,-1):
            try:
                if(dict.index(" ",i)<= wid):
                    space = dict.index(" ",i)
                    return [dict[:space],dict[space+1:]]
            except:
                None
        return dict
    else:
        di = []
        for d in dict:
            d = lengthLimit(d,wid)
            if(type(d) == type("")):
                di.append(d)
            else:
                for ad in d:
                    di.append(ad)
        return di

def parseWeapon(name):
    name = name[name.rindex(".DA_Weapon_")+11:]
    return spaceBeforeUpper(name)

def parseWeaponMod(name):
    rarity = name[name.index("Mod/")+4:name.index("/",name.index("Mod/")+4)]
    name = name[name.rindex(".DA_WeaponMod_")+14:]
    return [spaceBeforeUpper(name) , rarity]

def parseGernadeMod(name):
    rarity = name[name.index("Mod/")+4:name.index("/",name.index("Mod/")+4)]
    name =  name[name.rindex(".DA_GrenadeMod_")+15:]
    return [spaceBeforeUpper(name) , rarity]

def parsePerk(name):
    rarity = name[name.index("Perk/")+5:name.index("/",name.index("Perk/")+5)]
    name =  name[name.rindex(".DA_Perk_")+9:]
    return [spaceBeforeUpper(name) , rarity]
   
global owd
owd = os.getcwd()

# os.remove("CrabChampionSaveManager/backupDataCache.json")
# time.sleep(1)

makeScreen()
loadSettings()

infoScreen("Starting Crab Champion Save Manager\nThis may take a few seconds")

uepath = getUesavePath()
if(uepath == ""):
    scrollInfoMenu("This script uses uesave a lot,it is highly reccomended to download it\nyou can still use this program but i can not guarantee that it will fully work\nPress Enter to continue")
else:
    start = time.time()
    loadCache()
    stop = time.time()
# print(round(stop-start,2))
# exiting(0)

curses.resize_term(TermHeight,TermWidth)  
            
# 30 x 120
    
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
    updateScript()
elif(VersionValue > LatestValue):
    mainMenuPrompt += "\n\nooohh , you have a version that isn't released yet, nice"
else:
    mainMenuPrompt += "\n\nYou have the latest version"



            
if(currentDirCheck()):
    try:
        if(isLinux):
            new_dir = os.path.expandvars("$HOME/.steam/steam/steamapps/compatdata/774801/pfx/drive_c/users/steamuser/AppData/Local/CrabChampions/Saved")
        else:
            new_dir = os.path.expandvars("%APPDATA%\\..\\Local\\CrabChampions\\Saved")
        os.chdir(new_dir)
    except:
        infoScreen("Could not find save game directory\nYou either don't have Crab Champions installed\n or you have it installed in a different spot than the default\n if it is installed in a different spot than the defualt then put this file in the equivalent of CrabChampions\Saved\nPress any key to continue . . .")
        screen.getch()
        exiting(0)



#time.sleep(20)
mainMenuPrompt += "\n\nWelcome to Crab Champion Save Manager"
mainMenuPrompt += "\nMade By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager\nWhat do you want to do\n"
while(True):
    options = "Edit save game\nBackup Save\nUpdate backup\nRestore Save from backup (Warning : Deletes current save)\nDelete backup\nList Backups\nInfo/How to use\nSettings\nExit"
    choice = scrollSelectMenu(mainMenuPrompt,options,-1,1,loop=True)+1
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
        infoList = """
Crab Champion Save Manager
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

 \nSettings:
    - Change program settings

 \nExit:
    - Exits the program.

 This script uses uesave from https://github.com/trumank/uesave-rs, all credit for this goes to trumank,their program is in my opinion very well made and works very well
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
