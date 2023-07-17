import copy
import hashlib
import os
import random
import shutil
import time
import subprocess
import platform
import sys
import json
from os import path
import threading
import re


global isExe
global isLinux
global Version
isExe = False
isLinux = False

Version = "3.2.1"

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

def isValidPresetName(name):
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                      'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3',
                      'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    # Check for invalid characters
    if re.search(invalid_chars, name):
        return False
    
    # Check for reserved names
    if name.upper() in reserved_names:
        return False
    
    # Check for other conditions (if any) that make the name invalid
    
    # If none of the above conditions match, the name is valid
    return True

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

def backupNameMenu(prompt,escape = None,name = "",escapeReturn = None):
    global screen

    if(type(prompt) == type("")):
        prompt = prompt.split("\n")

    curstate = curses.curs_set(1)
    folder_name = name
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
            if(folder_name == escape):
                return escapeReturn
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
        saveName = backupNameMenu("Enter nothing to go back to the main menu\nEnter backup name",escape="",escapeReturn="")
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
    choice = scrollSelectMenu(prompt,options,-1,1,detailsSelected=False)
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

def editBackupRaw():
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
    choice = scrollSelectMenu(prompt,options,-1,1,detailsSelected=False)
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
    #time.sleep(10)
    
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
    choice = scrollSelectMenu(prompt,options,-1,1,detailsSelected=False)
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
    foldersInfo = getBackups(moreInfo=1,currentSave=True)
    folders = getBackups(currentSave=True)
    prompt = str(len(folders))+" Backups Stored\nSelect Backup for more info about that backup\n"
    backups = "Go back to main menu\n"
    for i,name in enumerate(foldersInfo):
        if(i == 0):
            backups += str(name)
        else:
            backups += "\n"+str(name)
            
    choice = scrollSelectMenu(prompt,backups,wrapMode=2,detailsSelected = False)
    if(choice == 0):
        return
    choice -=1
    backupDetailsScreen(folders[choice])
    listBackups()

def getBackups(moreInfo = 0,currentSave = False):
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
    if(currentSave):
        folders.insert(0,"Current Save")
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
    return str(string)    

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
    choice = scrollSelectMenu(prompt,options,-1,1,detailsSelected=False)
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
        infoScreen("Updating CCSM\nThis may take a few minutes\n1/3")
        print("\nUpdating CCSM\nThis may take a few minutes\n2/3")
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
                os.chdir(owd)
                subprocess.Popen(["CrabChampionSaveManagerUpdater.exe"], shell=True)
                meow = True
        except:
            infoScreen("Could not download latest version\nThis program may be corrupted")
            time.sleep(2)
            exiting(1)
        if(meow):
            exiting(0)
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
    try:
        curses.start_color()
        curses.use_default_colors()
    except:
        None

def scrollSelectMenu(prompt,options,win_height = -1,buffer_size = 1,wrapMode = 1,loop=False,detailsSelected = True,skip=[],startChoice = 0,returnMore = False,scrollWindowStart = 0,useItemColors = False,checkForRarityColor = False):
    global screen
    
    try:
        curses.init_pair(1, RARECOLOR, -1)
        curses.init_pair(2, EPICCOLOR, -1)
        curses.init_pair(3, LEGENDARYCOLOR, -1)
        curses.init_pair(4, GREEDCOLOR, -1)
        colors = "ItemRarityColor"
    except:
        colors = "None"
    
    def moreDeatils(opt,details=False):
        optio = ""
        detail = ""
        try: 
           optio = opt[:opt.index("-")]
           detail = opt[opt.index("-")+1:]
        except:
            optio = opt
            detail = ""
            details = False
        if(details):
            return str(optio)+" - "+str(detail)
        else:
            return str(optio)
    
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
    
    selected_option = startChoice
    scroll_window = scrollWindowStart
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
                    if(detailsSelected):
                        if(useItemColors):
                            op = option.replace("  ","")
                            try:
                                rar = WEAPONMODS[op]
                            except:
                                rar = ""
                            if(rar == ""):
                                try:
                                    rar = GRENADEMODS[op]
                                except:
                                    rar = ""  
                            if(rar == ""):
                                try:
                                    rar = PERKS[op]
                                except:
                                    rar = "" 
                            if("Rare" in rar):
                                rarColor = curses.color_pair(1)
                                screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor)
                            elif("Epic" in rar):
                                rarColor = curses.color_pair(2)
                                screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor)
                            elif("Legendary" in rar):
                                rarColor = curses.color_pair(3)
                                screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor)   
                            elif("Greed" in rar):
                                rarColor = curses.color_pair(4)
                                screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor) 
                            else:
                                if(checkForRarityColor):
                                    if("Rare" in option):
                                        rarColor = curses.color_pair(1)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor)
                                    elif("Epic" in option):
                                        rarColor = curses.color_pair(2)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor)
                                    elif("Legendary" in option):
                                        rarColor = curses.color_pair(3)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor)   
                                    elif("Greed" in option):
                                        rarColor = curses.color_pair(4)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),rarColor) 
                                    else:
                                        screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),curses.A_BOLD)
                                else:
                                    screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True),curses.A_BOLD)
                        else:
                            screen.addstr((i + len(prompt) - scroll_window), 0, " > " + moreDeatils(option,details=True), curses.A_BOLD)
                    else:
                        
                        screen.addstr((i + len(prompt) - scroll_window), 0, " > " + option, curses.A_BOLD)
                else:
                    if(len(option)+1>win_wid) and wrapMode == 2:
                        option = option[:win_wid]
                    if(detailsSelected):
                        if(useItemColors):
                            op = option.replace("  ","")
                            try:
                                rar = WEAPONMODS[op]
                            except:
                                rar = ""
                            if(rar == ""):
                                try:
                                    rar = GRENADEMODS[op]
                                except:
                                    rar = ""  
                            if(rar == ""):
                                try:
                                    rar = PERKS[op]
                                except:
                                    rar = "" 
                            if("Rare" in rar):
                                rarColor = curses.color_pair(1)
                                screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                            elif("Epic" in rar):
                                rarColor = curses.color_pair(2)
                                screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                            elif("Legendary" in rar):
                                rarColor = curses.color_pair(3)
                                screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                            elif("Greed" in rar):
                                rarColor = curses.color_pair(4)
                                screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                            else:
                                if(checkForRarityColor):
                                    if("Rare" in option):
                                        rarColor = curses.color_pair(1)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                                    elif("Epic" in option):
                                        rarColor = curses.color_pair(2)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                                    elif("Legendary" in option):
                                        rarColor = curses.color_pair(3)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                                    elif("Greed" in option):
                                        rarColor = curses.color_pair(4)
                                        screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option),rarColor)
                                    else:
                                        screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option))
                                else:
                                    screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option))
                        else:
                            screen.addstr((i + len(prompt) - scroll_window), 0, "  " + moreDeatils(option))
                    else:
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
            while(options[selected_option] in skip):
                if(selected_option-1>0):
                    selected_option-=1
                else:
                    selected_option+=1
        elif key == curses.KEY_DOWN and selected_option < len(options) - 1:
            selected_option += 1
            while(options[selected_option] in skip):
                if((selected_option)< (len(options) - 1)):
                    selected_option+=1
                    
                else:
                    selected_option-=1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            if(returnMore):
                return selected_option , scroll_window
            else:
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

def scrollInfoMenu(info,window_height = -1,loop = False,instructions = "Use arrow keys to scroll up and down. Press Enter to go back to main menu.",itemRarityColors = False):
    global screen
    try:
        curses.init_pair(1, RARECOLOR, -1)
        curses.init_pair(2, EPICCOLOR, -1)
        curses.init_pair(3, LEGENDARYCOLOR, -1)
        curses.init_pair(4, GREEDCOLOR, -1)
        colors = "ItemRarityColor"
    except:
        colors = "None"

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
                if(itemRarityColors):
                    if("Rare" in inf):
                        rarColor = curses.color_pair(1)
                        screen.addstr((i - scroll_window)+1, 0, str(inf),rarColor)  
                    elif("Epic" in inf):
                        rarColor = curses.color_pair(2)
                        screen.addstr((i - scroll_window)+1, 0, str(inf),rarColor)  
                    elif("Legendary" in inf):
                        rarColor = curses.color_pair(3)
                        screen.addstr((i - scroll_window)+1, 0, str(inf),rarColor)   
                    elif("Greed" in inf):
                        rarColor = curses.color_pair(4)
                        screen.addstr((i - scroll_window)+1, 0, str(inf),rarColor)  
                    else:
                        screen.addstr((i - scroll_window)+1, 0, str(inf))   
                else:
                    screen.addstr((i - scroll_window)+1, 0, str(inf))
        
        screen.addstr(window_height +2, 0, instructions)
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
        else:
            None
            
def infoScreen(info):
    curstate = curses.curs_set(0)
    screen.clear()
    screen.addstr(1,0,info)
    screen.refresh()
    curses.curs_set(curstate)

def userInputMenuNum(prompt,escape = None,lowLimit = -2000000000,highLimit = 2000000000,default = None,useDefaultAsPreset = False,decimal = False):
    global screen

    if(type(prompt) == type("")):
        prompt = prompt.split("\n")

    curstate = curses.curs_set(1)
    num = ""
    if(useDefaultAsPreset):
        num = str(default)
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
            try:
                if(decimal):
                    if (float(num)<highLimit and float(num)>lowLimit):
                        return float(num)
                    elif(float(num) == escape):
                        return default
                else:
                    if (int(num)<highLimit and int(num)>lowLimit):
                        return int(num)
                    elif(int(num) == escape):
                        return default
            except:
                if(num == escape):
                    return default
        else:
            if(key in range(48,58) or (key == 46 and decimal)):
                if(not "." in num):
                    num += chr(key)
                elif(key != 46):
                    num += chr(key)
        try:
            if(decimal):
                numint = float(num)
                if(not numint>lowLimit):
                    num = float(lowLimit+1)
                elif(not numint<highLimit):
                    num = float(highLimit-1)
            else:
                numint = int(num)
                if(not numint>lowLimit):
                    num = str(lowLimit+1)
                elif(not numint<highLimit):
                    num = str(highLimit-1)
        except:
            None
 
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
                        choice = scrollSelectMenu(promptTS,optionsTS,detailsSelected=False)
                        if(choice == 0):
                            break
                        elif(choice == 1):
                            try:
                                prompt = f"Enter 0 to use current height\nEnter new height for terminal at start up (Currently at {TermHeight})\nIt is not recommend to go below 30"
                                configJSON["Start_Up"]["Terminal_Size"]["Height"] = userInputMenuNum(prompt,escape=0,lowLimit=-1,default=TermHeight)
                                saveSettings()
                            except:
                                None
                        elif(choice == 2):
                            try:
                                prompt = f"Enter 0 to use current width\nEnter new width for terminal at start up (Currently at {TermWidth})\nIt is not recommend to go below 120"
                                configJSON["Start_Up"]["Terminal_Size"]["Width"] = userInputMenuNum(prompt,escape=0,lowLimit=-1,defailt = TermWidth)
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
    infoScreen("Loading Cache\nThis might take a few seconds")
    global cacheLock
    global Version
    global owd
    cacheLock = threading.Lock()
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
        cacheJSON["PlayerData"] = {}
    threads = []
    try:
        cacheVersion = cacheJSON["Version"]
    except:
        cacheJSON["Version"] = Version
        cacheVersion = "0.0.0"
    for backup in backups:
        currentCS = getChecksum(backup+"/SaveSlot.sav")
        try:
            cacheCS = cacheJSON["BackupData"][backup]["CheckSum"]
        except:
            cacheCS = ""
        if(currentCS != cacheCS or versionToValue(cacheVersion) < versionToValue(Version)):
            t = threading.Thread(target=genBackupData, args=(backup,))
            t.start()
            threads.append(t)
    CurrentSaveCS = getChecksum(os.getcwd().replace("\\","/")+"/SaveGames/SaveSlot.sav")
    try:
        CurrentSaveCacheCS = cacheJSON["BackupData"]["Current Save"]["CheckSum"]
    except:
        CurrentSaveCacheCS = ""
    if(CurrentSaveCS != CurrentSaveCacheCS):
        t = threading.Thread(target=genBackupData, args=("SaveGames",))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    file.seek(0)
    file.truncate()
    file.write(json.dumps(cacheJSON,indent=4))
        
def spaceBeforeUpper(string):
    if string == "FMJ":
        return string
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
    global cacheLock
    global cacheJSON
    savFilePath = ""+backupName+"/SaveSlot.sav"
    savFile = savFilePath
    #print(savFile)
    #print(savFile.replace("SaveSlot.sav","data.json"))
    uesavePath = getUesavePath()
    savFile = savFile.replace("\\","/")
    ueStart = time.time()
    proc = subprocess.Popen(uesavePath+" to-json -i \""+savFile+"\" -o \""+savFile.replace("SaveSlot.sav","data.json")+"\"", shell=True)
    proc.wait()
    ueStop = time.time()
    start3 = time.time()
    saveFile = open(savFile.replace("SaveSlot.sav","data.json"),"r")
    saveJSON = json.loads(saveFile.read())
    saveFile.close()
    os.remove(savFile.replace("SaveSlot.sav","data.json"))
    checksum = getChecksum(backupName+"/SaveSlot.sav")
    if(backupName == "SaveGames"):
        backupName = "Current Save"
        genPlayerData(saveJSON,checksum)
    try:
        saveJSON = saveJSON["root"]["properties"]["AutoSave"]["Struct"]["value"]["Struct"]
    except:
        cacheLock.acquire()
        cacheJSON["BackupData"][backupName] = {}
        cacheJSON["BackupData"][backupName]["CheckSum"] = checksum
        cacheJSON["BackupData"][backupName]["NoSave"] = True
        cacheLock.release()
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
    # island name              ["NextIslandInfo"]["Struct"]["value"]["Struct"]["IslandName"]["Name"]["value"]
    # island type              ["NextIslandInfo"]["Struct"]["value"]["Struct"]["IslandType"]["Name"]["value"]
    # Health                   ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentHealth"]["Float"]["value"]
    # Max Health               ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentMaxHealth"]["Float"]["value"]
    # Armor Plates             ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlates"]["Int"]["value"]
    # Armor Plate Health       ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlateHealth"]["Float"]["value"]
    
    #Weapon                    ["WeaponDA"]["Object"]["value"]  -  use parseWeapon() to get proper name
    
    #Items
    #Weapon Mod Slots           ["NumWeaponModSlots"]["Byte"]["value"]["Byte"]
    #Weapon Mod Array           ["WeaponMods"]["Array"]["value"]["Struct"]["value"]
    #Weapon Mod in array item   ["Struct"]["WeaponModDA"]["Object"]["value"] - use parseWeaponMod() to get parsed and formated name 
    #Weapon Mod in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]
    
    #Grenade Mod Slots           ["NumGrenadeModSlots"]["Byte"]["value"]["Byte"]
    #Grenade Mod Array           ["GrenadeMods"]["Array"]["value"]["Struct"]["value"]
    #Grenade Mod in array item   ["Struct"]["GrenadeModDA"]["Object"]["value"] - use parseGrenadeMod() to get parsed and formated name 
    #Grenade Mod in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]

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
    #Eliminations            - ["BackupData"][BackupName]["Elimns"]
    #Shots Fired             - ["BackupData"][BackupName]["ShotsFired"]
    #Damage Dealt            - ["BackupData"][BackupName]["DmgDealt"]
    #Most Damage Dealt       - ["BackupData"][BackupName]["MostDmgDealt"]
    #Damage Taken            - ["BackupData"][BackupName]["DmgTaken"]
    #Flawless Islands        - ["BackupData"][BackupName]["FlawlessIslands"]
    #Items Salvaged          - ["BackupData"][BackupName]["ItemsSalvaged"]
    #Items Purchased         - ["BackupData"][BackupName]["ItemsPurchased"]
    #Shop Rerolls            - ["BackupData"][BackupName]["ShopRerolls"]
    #Totems Destroyed        - ["BackupData"][BackupName]["TotemsDestroyed"]
    #Current Biome           - ["BackupData"][BackupName]["Biome"]
    #Current Loot Type       - ["BackupData"][BackupName]["LootType"]
    #island name             - ["BackupData"][BackupName]["IslandName"]
    #island type             - ["BackupData"][BackupName]["IslandType"]
    #Crystals                - ["BackupData"][BackupName]["Crystals"]
    #Heath                   - ["BackupData"][BackupName]["Health"]
    #Max Health              - ["BackupData"][BackupName]["MaxHealth"]
    #Armor Plates            - ["BackupData"][BackupName]["ArmorPlates"]
    #Armor Plate Health      - ["BackupData"][BackupName]["ArmorPlatesHealth"]
    
    #Inventory               - [backupName]["Inventory"]
    #Weapon                  - [backupName]["Inventory"]["Weapon"]
    
    #Weapon Mod Slots        - [backupName]["Inventory"]["WeaponMods"]["Slots"]
    #Weapon Mods             - [backupName]["Inventory"]["WeaponMods"]["Mods"]
    #Weapon Mod Name         - [backupName]["Inventory"]["WeaponMods"]["Mods"][index of WMod]["Name"]
    #Weapon Mod Rarity       - [backupName]["Inventory"]["WeaponMods"]["Mods"][index of WMod]["Rarity"]
    #Weapon Mod Level        - [backupName]["Inventory"]["WeaponMods"]["Mods"][index of WMod]["Level"]
    
    #Grenade Mod Slots       - [backupName]["Inventory"]["GrenadeMods"]["Slots"]
    #Grenade Mods            - [backupName]["Inventory"]["GrenadeMods"]["Mods"]
    #Grenade Mod Name        - [backupName]["Inventory"]["GrenadeMods"]["Mods"][index of WMod]["Name"]
    #Grenade Mod Rarity      - [backupName]["Inventory"]["GrenadeMods"]["Mods"][index of WMod]["Rarity"]
    #Grenade Mod Level       - [backupName]["Inventory"]["GrenadeMods"]["Mods"][index of WMod]["Level"]
    
    #Perk Slots              - [backupName]["Inventory"]["Perks"]["Slots"]
    #Perks                   - [backupName]["Inventory"]["Perks"]["Perks"]
    #Perk Name               - [backupName]["Inventory"]["Perks"]["Perks"][index of WMod]["Name"]
    #Perk Rarity             - [backupName]["Inventory"]["Perks"]["Perks"][index of WMod]["Rarity"]
    #Perk Level              - [backupName]["Inventory"]["Perks"]["Perks"][index of WMod]["Level"]
    
    #Island types
    

    #Arctic
    
    #Arctic_Arena_01
    #Arctic_Arena_02
    #Arctic_Boss_01
    #Arctic_Boss_02
    #Arctic_Boss_03
    #Arctic_Horde_01
    #Arctic_Horde_02
    #Arctic_Horde_03
    #Arctic_Horde_04
    #Arctic_Horde_05
    #Arctic_Horde_06
    #Arctic_Horde_07
    #Arctic_Horde_08
    #Arctic_Parkour_01
    
    #Other
    
    #Animation
    #DebugPersistent
    #MedalLightroom
    
    #Tropical
    
    #Tropical_Arena_01
    #Tropical_Arena_02
    #Tropical_Arena_03
    #Tropical_Arena_04
    #Tropical_Arena_05
    #Tropical_Arena_06
    #Tropical_Arena_07
    #Tropical_Arena_08
    #Tropical_Boss_01
    #Tropical_Boss_02
    #Tropical_Horde_01
    #Tropical_Horde_02
    #Tropical_Horde_03
    #Tropical_Horde_04
    #Tropical_Horde_05
    #Tropical_Horde_06
    #Tropical_Horde_07
    #Tropical_Parkour_01
    #Tropical_Shop_01
    
    #Volcanic
    
    #Volcanic_Arena_01
    #Volcanic_Arena_02
    #Volcanic_Arena_03
    #Volcanic_Arena_04
    #Volcanic_Arena_05
    #Volcanic_Arena_06
    #Volcanic_Boss_01
    #Volcanic_Horde_01
    #Volcanic_Horde_02
    #Volcanic_Horde_03
    #Volcanic_Horde_04
    #Volcanic_Horde_05
    
    #Island
    
    #CrabIsland
    #Lobby
    #Persistent
    #Splash
    #TemplateIsland
    
    
    #Island Type
    
    #Boss - used when going to a Boss battle island, ie lvl 30 boss
    #Elite - used when going to a Elite battel island , ie not lvl 30 boss
    #CrabIsland - used when going to crab island for a victory
    #Arena - used when going to a Arena battle island
    #Horde - used when going to a Horde battle island
    #Shop - used when going to a Shop island
    #Parkour - used when going to a parkour island
    
    
    #LootPool
    
    #ECrabLootPool_MAX
    #Economy
    #Elemental
    #Skill
    #Health
    #Random
    #Upgrade
    #Critical
    #Greed
    #Speed
    #Damage
    #Luck
     
    
    backupJSON[backupName] = {}
    try:
        backupJSON[backupName]["RunTime"] = saveJSON["CurrentTime"]["Int"]["value"]
    except:
        backupJSON[backupName]["RunTime"] = 0
    try:
        backupJSON[backupName]["Score"] = saveJSON["Points"]["Int"]["value"]
    except:
        backupJSON[backupName]["Score"] = 0
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
    try:
        backupJSON[backupName]["Elimns"] = saveJSON["Eliminations"]["Int"]["value"]
    except:
        backupJSON[backupName]["Elimns"] = 0
    try:
        backupJSON[backupName]["ShotsFired"] = saveJSON["ShotsFired"]["Int"]["value"]
    except:
        backupJSON[backupName]["ShotsFired"] = 0
        
    try:
        backupJSON[backupName]["DmgDealt"] = saveJSON["DamageDealt"]["Int"]["value"]
    except:
        backupJSON[backupName]["DmgDealt"] = 0
        
    try:
        backupJSON[backupName]["MostDmgDealt"] = saveJSON["HighestDamageDealt"]["Int"]["value"]
    except:
        backupJSON[backupName]["MostDmgDealt"] = 0   
    
    try:
        backupJSON[backupName]["DmgTaken"] = saveJSON["DamageTaken"]["Int"]["value"]
    except:
       backupJSON[backupName]["DmgTaken"] = 0 
    
    try:
        backupJSON[backupName]["FlawlessIslands"] = saveJSON["NumFlawlessIslands"]["Int"]["value"]
    except:
        backupJSON[backupName]["FlawlessIslands"] =0    
    try:
        backupJSON[backupName]["ItemsSalvaged"] = saveJSON["NumTimesSalvaged"]["Int"]["value"]
    except:
        backupJSON[backupName]["ItemsSalvaged"] = 0
    try:
        backupJSON[backupName]["ItemsPurchased"] = saveJSON["NumShopPurchases"]["Int"]["value"]
    except:
        backupJSON[backupName]["ItemsPurchased"] = 0
    try:
        backupJSON[backupName]["ShopRerolls"] = saveJSON["NumShopRerolls"]["Int"]["value"]
    except:
        backupJSON[backupName]["ShopRerolls"] = 0
    try:
        backupJSON[backupName]["TotemsDestroyed"] = saveJSON["NumTotemsDestroyed"]["Int"]["value"]
    except:
        backupJSON[backupName]["TotemsDestroyed"] = 0
    
    try:
        backupJSON[backupName]["Crystals"] = saveJSON["Crystals"]["UInt32"]["value"]
    except:
        backupJSON[backupName]["Crystals"] = 0   
    
    diff = saveJSON["NextIslandInfo"]["Struct"]["value"]["Struct"]["Biome"]["Enum"]["value"]
    diff = diff[diff.index("::")+2:]
    backupJSON[backupName]["Biome"] = diff
    
    try:
        diff = saveJSON["NextIslandInfo"]["Struct"]["value"]["Struct"]["RewardLootPool"]["Enum"]["value"]
        diff = diff[diff.index("::")+2:]
    except:
        diff = "New Biome"    
    backupJSON[backupName]["LootType"] = diff
    backupJSON[backupName]["IslandName"] = saveJSON["NextIslandInfo"]["Struct"]["value"]["Struct"]["IslandName"]["Name"]["value"]
    diff = saveJSON["NextIslandInfo"]["Struct"]["value"]["Struct"]["IslandType"]["Enum"]["value"]
    diff = diff[diff.index("::")+2:]
    backupJSON[backupName]["IslandType"] = diff
    
    
    backupJSON[backupName]["Health"] = saveJSON["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentHealth"]["Float"]["value"]
    backupJSON[backupName]["MaxHealth"] = saveJSON["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentMaxHealth"]["Float"]["value"]
    try:
        backupJSON[backupName]["ArmorPlates"] = saveJSON["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlates"]["Int"]["value"]
        backupJSON[backupName]["ArmorPlatesHealth"] = saveJSON["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlateHealth"]["Float"]["value"]
    except:
        backupJSON[backupName]["ArmorPlates"] = 0
        backupJSON[backupName]["ArmorPlatesHealth"] = 0
    
    
    backupJSON[backupName]["Inventory"] = {}
    try:
        backupJSON[backupName]["Inventory"]["Weapon"] = parseWeapon(saveJSON["WeaponDA"]["Object"]["value"])
    except:
        backupJSON[backupName]["Inventory"]["Weapon"] = "Lobby Dependant"
    
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
    
    
    backupJSON[backupName]["Inventory"]["GrenadeMods"] = {}
    backupJSON[backupName]["Inventory"]["GrenadeMods"]["Slots"] = saveJSON["NumGrenadeModSlots"]["Byte"]["value"]["Byte"]
    backupJSON[backupName]["Inventory"]["GrenadeMods"]["Mods"] = {}
    try:
        GrenadeMods = saveJSON["GrenadeMods"]["Array"]["value"]["Struct"]["value"]
        GrenadeModArray = []
        while(len(GrenadeModArray)<len(GrenadeMods)):
            GrenadeModArray.append("")
        for i,name in enumerate(GrenadeMods):
            GrenadeModArray[i] = json.loads("{}")
            GrenadeModArray[i]["Name"] = parseGrenadeMod(name["Struct"]["GrenadeModDA"]["Object"]["value"])[0]
            GrenadeModArray[i]["Rarity"] = parseGrenadeMod(name["Struct"]["GrenadeModDA"]["Object"]["value"])[1]
            GrenadeModArray[i]["Level"] = name["Struct"]["Level"]["Byte"]["value"]["Byte"]
        backupJSON[backupName]["Inventory"]["GrenadeMods"]["Mods"] = GrenadeModArray
    except:
        backupJSON[backupName]["Inventory"]["GrenadeMods"]["Mods"] = []
    
    
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
    
    
    backupJSON[backupName]["CheckSum"] = checksum
    backupJSON[backupName]["NoSave"] = False
    cacheLock.acquire()
    
    try:
        cacheJSON["BackupData"][backupName] = backupJSON[backupName]
    except:
        cacheJSON["BackupData"] = {}
        cacheJSON["BackupData"][backupName] = backupJSON[backupName]
    cacheLock.release()
    stop = time.time()
    #print(backupName+str("  -  ")+str(round(stop-start,2))+str("  -ue  ")+str(round(ueStop-ueStart,2)))

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

def parseGrenadeMod(name):
    rarity = name[name.index("Mod/")+4:name.index("/",name.index("Mod/")+4)]
    name =  name[name.rindex(".DA_GrenadeMod_")+15:]
    return [spaceBeforeUpper(name) , rarity]

def parsePerk(name):
    rarity = name[name.index("Perk/")+5:name.index("/",name.index("Perk/")+5)]
    name =  name[name.rindex(".DA_Perk_")+9:]
    return [spaceBeforeUpper(name) , rarity]

def parseWeaponRank(rank):
    return rank[rank.index("ECrabRank::")+11:]

def formatNumber(num=0, decimal_places=0):
    return '{:,.{}f}'.format(num, decimal_places)

def parseSkin(skin):
    return skin[skin.rindex("MI_")+3:]
    
def parseChallenageName(name):
    name = name[4:]
    name = name.split("_")
    tname = ""
    for i in range(len(name)):
        if(len(name[i]) == name[i].count("I")):
            None
        else:
            name[i] = name[i].lower()
            name[i] = name[i][:1].upper()+name[i][1:]
        if(i == 0):
            tname = name[i]
        else:
            tname +=" "+name[i]
    return tname

def backupDetailsScreen(backupName):
    
    #Rarity Rare Color Number 3
    #Rarity Epic Color Number 13
    #Rarity Legendary Color Number 14
    #Rarity Greed Color Number 12
    
    
    leng = 22
    indent = ensureLength("",2)
    disbetween = 4
    backupJSON = cacheJSON["BackupData"][backupName]
    info =ensureLength("Backup Name: ",leng)+str(backupName)
    if(backupJSON["NoSave"]):
        info+="This backup has no save"
        scrollInfoMenu(info)
        return
    info += "\n"+str(ensureLength("Run Time: ",leng))+str(formatTime(backupJSON["RunTime"]))
    info += "\n"+str(ensureLength("Score: ",leng))+str(formatNumber(backupJSON["Score"],0))
    info += "\n"+str(ensureLength("Island: ",leng))+str(formatNumber(backupJSON["IslandNum"],0))
    info += "\n"+str(ensureLength("Crystals: ",leng))+str(formatNumber(backupJSON["Crystals"],0))
    info += "\n"+str(ensureLength("Difficulty: ",leng))+str(backupJSON["Diff"])
    info += "\n"+str(ensureLength("Biome: ",leng))+str(backupJSON["Biome"])
    if(str(backupJSON["LootType"]) != "New Biome"):
        info += "\n"+ensureLength("Loot Type: ",leng)+str(backupJSON["LootType"])
    info += "\n"+ensureLength("Island Name: ",leng)+str(backupJSON["IslandName"])
    info += "\n"+ensureLength("Island Type: ",leng)+str(backupJSON["IslandType"])
    info += "\n"+ensureLength("Health:",leng)+str(formatNumber(backupJSON["Health"],0))
    info += "\n"+ensureLength("Max Health:",leng)+str(formatNumber(backupJSON["MaxHealth"],0))
    info += "\n"+ensureLength("Armor Plates:",leng)+str(formatNumber(backupJSON["ArmorPlates"],0))
    info += "\n"+ensureLength("Armor Plate Health:",leng)+str(formatNumber(backupJSON["ArmorPlatesHealth"],0))  
    info += "\n"+ensureLength("Eliminations:",leng)+str(formatNumber(backupJSON["Elimns"],0))
    info += "\n"+ensureLength("Shots Fired:",leng)+str(formatNumber(backupJSON["ShotsFired"],0))
    info += "\n"+ensureLength("Damage Dealt:",leng)+str(formatNumber(backupJSON["DmgDealt"]))
    info += "\n"+ensureLength("Most Damage Dealt:",leng)+str(formatNumber(backupJSON["MostDmgDealt"]))
    info += "\n"+ensureLength("Damage Taken:",leng)+str(formatNumber(backupJSON["DmgTaken"]))
    info += "\n"+ensureLength("Flawless Islands:",leng)+str(formatNumber(backupJSON["FlawlessIslands"],0))
    info += "\n"+ensureLength("Items Salvaged:",leng)+str(formatNumber(backupJSON["ItemsSalvaged"],0))
    info += "\n"+ensureLength("Items Purchased:",leng)+str(formatNumber(backupJSON["ItemsPurchased"],0))
    info += "\n"+ensureLength("Shop Rerolls:",leng)+str(formatNumber(backupJSON["ShopRerolls"],0))
    info += "\n"+ensureLength("Totems Destroyed:",leng)+str(formatNumber(backupJSON["TotemsDestroyed"],0))
    try:
        info += "\n"+ensureLength("Average DPB:",leng)+str(formatNumber(round(backupJSON["DmgDealt"]/backupJSON["ShotsFired"],3),3))
        info += "\n"+ensureLength("Average SPS:",leng)+str(formatNumber(round(backupJSON["ShotsFired"]/backupJSON["RunTime"],3),3))
        info += "\n"+ensureLength("Average DPS:",leng)+str(formatNumber(round((backupJSON["ShotsFired"]/backupJSON["RunTime"])*(backupJSON["DmgDealt"]/backupJSON["ShotsFired"]),3),3))
    except:
        info += "\n"+ensureLength("Average DPB:",leng)+"0"
        info += "\n"+ensureLength("Average SPS:",leng)+"0"
        info += "\n"+ensureLength("Average DPS:",leng)+"0"
    if(len(backupJSON["DiffMods"])>0):
        info += "\nDifficulty Modifiers: "
        for diffMod in backupJSON["DiffMods"]:
            info += "\n"+indent+str(diffMod)
    info += "\n"
    info += "\n"+ensureLength("Weapon:",leng)+str(backupJSON["Inventory"]["Weapon"])
    info += "\n"+ensureLength("Weapon Mod Slots:",leng)+str(backupJSON["Inventory"]["WeaponMods"]["Slots"])
    info += "\n"+ensureLength("Grenade Mod Slots:",leng)+str(backupJSON["Inventory"]["GrenadeMods"]["Slots"])
    info += "\n"+ensureLength("Perk Slots:",leng)+str(backupJSON["Inventory"]["Perks"]["Slots"])
    info += "\nItems:"
    maxName = 0
    maxRarity = 0
    maxLevel = 0
    #Grenade Mod Name        - [backupName]["Inventory"]["GrenadeMods"]["Mods"][index of WMod]["Name"]
    #Grenade Mod Rarity      - [backupName]["Inventory"]["GrenadeMods"]["Mods"][index of WMod]["Rarity"]
    #Grenade Mod Level       - [backupName]["Inventory"]["GrenadeMods"]["Mods"][index of WMod]["Level"]
    for WMod in backupJSON["Inventory"]["WeaponMods"]["Mods"]:
        maxName = max(maxName,len(WMod["Name"]))
        maxRarity = max(maxRarity,len(WMod["Rarity"]))
        maxLevel = max(maxLevel,len(str(WMod["Level"])))
    for GMod in backupJSON["Inventory"]["GrenadeMods"]["Mods"]:
        maxName = max(maxName,len(GMod["Name"]))
        maxRarity = max(maxRarity,len(GMod["Rarity"]))
        maxLevel = max(maxLevel,len(str(GMod["Level"])))
    for Perk in backupJSON["Inventory"]["Perks"]["Perks"]:
        maxName = max(maxName,len(Perk["Name"]))
        maxRarity = max(maxRarity,len(Perk["Rarity"]))
        maxLevel = max(maxLevel,len(str(Perk["Level"])))
    maxRarity+=disbetween
    maxName+=disbetween
    info += "\n"+indent+ensureLength("Type",10+disbetween)+ensureLength("Rarity",maxRarity)+ensureLength("Name",maxName)+ensureLength("Level",maxLevel)
    #info += "\n"
    for WMod in backupJSON["Inventory"]["WeaponMods"]["Mods"]:
        info += "\n"+indent+ensureLength("Weapon Mod",10+disbetween)+ensureLength(WMod["Rarity"],maxRarity)+ensureLength(WMod["Name"],maxName)+ensureLength(str(WMod["Level"]),maxLevel)
    if(len(backupJSON["Inventory"]["WeaponMods"]["Mods"])>= 1):
       info += "\n" 
    for GMod in backupJSON["Inventory"]["GrenadeMods"]["Mods"]:
        info += "\n"+indent+ensureLength("Grenade Mod",10+disbetween)+ensureLength(GMod["Rarity"],maxRarity)+ensureLength(GMod["Name"],maxName)+ensureLength(str(GMod["Level"]),maxLevel)
    if(len(backupJSON["Inventory"]["GrenadeMods"]["Mods"])>= 1):
       info += "\n" 
    for Perk in backupJSON["Inventory"]["Perks"]["Perks"]:
        info += "\n"+indent+ensureLength("Perk",10+disbetween)+ensureLength(Perk["Rarity"],maxRarity)+ensureLength(Perk["Name"],maxName)+ensureLength(str(Perk["Level"]),maxLevel)
    scrollInfoMenu(info,itemRarityColors = True)
    return

def manageBackups():
    prompt = "Managing Backups\n"
    options = """Back-Returns you to the main menu
Edit Save-Edit your current save or any of your backups using uesave
Backup Save-Backup up your current save with a name of your choice
Update Backup-Choose a backup to update using your current save
Restore Save-Set your current save using a backup
Delete Backup-Delete a backup
List Backups and Backup Details-List backups and some details about, choose a backup to learn more about it"""
    while True:
        choice = scrollSelectMenu(prompt,options)
        if(choice == 0):
            return
        elif(choice == 1):
            editBackupRaw()
        elif(choice == 2):
            backupSave()
        elif(choice == 3):
            updateBackup()
        elif(choice == 4):
            restoreBackup()
        elif(choice == 5):
            deleteBackup()
        elif(choice == 6):
            listBackups()

def managePresets():
    prompt = "Managing Presets\n"
    options = """Back-Returns you to the main menu
Create Preset-Create a new preset
Use Preset-Set current save or backup using a preset
Edit Presets-Edit one of your presets
Delete Preset-Delete a preset
List Presets and Preset Details-List all your presets, select a preset to see it's settings"""
    while True:
        choice = scrollSelectMenu(prompt,options)
        if(choice == 0):
            return
        elif(choice == 1):
            createPreset()
        elif(choice == 2):
            usePreset()
        elif(choice == 3):
            editPresetMenu()
        elif(choice == 4):
            deletePreset()
        elif(choice == 5):
            listPresets()

def genPlayerData(saveJSON,checksum):
    start = time.time()
    global cacheLock
    global cacheJSON
    try:
        cacheJSON["PlayerData"] = {}
        saveJSON = saveJSON["root"]["properties"]
    except:
        cacheLock.acquire()
        cacheJSON["PlayerData"] = {}
        cacheLock.release()
        return
    PlayerDataJSON = json.loads("{}")
    # in .sav to json
    #XP to next level up           - ["XPToNextLevelUp"]["Int"]["value"]
    #Weapon Rank Array             - ["RankedWeapons"]["Array"]["value"]["Struct"]["value"]
    #    Weapon Name From Array    - ["Struct"]["Weapon"]["Object"]["value"] , use parseWeapon()
    #    Weapon Rank From Array    - ["Struct"]["Rank"]["Enum"]["value"] , use parseWeaponRank()
    #Account Level                 - ["AccountLevel"]["Int"]["value"]
    #Keys                          - ["Keys"]["Int"]["value"]
    #Crab Skin                     - ["CrabSkin"]["Object"]["value"] , use parseSkin()
    #Weapon                        - ["WeaponDA"]["Object"]["value"] , use parseWeapon()
    #Challenages Array             - ["Challenges"]["Array"]["value"]["Struct"]["value"]
    #    Name                      - ["Struct"]["ChallenageID"]["Name"]["value"] , use parseChallenageName()
    #    Description               - ["Struct"]["ChallengeDescription"]["Str"]["value"]
    #    Progress                  - ["Struct"]["ChallengeProgress"]["Int"]["value"]
    #    Goal                      - ["Struct"]["ChallengeGoal"]["Int"]["value"]
    #    Completed                 - ["Struct"]["bChallengeCompleted"]["Bool"]["value"]
    #    Cosmetic Reward Name      - ["Struct"]["CosmeticReward"]["Struct"]["value"]["Struct"]["CosmeticName"]["Str"]["value"]
    #Unlocked Weapons Array        - ["UnlockedWeapons"]["Array"]["value"]["Base"]["Object"] , make sure to parse each with parseWeapon()
    #Unlocked Weapon Mods Array    - ["UnlockedWeaponMods"]["Array"]["value"]["Base"]["Object"]
    #Unlocked Grenade Mods Array   - ["UnlockedGrenadeMods"]["Array"]["value"]["Base"]["Object"]
    #Unlocked Perks Array          - ["UnlockedPerks"]["Array"]["value"]["Base"]["Object"]
    #Easy Attempts                 - ["EasyAttempts"]["Int"]["value"]
    #Easy Wins                     - ["EasyWins"]["Int"]["value"]
    #Easy Highscore                - ["EasyHighScore"]["Int"]["value"]
    #Easy Winstreak                - ["EasyWinStreak"]["Int"]["value"]
    #Easy Highest Island           - ["EasyHighestIslandReached"]["Int"]["value"]
    #Normal Attempts               - ["NormalAttempts"]["Int"]["value"]
    #Normal Wins                   - ["NormalWins"]["Int"]["value"]
    #Normal Highscore              - ["NormalHighScore"]["Int"]["value"]
    #Normal Winstreak              - ["NormalWinStreak"]["Int"]["value"]
    #Normal Highest Island         - ["NormalHighestIslandReached"]["Int"]["value"]
    #Nightmare Attempts            - ["NightmareAttempts"]["Int"]["value"]
    #Nightmare Wins                - ["NightmareWins"]["Int"]["value"]
    #Nightmare Highscore           - ["NightmareHighScore"]["Int"]["value"]
    #Nightmare Winstreak           - ["NightmareWinStreak"]["Int"]["value"]
    #Nightmare Highest Island      - ["NightmareHighestIslandReached"]["Int"]["value"]
    
    
    #in cache json
    #XP to next level up           - ["XPToNextLevelUp"]
    #Weapon Rank Array             - ["RankedWeapons"]
    #    Weapon Name From Array    - ["RankedWeapons"][index]["Name"]
    #    Weapon Rank From Array    - ["RankedWeapons"][index]["Rank"]
    #Account Level                 - ["AccountLevel"]
    #Keys                          - ["Keys"]
    #Crab Skin                     - ["Skin"]
    #Current Weapon                - ["CurrentWeapon"]
    #Challenages Array             - ["Challenges"]
    #    Name                      - ["Challenges"][index]["Name"]
    #    Description               - ["Challenges"][index]["Description"]
    #    Progress                  - ["Challenges"][index]["Progress"]
    #    Goal                      - ["Challenges"][index]["Goal"]
    #    Completed                 - ["Challenges"][index]["Completed"]
    #    Cosmetic Reward Name      - ["Challenges"][index]["SkinRewardName"]
    #Unlocked Weapons Array        - ["UnlockedWeapons"]
    #Unlocked Weapon Mods Array    - ["UnlockedWeaponMods"]
    #Unlocked Grenade Mods Array   - ["UnlockedGrenadeMods"]
    #Unlocked Perks Array          - ["UnlockedPerks"]
    #Easy Attempts                 - ["EasyAttempts"]
    #Easy Wins                     - ["EasyWins"]
    #Easy Highscore                - ["EasyHighScore"]
    #Easy Winstreak                - ["EasyWinStreak"]
    #Easy Highest Island           - ["EasyHighestIslandReached"]
    #Normal Attempts               - ["NormalAttempts"]
    #Normal Wins                   - ["NormalWins"]
    #Normal Highscore              - ["NormalHighScore"]
    #Normal Winstreak              - ["NormalWinStreak"]
    #Normal Highest Island         - ["NormalHighestIslandReached"]
    #Nightmare Attempts            - ["NightmareAttempts"]
    #Nightmare Wins                - ["NightmareWins"]
    #Nightmare Highscore           - ["NightmareHighScore"]
    #Nightmare Winstreak           - ["NightmareWinStreak"]
    #Nightmare Highest Island      - ["NightmareHighestIslandReached"]
    
    try:
        PlayerDataJSON["XPToNextLevelUp"] = saveJSON["XPToNextLevelUp"]["Int"]["value"]
    except:
        PlayerDataJSON["XPToNextLevelUp"] = 0
    PlayerDataJSON["RankedWeapons"] = []
    RWArray = []
    RWArrayRaw = saveJSON["RankedWeapons"]["Array"]["value"]["Struct"]["value"]
    for RWArrayObject in RWArrayRaw:
        RankedWeapon = json.loads("{}")
        RankedWeapon["Name"] = parseWeapon(RWArrayObject["Struct"]["Weapon"]["Object"]["value"])
        RankedWeapon["Rank"] = parseWeaponRank(RWArrayObject["Struct"]["Rank"]["Enum"]["value"])
        RWArray.append(RankedWeapon)
    PlayerDataJSON["RankedWeapons"] = RWArray
    try:
        PlayerDataJSON["AccountLevel"] = saveJSON["AccountLevel"]["Int"]["value"]
    except:
        PlayerDataJSON["AccountLevel"] = 0 
    try:
        PlayerDataJSON["Keys"] = saveJSON["Keys"]["Int"]["value"]
    except:
        PlayerDataJSON["Keys"] = 0
    PlayerDataJSON["Skin"] = parseSkin(saveJSON["CrabSkin"]["Object"]["value"])
    PlayerDataJSON["CurrentWeapon"] = parseWeapon(saveJSON["WeaponDA"]["Object"]["value"])
    PlayerDataJSON["Challenges"] = []
    ChallengeArray = []
    ChallengeArrayRaw = saveJSON["Challenges"]["Array"]["value"]["Struct"]["value"]
    for ChallengeArrayObject in ChallengeArrayRaw:
        Challenge = json.loads("{}")
        #infoScreen(str(ChallengeArrayObject["Struct"].keys()))
        Challenge["Name"] = parseChallenageName(ChallengeArrayObject["Struct"]["ChallengeID"]["Name"]["value"])
        Challenge["Description"] = (ChallengeArrayObject["Struct"]["ChallengeDescription"]["Str"]["value"])
        Challenge["Progress"] = (ChallengeArrayObject["Struct"]["ChallengeProgress"]["Int"]["value"])
        Challenge["Goal"] = (ChallengeArrayObject["Struct"]["ChallengeGoal"]["Int"]["value"])
        Challenge["Completed"] = (ChallengeArrayObject["Struct"]["bChallengeCompleted"]["Bool"]["value"])
        Challenge["SkinRewardName"] = (ChallengeArrayObject["Struct"]["CosmeticReward"]["Struct"]["value"]["Struct"]["CosmeticName"]["Str"]["value"])
        ChallengeArray.append(Challenge)
    PlayerDataJSON["Challenges"] = ChallengeArray
    
    PlayerDataJSON["UnlockedWeapons"] = []
    UnlockedWeaponsArray = []
    UnlockedWeaponsArrayRaw = saveJSON["UnlockedWeapons"]["Array"]["value"]["Base"]["Object"]
    for UnlockedWeapon in UnlockedWeaponsArrayRaw:
        UnlockedWeaponsArray.append(parseWeapon(UnlockedWeapon))
    PlayerDataJSON["UnlockedWeapons"] = UnlockedWeaponsArray
    
    PlayerDataJSON["UnlockedWeaponMods"] = []
    UnlockedWeaponModsArray = []
    UnlockedWeaponModsArrayRaw = saveJSON["UnlockedWeaponMods"]["Array"]["value"]["Base"]["Object"]
    for UnlockedWeaponMod in UnlockedWeaponModsArrayRaw:
        WeaponMod = json.loads("{}")
        WeaponMod["Name"] = parseWeaponMod(UnlockedWeaponMod)[0]
        WeaponMod["Rarity"] = parseWeaponMod(UnlockedWeaponMod)[1]
        UnlockedWeaponModsArray.append(WeaponMod)
    PlayerDataJSON["UnlockedWeaponMods"] = UnlockedWeaponModsArray

    PlayerDataJSON["UnlockedGrenadeMods"] = []
    UnlockedGrenadeModsArray = []
    UnlockedGrenadeModsArrayRaw = saveJSON["UnlockedGrenadeMods"]["Array"]["value"]["Base"]["Object"]
    for UnlockedGrenadeMod in UnlockedGrenadeModsArrayRaw:
        GrenadeMod = json.loads("{}")
        GrenadeMod["Name"] = parseGrenadeMod(UnlockedGrenadeMod)[0]
        GrenadeMod["Rarity"] = parseGrenadeMod(UnlockedGrenadeMod)[1]
        UnlockedGrenadeModsArray.append(GrenadeMod)
    PlayerDataJSON["UnlockedGrenadeMods"] = UnlockedGrenadeModsArray
    
    PlayerDataJSON["UnlockedPerks"] = []
    UnlockedPerksArray = []
    UnlockedPerksArrayRaw = saveJSON["UnlockedPerks"]["Array"]["value"]["Base"]["Object"]
    for UnlockedPerk in UnlockedPerksArrayRaw:
        Perk = json.loads("{}")
        Perk["Name"] = parsePerk(UnlockedPerk)[0]
        Perk["Rarity"] = parsePerk(UnlockedPerk)[1]
        UnlockedPerksArray.append(Perk)
    PlayerDataJSON["UnlockedPerks"] = UnlockedPerksArray
    
    try:
        PlayerDataJSON["EasyAttempts"] = saveJSON["EasyAttempts"]["Int"]["value"]
    except:
        PlayerDataJSON["EasyAttempts"] = 0

    try:
        PlayerDataJSON["EasyWins"] = saveJSON["EasyWins"]["Int"]["value"]
    except:
        PlayerDataJSON["EasyWins"] = 0

    try:
        PlayerDataJSON["EasyHighScore"] = saveJSON["EasyHighScore"]["Int"]["value"]
    except:
        PlayerDataJSON["EasyHighScore"] = 0

    try:
        PlayerDataJSON["EasyWinStreak"] = saveJSON["EasyWinStreak"]["Int"]["value"]
    except:
        PlayerDataJSON["EasyWinStreak"] = 0

    try:
        PlayerDataJSON["EasyHighestIslandReached"] = saveJSON["EasyHighestIslandReached"]["Int"]["value"]
    except:
        PlayerDataJSON["EasyHighestIslandReached"] = 0

    try:
        PlayerDataJSON["NormalAttempts"] = saveJSON["NormalAttempts"]["Int"]["value"]
    except:
        PlayerDataJSON["NormalAttempts"] = 0

    try:
        PlayerDataJSON["NormalWins"] = saveJSON["NormalWins"]["Int"]["value"]
    except:
        PlayerDataJSON["NormalWins"] = 0

    try:
        PlayerDataJSON["NormalHighScore"] = saveJSON["NormalHighScore"]["Int"]["value"]
    except:
        PlayerDataJSON["NormalHighScore"] = 0

    try:
        PlayerDataJSON["NormalWinStreak"] = saveJSON["NormalWinStreak"]["Int"]["value"]
    except:
        PlayerDataJSON["NormalWinStreak"] = 0

    try:
        PlayerDataJSON["NormalHighestIslandReached"] = saveJSON["NormalHighestIslandReached"]["Int"]["value"]
    except:
        PlayerDataJSON["NormalHighestIslandReached"] = 0

    try:
        PlayerDataJSON["NightmareAttempts"] = saveJSON["NightmareAttempts"]["Int"]["value"]
    except:
        PlayerDataJSON["NightmareAttempts"] = 0

    try:
        PlayerDataJSON["NightmareWins"] = saveJSON["NightmareWins"]["Int"]["value"]
    except:
        PlayerDataJSON["NightmareWins"] = 0

    try:
        PlayerDataJSON["NightmareHighScore"] = saveJSON["NightmareHighScore"]["Int"]["value"]
    except:
        PlayerDataJSON["NightmareHighScore"] = 0

    try:
        PlayerDataJSON["NightmareWinStreak"] = saveJSON["NightmareWinStreak"]["Int"]["value"]
    except:
        PlayerDataJSON["NightmareWinStreak"] = 0

    try:
        PlayerDataJSON["NightmareHighestIslandReached"] = saveJSON["NightmareHighestIslandReached"]["Int"]["value"]
    except:
        PlayerDataJSON["NightmareHighestIslandReached"] = 0
        
    cacheLock.acquire()
    try:
        cacheJSON["PlayerData"] = PlayerDataJSON
    except:
        cacheJSON["PlayerData"] = {}
        cacheJSON["PlayerData"] = PlayerDataJSON
    cacheLock.release()
    stop = time.time()
    
def createPreset():
    defaultPreset = "{\"Diff\":\"Normal\",\"IslandNum\":1,\"DiffMods\":[],\"Crystals\":0,\"Biome\":\"Tropical\",\"LootType\":\"Random Loot Type\",\"IslandName\":\"Tropical Arena Island\",\"IslandType\":\"Automatic\",\"Health\":100,\"MaxHealth\":100,\"ArmorPlates\":0,\"ArmorPlatesHealth\":0,\"HealthMultiplier\":1,\"DamageMultiplier\":1,\"keyTotemItem\":false,\"Inventory\":{\"Weapon\":\"Lobby Dependant\",\"WeaponMods\":{\"Slots\":24,\"Mods\":[]},\"GrenadeMods\":{\"Slots\":24,\"Mods\":[]},\"Perks\":{\"Slots\":24,\"Perks\":[]}}}"
    preset = json.loads(defaultPreset)
    prompt = "What should the preset be named?\nEnter nothing to go back"
    name = backupNameMenu(prompt)
    if(name.replace(" ","") == ""):
        return
    preset = editPreset(preset,name)
    
def listPresets():

    loadPresets()
    foldersInfo = getPresets(moreInfo=1)
    presetss = getPresets()
    prompt = str(len(presetss))+" Presets Stored\nSelect Preset for more info about that preset\n"
    presets = "Back\n"
    for i,name in enumerate(foldersInfo):
        if(i == 0):
            presets += str(name)
        else:
            presets += "\n"+str(name)
            
    choice = scrollSelectMenu(prompt,presets,wrapMode=2,detailsSelected = False)
    if(choice == 0):
        return
    choice -=1
    presetDetailsScreen(presetss[choice])
    listPresets()
    
def getPresets(moreInfo = False):
    global presetsJSON
    global owd
    
    
    
    curDir = owd+"/CrabChampionSaveManager/Presets"
    if(not os.path.exists(curDir)):
        os.makedirs(curDir,exist_ok=True)
    
    items = os.listdir(curDir)
    
    presets = [item for item in items if os.path.isfile(os.path.join(curDir,item))]
    pres = presets.copy()
    for pre in presets:
        f = open(owd+"/CrabChampionSaveManager/Presets/"+pre,"r")
        try:
            json.loads(f.read())
        except:
            pres.remove(pre)
    presets = pres.copy()
    f = open("debug.txt",'w')
    f.write(str(presets))
    f.close()
    for i,pre in enumerate(presets):
        if(".json" in pre):
            f = open(owd+"/CrabChampionSaveManager/Presets/"+pre.replace(".json",".ccsm"),"w")
            f.write(open(owd+"/CrabChampionSaveManager/Presets/"+pre,"r").read())
            f.close()
            os.remove(owd+"/CrabChampionSaveManager/Presets/"+pre)
            presets[i] = presets[i].replace(".json",".ccsm")
        presets[i] = (pre.replace(".ccsm","")) 
    if(not moreInfo):
        return presets
    else:
        oPresets = presets
        try:
            loadPresets()
            maxLenName = 0
            maxLenDiff = 0
            maxLenIsland = 0
            for preset in presets:
                maxLenName = max(maxLenName,len(preset))
                maxLenDiff = max(maxLenDiff,len("Diff: "+str(presetsJSON[preset]["Diff"])))
                maxLenIsland = max(maxLenIsland,len("Island: "+str(presetsJSON[preset]["IslandNum"])))
            distance = 4
            maxLenDiff += distance
            maxLenIsland += distance
            for i in range(len(presets)):
                preset = presets[i]
                diff = "Diff: "+str(presetsJSON[preset]["Diff"])
                diff = ensureLength(diff,maxLenDiff)
                islandnum = "Island: "+str(presetsJSON[preset]["IslandNum"])
                islandnum = ensureLength(islandnum,maxLenIsland)
                preset = ensureLength(preset,maxLenName)
                presets[i] = preset+" - "+diff+islandnum
            return presets
        except Exception as e:
            # import traceback
            # print(e)
            # traceback.print_exc()
            return oPresets
    
def loadPresets():
    global presetsJSON
    global owd
    presets = getPresets()
    presetsJSON = json.loads("{}")
    for preset in presets:
        try:
            presetsJSON[preset]= json.loads(open(owd.replace("\\","/")+"/CrabChampionSaveManager/Presets/"+preset+".ccsm","r").read())
        except:
            None
        opreset = presetsJSON[preset].copy()
        presetsJSON[preset] = updatePreset(presetsJSON[preset].copy())
        if(opreset != presetsJSON[preset]):
            f = open(owd.replace("\\","/")+"/CrabChampionSaveManager/Presets/"+preset+".ccsm","w")
            f.write(json.dumps(presetsJSON[preset],indent=4))
            f.close()
    
def presetDetailsScreen(preset):
    
    #Rarity Rare Color Number 3
    #Rarity Epic Color Number 13
    #Rarity Legendary Color Number 14
    #Rarity Greed Color Number 12
    
    
    leng = 22
    try:
        curses.init_pair(1, 3, -1)
        curses.init_pair(2, 13, -1)
        curses.init_pair(3, 14, -1)
        curses.init_pair(4, 12, -1)
        colors = "BackupDetails"
    except:
        colors = "None"
    indent = ensureLength("",2)
    disbetween = 4
    presetJSON = presetsJSON[preset]
    info =ensureLength("Preset Name: ",leng)+str(preset)
    info += "\n"+str(ensureLength("Island: ",leng))+str(formatNumber(presetJSON["IslandNum"],0))
    info += "\n"+str(ensureLength("Crystals: ",leng))+str(formatNumber(presetJSON["Crystals"],0))
    info += "\n"+str(ensureLength("Difficulty: ",leng))+str(presetJSON["Diff"])
    info += "\n"+str(ensureLength("Biome: ",leng))+str(presetJSON["Biome"])
    info += "\n"+ensureLength("Loot Type: ",leng)+str(presetJSON["LootType"])
    info += "\n"+ensureLength("Island Type: ",leng)+str(presetJSON["IslandType"])
    info += "\n"+ensureLength("Health:",leng)+str(formatNumber(presetJSON["Health"],0))
    info += "\n"+ensureLength("Max Health:",leng)+str(formatNumber(presetJSON["MaxHealth"],0))
    info += "\n"+ensureLength("Armor Plates:",leng)+str(formatNumber(presetJSON["ArmorPlates"],0))
    info += "\n"+ensureLength("Armor Plate Health:",leng)+str(formatNumber(presetJSON["ArmorPlatesHealth"],0))  
    if(len(presetJSON["DiffMods"])>0):
        info += "\nDifficulty Modifiers: "
        for diffMod in presetJSON["DiffMods"]:
            info += "\n"+indent+str(diffMod)
    info += "\n"
    info += "\n"+ensureLength("Weapon:",leng)+str(presetJSON["Inventory"]["Weapon"])
    info += "\n"+ensureLength("Weapon Mod Slots:",leng)+str(presetJSON["Inventory"]["WeaponMods"]["Slots"])
    info += "\n"+ensureLength("Grenade Mod Slots:",leng)+str(presetJSON["Inventory"]["GrenadeMods"]["Slots"])
    info += "\n"+ensureLength("Perk Slots:",leng)+str(presetJSON["Inventory"]["Perks"]["Slots"])
    info += "\nItems:"
    maxName = 0
    maxRarity = 0
    maxLevel = 0
    for WMod in presetJSON["Inventory"]["WeaponMods"]["Mods"]:
        maxName = max(maxName,len(WMod["Name"]))
        maxRarity = max(maxRarity,len(WMod["Rarity"]))
        maxLevel = max(maxLevel,len(str(WMod["Level"])))
    for GMod in presetJSON["Inventory"]["GrenadeMods"]["Mods"]:
        maxName = max(maxName,len(GMod["Name"]))
        maxRarity = max(maxRarity,len(GMod["Rarity"]))
        maxLevel = max(maxLevel,len(str(GMod["Level"])))
    for Perk in presetJSON["Inventory"]["Perks"]["Perks"]:
        maxName = max(maxName,len(Perk["Name"]))
        maxRarity = max(maxRarity,len(Perk["Rarity"]))
        maxLevel = max(maxLevel,len(str(Perk["Level"])))
    maxRarity+=disbetween
    maxName+=disbetween
    info += "\n"+indent+ensureLength("Type",10+disbetween)+ensureLength("Rarity",maxRarity)+ensureLength("Name",maxName)+ensureLength("Level",maxLevel)
    #info += "\n"
    for WMod in presetJSON["Inventory"]["WeaponMods"]["Mods"]:
        info += "\n"+indent+ensureLength("Weapon Mod",10+disbetween)+ensureLength(WMod["Rarity"],maxRarity)+ensureLength(WMod["Name"],maxName)+ensureLength(str(WMod["Level"]),maxLevel)
    if(len(presetJSON["Inventory"]["WeaponMods"]["Mods"])>= 1):
       info += "\n" 
    for GMod in presetJSON["Inventory"]["GrenadeMods"]["Mods"]:
        info += "\n"+indent+ensureLength("Grenade Mod",10+disbetween)+ensureLength(GMod["Rarity"],maxRarity)+ensureLength(GMod["Name"],maxName)+ensureLength(str(GMod["Level"]),maxLevel)
    if(len(presetJSON["Inventory"]["GrenadeMods"]["Mods"])>= 1):
       info += "\n" 
    for Perk in presetJSON["Inventory"]["Perks"]["Perks"]:
        info += "\n"+indent+ensureLength("Perk",10+disbetween)+ensureLength(Perk["Rarity"],maxRarity)+ensureLength(Perk["Name"],maxName)+ensureLength(str(Perk["Level"]),maxLevel)
    scrollInfoMenu(info,itemRarityColors=True)
    return

def deletePreset():
    global owd
    loadPresets()
    presets = getPresets()
    presetsDetails = getPresets(moreInfo=True)
    prompt = "Which preset would you like to delete?\n"
    options="Back"
    for preset in presetsDetails:
        options+="\n"+preset
    choice = scrollSelectMenu(prompt,options,detailsSelected=False)
    if choice == 0:
        return
    preset = presets[choice-1]
    try:
        os.remove(owd+"/CrabChampionSaveManager/Presets/"+preset+".ccsm")
    except:
        os.remove(owd+"/CrabChampionSaveManager/Presets/"+preset+".ccsm")
    return

def presetNameMenu(prompt):
    global screen

    if(type(prompt) == type("")):
        prompt = prompt.split("\n")

    curstate = curses.curs_set(1)
    presetName = ""
    while True:
        screen.clear()
        for i , prom in enumerate(prompt):
            screen.addstr(i, 0, prom)
        screen.addstr(len(prompt)-1, 0, prompt[len(prompt)-1]+": "+presetName)
        screen.refresh()
        key = screen.getch()

        if key == curses.KEY_BACKSPACE or key in [127, 8]:
            presetName = presetName[:-1]
        elif key == curses.KEY_ENTER or key in [10, 13]:
            curses.curs_set(curstate)
            if(presetName == ""):
                return ""
            elif isValidPresetName(presetName):
                return presetName
            else:
                infoScreen("Invaild preset name\Preset name can not contain any of these characters \\ / : * ? \" < > | .")
                screen.refresh()
                curses.napms(2000)  # Display the error message for 2 seconds
                presetName = ""
        else:
            presetName += chr(key)
            
def editPreset(preset,name,overriade = False):
    getUnlocked()
    global WEAPONS
    global WEAPONMODS
    global GRENADEMODS
    global PERKS
    global DIFFMODS
    global DIFFMODSDETAILS
    DiffModsWithDetails = []
    for i in range(len(DIFFMODS)):
        DiffModsWithDetails.append(DIFFMODS[i]+" - "+DIFFMODSDETAILS[i])
    leng = 22
    indent = ensureLength("",2)
    disbetween = 4
    presetJSON = preset
    
    #island name             - ["BackupData"][BackupName]["IslandName"]
    preset = updatePreset(preset)
    choice = 0
    window = 0
    oname = name
    while True:
        info = "Finish"
        info +="\n"+ensureLength("Preset Name: ",leng)+str(name)
        info += "\n"+str(ensureLength("Island: ",leng))+str(formatNumber(presetJSON["IslandNum"],0))
        info += "\n"+str(ensureLength("Crystals: ",leng))+str(formatNumber(presetJSON["Crystals"],0))
        info += "\n"+str(ensureLength("Difficulty: ",leng))+str(presetJSON["Diff"])
        info += "\n"+str(ensureLength("Biome: ",leng))+str(presetJSON["Biome"])
        info += "\n"+str(ensureLength("Island Name: ",leng))+str(presetJSON["IslandName"])
        info += "\n"+ensureLength("Loot Type: ",leng)+str(presetJSON["LootType"])
        info += "\n"+ensureLength("Island Type: ",leng)+str(presetJSON["IslandType"])
        info += "\n"+ensureLength("Health:",leng)+str(formatNumber(presetJSON["Health"],0))
        info += "\n"+ensureLength("Max Health:",leng)+str(formatNumber(presetJSON["MaxHealth"],0))
        info += "\n"+ensureLength("Armor Plates:",leng)+str(formatNumber(presetJSON["ArmorPlates"],0))
        info += "\n"+ensureLength("Armor Plate Health:",leng)+str(formatNumber(presetJSON["ArmorPlatesHealth"],0))
        info += "\n"+ensureLength("Health Multiplier:",leng)+str(formatNumber(presetJSON["HealthMultiplier"],3))  
        info += "\n"+ensureLength("Damage Multiplier:",leng)+str(formatNumber(presetJSON["DamageMultiplier"],3))  
        info += "\nDifficulty Modifiers: "
        if(len(presetJSON["DiffMods"])>0):
            for diffMod in presetJSON["DiffMods"]:
                info += "\n"+indent+str(diffMod)+" - "+DIFFMODSDETAILS[DIFFMODS.index(diffMod)]
        if(len(presetJSON["DiffMods"])<12):
            info += "\n"+indent+str("Add Difficulty Modifer")
        info += "\n"
        info += "\n"+ensureLength("Weapon:",leng)+str(presetJSON["Inventory"]["Weapon"])
        info += "\n"+ensureLength("Weapon Mod Slots:",leng)+str(presetJSON["Inventory"]["WeaponMods"]["Slots"])
        info += "\n"+ensureLength("Grenade Mod Slots:",leng)+str(presetJSON["Inventory"]["GrenadeMods"]["Slots"])
        info += "\n"+ensureLength("Perk Slots:",leng)+str(presetJSON["Inventory"]["Perks"]["Slots"])
        info += "\n"+ensureLength("Key Totem:",leng)+str(presetJSON["keyTotemItem"])
        info += "\nItems:"
        maxName = 6
        maxRarity = 8
        maxLevel = 0
        for WMod in presetJSON["Inventory"]["WeaponMods"]["Mods"]:
            maxName = max(maxName,len(WMod["Name"]))
            maxRarity = max(maxRarity,len(WMod["Rarity"]))
            maxLevel = max(maxLevel,len(str(WMod["Level"])))
        for GMod in presetJSON["Inventory"]["GrenadeMods"]["Mods"]:
            maxName = max(maxName,len(GMod["Name"]))
            maxRarity = max(maxRarity,len(GMod["Rarity"]))
            maxLevel = max(maxLevel,len(str(GMod["Level"])))
        for Perk in presetJSON["Inventory"]["Perks"]["Perks"]:
            maxName = max(maxName,len(Perk["Name"]))
            maxRarity = max(maxRarity,len(Perk["Rarity"]))
            maxLevel = max(maxLevel,len(str(Perk["Level"])))
        maxRarity+=disbetween
        maxName+=disbetween
        info += "\n"+indent+ensureLength("Type",10+disbetween)+ensureLength("Rarity",maxRarity)+ensureLength("Name",maxName)+ensureLength("Level",maxLevel)
        #info += "\n"
        for WMod in presetJSON["Inventory"]["WeaponMods"]["Mods"]:
            info += "\n"+indent+ensureLength("Weapon Mod",10+disbetween)+ensureLength(WMod["Rarity"],maxRarity)+ensureLength(WMod["Name"],maxName)+ensureLength(str(WMod["Level"]),maxLevel)
        if(len(presetJSON["Inventory"]["WeaponMods"]["Mods"])<= 64):
            info += "\nAdd Weapon Mod" 
        info += "\n" 
        for GMod in presetJSON["Inventory"]["GrenadeMods"]["Mods"]:
            info += "\n"+indent+ensureLength("Grenade Mod",10+disbetween)+ensureLength(GMod["Rarity"],maxRarity)+ensureLength(GMod["Name"],maxName)+ensureLength(str(GMod["Level"]),maxLevel)
        if(len(presetJSON["Inventory"]["GrenadeMods"]["Mods"])<= 64):
            info += "\nAdd Grenade Mod" 
        info += "\n" 
        for Perk in presetJSON["Inventory"]["Perks"]["Perks"]:
            info += "\n"+indent+ensureLength("Perk",10+disbetween)+ensureLength(Perk["Rarity"],maxRarity)+ensureLength(Perk["Name"],maxName)+ensureLength(str(Perk["Level"]),maxLevel)  
        if(len(presetJSON["Inventory"]["Perks"]["Perks"])<= 64):
            info += "\nAdd Perk" 

        choice , window = scrollSelectMenu("",info,skip=["",str(indent+ensureLength("Type",10+disbetween)+ensureLength("Rarity",maxRarity)+ensureLength("Name",maxName)+ensureLength("Level",maxLevel)),"Difficulty Modifiers: ","Items:"],startChoice = choice,scrollWindowStart=window,returnMore=True,checkForRarityColor=True,useItemColors=True)
        info = info.split("\n")
        
        if(":" in info[choice] and "Preset Name" in info[choice][:info[choice].index(":")]):
            prompt = "What should the preset be named?\nEnter nothing to go back"
            nam = backupNameMenu(prompt,escape = "",name = name,escapeReturn="")
            if(not nam == ""):
                name = nam
            
        elif(":" in info[choice] and "Island" in info[choice][:info[choice].index(":")]and not "Name" in info[choice][:info[choice].index(":")] and not "Type" in info[choice][:info[choice].index(":")]):
            presetJSON["IslandNum"] = userInputMenuNum("Enter number for island\nEnter nothing to not change anything","",0,2147483647,default = presetJSON["IslandNum"],useDefaultAsPreset=True)
            
        elif(":" in info[choice] and "Crystals" in info[choice][:info[choice].index(":")]):
            presetJSON["Crystals"] = userInputMenuNum("Enter number for crystals\nEnter nothing to not change anything","",-1,4294967293,default = presetJSON["Crystals"],useDefaultAsPreset=True)
            
        elif(":" in info[choice] and "Difficulty" in info[choice][:info[choice].index(":")]):
            prompt = "Select Difficulty\nCurrent Difficulty is "+presetJSON["Diff"]+"\n"
            diff = ["Easy","Normal","Nightmare"]
            
            presetJSON["Diff"] = diff[scrollSelectMenu(prompt,diff,startChoice=diff.index(presetJSON["Diff"]))]
        
        elif(":" in info[choice] and "Biome" in info[choice][:info[choice].index(":")]):
            prompt = "Select Biome\nCurrent Biome is "+presetJSON["Biome"]+"\n"
            biome = ["Tropical","Arctic","Volcanic"]
            presetJSON["Biome"] = biome[scrollSelectMenu(prompt,biome,startChoice=biome.index(presetJSON["Biome"]))]
            
        elif(":" in info[choice] and "Island Name" in info[choice][:info[choice].index(":")]):
            prompt = "Select Island\nCurrent Island is "+presetJSON["IslandName"]+"\n"
            islandName = ["Tropical Arena Island","Tropical Horde Island","Tropical Elite Island","Tropical Parkour Island","Arctic Arena Island","Arctic Horde Island","Arctic Elite Island","Arctic Parkour Island","Volcanic Arena Island","Volcanic Horde Island","Volcanic Boss Island","Tropical_Arena_01","Tropical_Arena_02","Tropical_Arena_03","Tropical_Arena_04","Tropical_Arena_05","Tropical_Arena_06","Tropical_Arena_07","Tropical_Arena_08","Tropical_Boss_01","Tropical_Boss_02","Tropical_Horde_01","Tropical_Horde_02","Tropical_Horde_03","Tropical_Horde_04","Tropical_Horde_05","Tropical_Horde_06","Tropical_Horde_07","Tropical_Parkour_01","Tropical_Shop_01","Arctic_Arena_01","Arctic_Arena_02","Arctic_Boss_01","Arctic_Boss_02","Arctic_Boss_03","Arctic_Horde_01","Arctic_Horde_02","Arctic_Horde_03","Arctic_Horde_04","Arctic_Horde_05","Arctic_Horde_06","Arctic_Horde_07","Arctic_Horde_08","Arctic_Parkour_01","Volcanic_Arena_01","Volcanic_Arena_02","Volcanic_Arena_03","Volcanic_Arena_04","Volcanic_Arena_05","Volcanic_Arena_06","Volcanic_Boss_01","Volcanic_Horde_01","Volcanic_Horde_02","Volcanic_Horde_03","Volcanic_Horde_04","Volcanic_Horde_05","CrabIsland","Lobby"]
            presetJSON["IslandName"] = islandName[scrollSelectMenu(prompt,islandName,startChoice=islandName.index(presetJSON["IslandName"]),loop=True,buffer_size=2)]
            
        elif(":" in info[choice] and "Loot Type" in info[choice][:info[choice].index(":")]):
            prompt = "Select Loot Type\nCurrent Loot Type is "+presetJSON["LootType"]
            lootType = ["Economy","Speed","Skill","Greed","Critical","Damage","Health","Elemental","Luck","Random","Upgrade","Random Loot Type"]
            presetJSON["LootType"] = lootType[scrollSelectMenu(prompt,lootType,startChoice=lootType.index(presetJSON["LootType"]))]
        
        elif(":" in info[choice] and "Island Type" in info[choice][:info[choice].index(":")]):
            prompt = "Select Loot Type\nCurrent Loot Type is "+presetJSON["IslandType"]
            lootType = ISLANDTYPE.copy()
            presetJSON["IslandType"] = lootType[scrollSelectMenu(prompt,lootType,startChoice=lootType.index(presetJSON["IslandType"]))]
            
        elif(":" in info[choice] and "Health" in info[choice][:info[choice].index(":")] and not "Max" in info[choice][:info[choice].index(":")] and not "Armor" in info[choice][:info[choice].index(":")] and not "Multiplier" in info[choice][:info[choice].index(":")]):
            presetJSON["Health"] = userInputMenuNum("Enter number for health\nEnter nothing to not change anything","",0,2147483647,default = presetJSON["Health"],useDefaultAsPreset=True)
            
        elif(":" in info[choice] and "Max Health" in info[choice][:info[choice].index(":")]):
            presetJSON["MaxHealth"] = userInputMenuNum("Enter number for max health\nEnter nothing to not change anything","",0,2147483647,default = presetJSON["MaxHealth"],useDefaultAsPreset=True)
            
        elif(":" in info[choice] and "Armor Plates" in info[choice][:info[choice].index(":")]):
            presetJSON["ArmorPlates"] = userInputMenuNum("Enter number for armor plates\nEnter nothing to not change anything","",-1,7,default = presetJSON["ArmorPlates"],useDefaultAsPreset=True)
            
        elif(":" in info[choice] and "Armor Plate Health" in info[choice][:info[choice].index(":")]):
            presetJSON["ArmorPlatesHealth"] = userInputMenuNum("Enter number for armor plate health\nEnter nothing to not change anything","",0,2147483647,default = presetJSON["ArmorPlatesHealth"],useDefaultAsPreset=True)
        
        elif(":" in info[choice] and "Health Multiplier" in info[choice][:info[choice].index(":")]):
            presetJSON["HealthMultiplier"] = userInputMenuNum("Enter number for health multiplier\nEnter nothing to not change anything","",0,2147483647,default = presetJSON["HealthMultiplier"],useDefaultAsPreset=True,decimal = True)
            
        elif(":" in info[choice] and "Damage Multiplier" in info[choice][:info[choice].index(":")]):
            presetJSON["DamageMultiplier"] = userInputMenuNum("Enter number for damage multiplier\nEnter nothing to not change anything","",0,2147483647,default = presetJSON["DamageMultiplier"],useDefaultAsPreset=True,decimal = True)
            
        elif(info[choice].replace(indent,"") in DiffModsWithDetails):
            diffmods = presetJSON["DiffMods"]
            diffmods.remove(info[choice].replace(indent,"")[:info[choice].replace(indent,"").index(" - ")])
            presetJSON["DiffMods"] = diffmods
            
        elif("Add Difficulty Modifer" in info[choice]):
            diffmods = DIFFMODS.copy()
            for diffmod in presetJSON["DiffMods"]:
                diffmods.remove(diffmod)
            prompt = "Select Difficulty Modifer to add\n"
            odiffmods = diffmods.copy()
            for i in range(len(diffmods)):
                diffmods[i] = diffmods[i]+" - "+DIFFMODSDETAILS[DIFFMODS.index(diffmods[i])]
            diffmod = odiffmods[scrollSelectMenu(prompt,diffmods)]
            odiffmods = presetJSON["DiffMods"]
            odiffmods.append(diffmod)
            presetJSON["DiffMods"] = odiffmods
                    
        elif(":" in info[choice] and "Weapon" in info[choice][:info[choice].index(":")] and not "Mod" in info[choice][:info[choice].index(":")]):
            prompt = "Select Weapon\nCurrent Weapon is "+presetJSON["Inventory"]["Weapon"]+"\n"
            wep = WEAPONS.copy()
            wep.append("Random Weapon")
            wep.append("Lobby Dependant")
            presetJSON["Inventory"]["Weapon"] = wep[scrollSelectMenu(prompt,wep,startChoice=wep.index(presetJSON["Inventory"]["Weapon"]))]
            
        elif(":" in info[choice] and "Weapon Mod Slots" in info[choice][:info[choice].index(":")]):
            presetJSON["Inventory"]["WeaponMods"]["Slots"] = userInputMenuNum("Enter number for weapon mod slots\nEnter nothing to not change anything","",-1,65,default = presetJSON["Inventory"]["WeaponMods"]["Slots"],useDefaultAsPreset=True)
            
        elif(":" in info[choice] and "Grenade Mod Slots" in info[choice][:info[choice].index(":")]):
            presetJSON["Inventory"]["GrenadeMods"]["Slots"] = userInputMenuNum("Enter number for grenade mod slots\nEnter nothing to not change anything","",-1,65,default = presetJSON["Inventory"]["GrenadeMods"]["Slots"],useDefaultAsPreset=True)
            
        elif(":" in info[choice] and "Perk Slots" in info[choice][:info[choice].index(":")]):
            presetJSON["Inventory"]["Perks"]["Slots"] = userInputMenuNum("Enter number for perk slots\nEnter nothing to not change anything","",-1,65,default = presetJSON["Inventory"]["Perks"]["Slots"],useDefaultAsPreset=True)
        
        elif(":" in info[choice] and "Key Totem" in info[choice][:info[choice].index(":")]):
            if(presetJSON["keyTotemItem"]):
                presetJSON["keyTotemItem"] = False
            else:
                presetJSON["keyTotemItem"] = True
            
        elif(containsWepMod(info[choice])[0]):
            wepMod = containsWepMod(info[choice])[1]
            array = presetJSON["Inventory"]["WeaponMods"]["Mods"]
            for i in range(len(array)):
                #print(str(array[i].replace("'","\"")))
                if(wepMod == json.loads(str(array[i]).replace("'","\""))["Name"]):
                    array.remove(array[i])
                    break
            presetJSON["Inventory"]["WeaponMods"]["Mods"] = array
            
        elif("Add Weapon Mod" in info[choice]):
            wepmods = WEAPONMODS["Names"].copy()
            for wepmod in presetJSON["Inventory"]["WeaponMods"]["Mods"]:
                wepmods.remove(json.loads(str(wepmod).replace("'","\""))["Name"])
            prompt = "Select Weapon Mod to add\n"
            owepmods = wepmods.copy()
            # for i in range(len(wepmods)):
            #     wepmods[i] = wepmods[i]
            wepmods.insert(0,"Back")
            while True:
                wepmod = scrollSelectMenu(prompt,wepmods,useItemColors=True,loop=True)
                if(wepmod == 0):
                    break
                wepmod = owepmods[wepmod-1]
                lvl = userInputMenuNum("What level should "+str(wepmod)+" be?\nEnter nothing to select a differnt weapon mod","",0,256,"",)
                if(lvl == ""):
                    continue
                lvl = int(lvl)
                mods = presetJSON["Inventory"]["WeaponMods"]["Mods"]
                mod = json.loads("{}")
                mod["Name"] = wepmod
                mod["Rarity"] = WEAPONMODS[wepmod]
                mod["Level"] = lvl
                mods.append(mod)
                presetJSON["Inventory"]["WeaponMods"]["Mods"] = mods
                break        
            
        elif(containsGreMod(info[choice])[0]):
            gremod = containsGreMod(info[choice])[1]
            array = presetJSON["Inventory"]["GrenadeMods"]["Mods"]
            for i in range(len(array)):
                #print(str(array[i].replace("'","\"")))
                if(gremod == json.loads(str(array[i]).replace("'","\""))["Name"]):
                    array.remove(array[i])
                    break
            presetJSON["Inventory"]["GrenadeMods"]["Mods"] = array
            
        elif("Add Grenade Mod" in info[choice]):
            gremods = GRENADEMODS["Names"].copy()
            for gremod in presetJSON["Inventory"]["GrenadeMods"]["Mods"]:
                gremods.remove(json.loads(str(gremod).replace("'","\""))["Name"])
            prompt = "Select Grenade Mod to add\n"
            ogremods = gremods.copy()
            # for i in range(len(gremods)):
            #     gremods[i] = gremods[i]
            gremods.insert(0,"Back")
            while True:
                gremod = scrollSelectMenu(prompt,gremods,useItemColors=True,loop=True)
                if(gremod == 0):
                    break
                gremod = ogremods[gremod-1]
                lvl = userInputMenuNum("What level should "+str(gremod)+" be?\nEnter nothing to select a differnt grenade mod","",0,256,"",)
                if(lvl == ""):
                    continue
                lvl = int(lvl)
                mods = presetJSON["Inventory"]["GrenadeMods"]["Mods"]
                mod = json.loads("{}")
                mod["Name"] = gremod
                mod["Rarity"] = GRENADEMODS[gremod]
                mod["Level"] = lvl
                mods.append(mod)
                presetJSON["Inventory"]["GrenadeMods"]["Mods"] = mods
                break
            
        elif(containsPerk(info[choice])[0]):
            gremod = containsPerk(info[choice])[1]
            array = presetJSON["Inventory"]["Perks"]["Perks"]
            for i in range(len(array)):
                #print(str(array[i].replace("'","\"")))
                if(gremod == json.loads(str(array[i]).replace("'","\""))["Name"]):
                    array.remove(array[i])
                    break
            presetJSON["Inventory"]["Perks"]["Perks"] = array
                
        elif("Add Perk" in info[choice]):
            perks = PERKS["Names"].copy()
            for perk in presetJSON["Inventory"]["Perks"]["Perks"]:
                perks.remove(json.loads(str(perk).replace("'","\""))["Name"])
            prompt = "Select Perk to add\n"
            operks = perks.copy()
            # for i in range(len(perks)):
            #     perks[i] = perks[i]
            perks.insert(0,"Back")
            while True:
                perk = scrollSelectMenu(prompt,perks,useItemColors=True,loop=True)
                if(perk == 0):
                    break
                perk = operks[perk-1]
                lvl = userInputMenuNum("What level should "+str(perk)+" be?\nEnter nothing to select a differnt perk","",0,256,"",)
                if(lvl == ""):
                    continue
                lvl = int(lvl)
                mods = presetJSON["Inventory"]["Perks"]["Perks"]
                mod = json.loads("{}")
                mod["Name"] = perk
                mod["Rarity"] = PERKS[perk]
                mod["Level"] = lvl
                mods.append(mod)
                presetJSON["Inventory"]["Perks"]["Perks"] = mods
                break
        elif(choice == 0):
            if(os.path.exists(owd+"/CrabChampionSaveManager/Presets/"+name+".ccsm") and (not overriade or (overriade and oname != name))):
                perm = yornMenu("There is already a preset by that name, Overwrite")
                if(perm):
                    break
            else:
                break
    presetJSON
    
    f = open(owd+"/CrabChampionSaveManager/Presets/"+name+".ccsm","w")
    f.write(json.dumps(presetJSON,indent=4))
    f.close()
    
    if(oname != name):
        os.remove(owd+"/CrabChampionSaveManager/Presets/"+oname+".ccsm")
    
def usePreset():
    global presetsJSON
    loadPresets()
    foldersInfo = getPresets(moreInfo=1)
    presetss = getPresets()
    prompt = "Select Preset to use\n"
    presets = "Back\n"
    for i,name in enumerate(foldersInfo):
        if(i == 0):
            presets += str(name)
        else:
            presets += "\n"+str(name)
            
    choice = scrollSelectMenu(prompt,presets,wrapMode=2,detailsSelected = False)
    if(choice == 0):
        return
    choice -=1
    
    presetJSON = presetsJSON[presetss[choice]]
    
    GameJSON = convertPresetToGameSave(presetJSON)
    
    saveGame = os.path.join(os.getcwd(), "SaveGames")
    uesavePath = getUesavePath()
    if(uesavePath == ""):
        scrollInfoMenu("No copy of uesave could be found and no permission was given to download a copy\nPress Enter to return to main menu")
        return
    saveGame+="/SaveSlot.sav"
    saveGame = saveGame.replace("\\","/")
    saveGame = "\""+saveGame+"\""
    infoScreen("0/8")
    proc1 = subprocess.Popen(uesavePath+" to-json -i "+saveGame+" -o currentSave.json",shell=True)
    infoScreen("1/8")
    proc1.wait()
    with open("currentSave.json") as JSON_File:
        saveJSON = json.load(JSON_File)
    os.remove("currentSave.json")
    infoScreen("2/8")
    backupJSON = GameJSON 
    infoScreen("4/8")
    try:
        saveJSON["root"]["properties"]["AutoSave"] = GameJSON["AutoSave"]
    except Exception as error:
        scrollInfoMenu("Error when replacing autosave on current save, Error below\n"+str(error)+"\nPress Enter to return to main menu")
        input("Press Enter to continue . . .")
        return
    infoScreen("5/8")
    with open("usedPreset.json","w") as JSON_File:
        JSON_File.write(json.dumps(saveJSON, indent=4))
    infoScreen("6/8")
    proc1 = subprocess.Popen(uesavePath+" from-json -i usedPreset.json -o SaveGames/SaveSlot.sav", shell=True)
    proc1.wait()
    os.remove("usedPreset.json")
    infoScreen("7/8")
    #proc2.wait()
    shutil.copyfile("SaveGames/SaveSlot.sav","SaveGames/SaveSlotBackupA.sav")
    shutil.copyfile("SaveGames/SaveSlot.sav","SaveGames/SaveSlotBackupB.sav")
    infoScreen("8/8")
    stop = time.time()
    #print("it took",round(stop-start,3)," seconds")
    return
    
    
    f = open("game.json","w")
    f.write(json.dumps(GameJSON,indent=4))
    f.close()
        
def editPresetMenu():  
    loadPresets()
    foldersInfo = getPresets(moreInfo=1)
    presetss = getPresets()
    prompt = "Select preset to edit\n"
    presets = "Back\n"
    for i,name in enumerate(foldersInfo):
        if(i == 0):
            presets += str(name)
        else:
            presets += "\n"+str(name)
            
    choice = scrollSelectMenu(prompt,presets,wrapMode=2,detailsSelected = False)
    if(choice == 0):
        return
    choice -=1
    presetJSON = presetsJSON[presetss[choice]]
    editPreset(presetJSON,presetss[choice],overriade=True)
    
def getUnlocked():
    global WEAPONMODS
    global GRENADEMODS
    global PERKS
    global WEAPONS
    global cacheJSON
    loadCache()
        #in cache json
    #XP to next level up           - ["XPToNextLevelUp"]
    #Weapon Rank Array             - ["RankedWeapons"]
    #    Weapon Name From Array    - ["RankedWeapons"][index]["Name"]
    #    Weapon Rank From Array    - ["RankedWeapons"][index]["Rank"]
    #Account Level                 - ["AccountLevel"]
    #Keys                          - ["Keys"]
    #Crab Skin                     - ["Skin"]
    #Current Weapon                - ["CurrentWeapon"]
    #Challenages Array             - ["Challenges"]
    #    Name                      - ["Challenges"][index]["Name"]
    #    Description               - ["Challenges"][index]["Description"]
    #    Progress                  - ["Challenges"][index]["Progress"]
    #    Goal                      - ["Challenges"][index]["Goal"]
    #    Completed                 - ["Challenges"][index]["Completed"]
    #    Cosmetic Reward Name      - ["Challenges"][index]["SkinRewardName"]
    #Unlocked Weapons Array        - ["UnlockedWeapons"]
    #Unlocked Weapon Mods Array    - ["UnlockedWeaponMods"]
    #Unlocked Grenade Mods Array   - ["UnlockedGrenadeMods"]
    #Unlocked Perks Array          - ["UnlockedPerks"]
    WEAPONS = []
    for wep in cacheJSON["PlayerData"]["UnlockedWeapons"]:
        WEAPONS.append(wep)
    WEAPONS 
    WEAPONMODS = json.loads("{}") 
    rare = []
    epic = []
    leg = []
    greed = []
    names = []

    #print((cacheJSON["PlayerData"]["UnlockedWeaponMods"]))
    for wepMod in cacheJSON["PlayerData"]["UnlockedWeaponMods"]:
        wepMod = str(wepMod).replace("'","\"")
        wepMod = json.loads(wepMod)
        WEAPONMODS[wepMod["Name"]] = wepMod["Rarity"]
        names.append(wepMod["Name"])
        if(wepMod["Rarity"] == "Rare"):
            rare.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Epic"):
            epic.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Legendary"):
            leg.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Greed"):
            greed.append(wepMod["Name"])
    rare.sort()
    epic.sort()
    leg.sort()
    greed.sort()
    WEAPONMODS["Rare"] = rare
    WEAPONMODS["Epic"] = epic
    WEAPONMODS["Legendary"] = leg
    WEAPONMODS["Greed"] = greed
    names = []
    names.extend(rare)
    names.extend(epic)
    names.extend(leg)
    names.extend(greed)
    WEAPONMODS["Names"] = names
    # f = open("wepMod.json","w")
    # f.write(json.dumps(WEAPONMODS,indent=4))
    # f.close()
    
    
    GRENADEMODS = json.loads("{}") 
    rare = []
    epic = []
    leg = []
    greed = []
    names = []

    #print((cacheJSON["PlayerData"]["UnlockedWeaponMods"]))
    for wepMod in cacheJSON["PlayerData"]["UnlockedGrenadeMods"]:
        wepMod = str(wepMod).replace("'","\"")
        wepMod = json.loads(wepMod)
        GRENADEMODS[wepMod["Name"]] = wepMod["Rarity"]
        names.append(wepMod["Name"])
        if(wepMod["Rarity"] == "Rare"):
            rare.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Epic"):
            epic.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Legendary"):
            leg.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Greed"):
            greed.append(wepMod["Name"])
    rare.sort()
    epic.sort()
    leg.sort()
    greed.sort()
    names = []
    names.extend(rare)
    names.extend(epic)
    names.extend(leg)
    names.extend(greed)
    GRENADEMODS["Rare"] = rare
    GRENADEMODS["Epic"] = epic
    GRENADEMODS["Legendary"] = leg
    GRENADEMODS["Greed"] = greed
    GRENADEMODS["Names"] = names
    # f = open("greMod.json","w")
    # f.write(json.dumps(GRENADEMODS,indent=4))
    # f.close()
    
    
    PERKS = json.loads("{}") 
    rare = []
    epic = []
    leg = []
    greed = []
    names = []

    #print((cacheJSON["PlayerData"]["UnlockedWeaponMods"]))
    for wepMod in cacheJSON["PlayerData"]["UnlockedPerks"]:
        wepMod = str(wepMod).replace("'","\"")
        wepMod = json.loads(wepMod)
        PERKS[wepMod["Name"]] = wepMod["Rarity"]
        names.append(wepMod["Name"])
        if(wepMod["Rarity"] == "Rare"):
            rare.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Epic"):
            epic.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Legendary"):
            leg.append(wepMod["Name"])
        elif(wepMod["Rarity"] == "Greed"):
            greed.append(wepMod["Name"])
            
    rare.sort()
    epic.sort()
    leg.sort()
    greed.sort()
    names = []
    names.extend(rare)
    names.extend(epic)
    names.extend(leg)
    names.extend(greed)
    PERKS["Rare"] = rare
    PERKS["Epic"] = epic
    PERKS["Legendary"] = leg
    PERKS["Greed"] = greed
    PERKS["Names"] = names
    # f = open("perk.json","w")
    # f.write(json.dumps(PERKS,indent=4))
    # f.close()
            
def containsWepMod(string):
    for wepmod in WEAPONMODS["Names"]:
        if(wepmod in string):
            return True , wepmod
    return False , None  

def containsGreMod(string):
    for greMod in GRENADEMODS["Names"]:
        if(greMod in string):
            return True , greMod
    return False , None 

def containsPerk(string):
    for perk in PERKS["Names"]:
        if(perk in string):
            return True , perk
    return False , None 

def convertMyItemtoGameItem(MyItemJson):
    WeaponModJSON = "{\"Struct\":{\"WeaponModDA\":{\"Object\":{\"value\":\"\"}},\"Level\":{\"Byte\":{\"value\":{\"Byte\":0},\"enum_type\":\"None\"}}}}"
    GrenadeModJSON = "{\"Struct\":{\"GrenadeModDA\":{\"Object\":{\"value\":\"\"}},\"Level\":{\"Byte\":{\"value\":{\"Byte\":0},\"enum_type\":\"None\"}}}}"
    PerkJSON = "{\"Struct\":{\"PerkDA\":{\"Object\":{\"value\":\"\"}},\"Level\":{\"Byte\":{\"value\":{\"Byte\":0},\"enum_type\":\"None\"}}}}"

    #/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_AuraShot.DA_WeaponMod_AuraShot


    MyItemJson = json.loads(str(MyItemJson).replace("'","\""))
    
    
    if(MyItemJson["Name"] in WEAPONMODS["Names"]):
        GameItemJson = json.loads(WeaponModJSON)
        name = f"/Game/Blueprint/Pickup/WeaponMod/{MyItemJson['Rarity']}/DA_WeaponMod_{MyItemJson['Name'].replace(' ','')}.DA_WeaponMod_{MyItemJson['Name'].replace(' ','')}"
        GameItemJson["Struct"]["WeaponModDA"]["Object"]["value"] = name
        GameItemJson["Struct"]["Level"]["Byte"]["value"]["Byte"] = MyItemJson["Level"]
        return GameItemJson
    elif(MyItemJson["Name"] in GRENADEMODS["Names"]):
        GameItemJson = json.loads(GrenadeModJSON)
        name = f"/Game/Blueprint/Pickup/GrenadeMod/{MyItemJson['Rarity']}/DA_GrenadeMod_{MyItemJson['Name'].replace(' ','')}.DA_GrenadeMod_{MyItemJson['Name'].replace(' ','')}"
        GameItemJson["Struct"]["GrenadeModDA"]["Object"]["value"] = name
        GameItemJson["Struct"]["Level"]["Byte"]["value"]["Byte"] = MyItemJson["Level"]
        return GameItemJson
    elif(MyItemJson["Name"] in PERKS["Names"]):
        GameItemJson = json.loads(PerkJSON)
        name = f"/Game/Blueprint/Pickup/Perk/{MyItemJson['Rarity']}/DA_Perk_{MyItemJson['Name'].replace(' ','')}.DA_Perk_{MyItemJson['Name'].replace(' ','')}"
        GameItemJson["Struct"]["PerkDA"]["Object"]["value"] = name
        GameItemJson["Struct"]["Level"]["Byte"]["value"]["Byte"] = MyItemJson["Level"]
        return GameItemJson

def convertPresetToGameSave(preset):
    GameJSON = "{\"AutoSave\":{\"Struct\":{\"value\":{\"Struct\":{\"Difficulty\":{\"Enum\":{\"value\":\"ECrabDifficulty::Normal\",\"enum_type\":\"ECrabDifficulty\"}},\"DifficultyModifiers\":{\"Array\":{\"array_type\":\"EnumProperty\",\"value\":{\"Base\":{\"Enum\":[]}}}},\"NextIslandInfo\":{\"Struct\":{\"value\":{\"Struct\":{\"Biome\":{\"Enum\":{\"value\":\"ECrabBiome::Tropical\",\"enum_type\":\"ECrabBiome\"}},\"CurrentIsland\":{\"Int\":{\"value\":1}},\"IslandName\":{\"Name\":{\"value\":\"Tropical_Arena_01\"}},\"IslandType\":{\"Enum\":{\"value\":\"ECrabIslandType::Arena\",\"enum_type\":\"ECrabIslandType\"}},\"RewardLootPool\":{\"Enum\":{\"value\":\"ECrabLootPool::Random\",\"enum_type\":\"ECrabLootPool\"}}}},\"struct_type\":{\"Struct\":\"CrabNextIslandInfo\"},\"struct_id\":\"00000000-0000-0000-0000-000000000000\"}},\"HealthInfo\":{\"Struct\":{\"value\":{\"Struct\":{\"CurrentArmorPlates\":{\"Int\":{\"value\":0}},\"CurrentArmorPlateHealth\":{\"Float\":{\"value\":0}},\"CurrentHealth\":{\"Float\":{\"value\":100}},\"CurrentMaxHealth\":{\"Float\":{\"value\":100}}}},\"struct_type\":{\"Struct\":\"CrabHealthInfo\"},\"struct_id\":\"00000000-0000-0000-0000-000000000000\"}},\"HealthMultiplier\":{\"Float\":{\"value\":1}},\"DamageMultiplier\":{\"Float\":{\"value\":1}},\"WeaponDA\":{\"Object\":{\"value\":\"\"}},\"NumWeaponModSlots\":{\"Byte\":{\"value\":{\"Byte\":24},\"enum_type\":\"None\"}},\"WeaponMods\":{\"Array\":{\"array_type\":\"StructProperty\",\"value\":{\"Struct\":{\"_type\":\"WeaponMods\",\"name\":\"StructProperty\",\"struct_type\":{\"Struct\":\"CrabWeaponMod\"},\"id\":\"00000000-0000-0000-0000-000000000000\",\"value\":[]}}}},\"NumGrenadeModSlots\":{\"Byte\":{\"value\":{\"Byte\":24},\"enum_type\":\"None\"}},\"GrenadeMods\":{\"Array\":{\"array_type\":\"StructProperty\",\"value\":{\"Struct\":{\"_type\":\"GrenadeMods\",\"name\":\"StructProperty\",\"struct_type\":{\"Struct\":\"CrabGrenadeMod\"},\"id\":\"00000000-0000-0000-0000-000000000000\",\"value\":[]}}}},\"NumPerkSlots\":{\"Byte\":{\"value\":{\"Byte\":24},\"enum_type\":\"None\"}},\"Perks\":{\"Array\":{\"array_type\":\"StructProperty\",\"value\":{\"Struct\":{\"_type\":\"Perks\",\"name\":\"StructProperty\",\"struct_type\":{\"Struct\":\"CrabPerk\"},\"id\":\"00000000-0000-0000-0000-000000000000\",\"value\":[]}}}},\"Crystals\":{\"UInt32\":{\"value\":0}}}},\"struct_type\":{\"Struct\":\"CrabAutoSave\"},\"struct_id\":\"00000000-0000-0000-0000-000000000000\"}}}"
    GameJSON = json.loads(GameJSON)
    #saveJSON = saveJSON["AutoSave"]
    #difficulty                ["Difficulty"]["Enum"]["value"] , vaild values are ECrabDifficulty::Easy and ECrabDifficulty::Nightmare , it seems that for normal, the value is not there, this suggests the games uses normal as a default and this value in the .sav file is an override 
    #island num                ["NextIslandInfo"]["Struct"]["value"]["Struct"]["CurrentIsland"]["Int"]["value"]
    # diff mods                ["DifficultyModifiers"]["Array"]["value"]["Base"]["Enum"]
    # Crystals                 ["Crystals"]["UInt32"]["value"]
    # Biome                    ["NextIslandInfo"]["Struct"]["value"]["Struct"]["Biome"]["Enum"]["value"]
    # Loot Type                ["NextIslandInfo"]["Struct"]["value"]["Struct"]["RewardLootPool"]["Enum"]["value"]
    # island name              ["NextIslandInfo"]["Struct"]["value"]["Struct"]["IslandName"]["Name"]["value"]
    # Health                   ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentHealth"]["Float"]["value"]
    # Max Health               ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentMaxHealth"]["Float"]["value"]
    # Armor Plates             ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlates"]["Int"]["value"]
    # Armor Plate Health       ["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlateHealth"]["Float"]["value"]
    # HealthMultiplier         ["HealthMultiplier"]["Float"]["value"]
    # DamageMultiplier         ["DamageMultiplier"]["Float"]["value"]
    
    #Weapon                    ["WeaponDA"]["Object"]["value"]  -  use parseWeapon() to get proper name
    
    #Items
    #Weapon Mod Slots           ["NumWeaponModSlots"]["Byte"]["value"]["Byte"]
    #Weapon Mod Array           ["WeaponMods"]["Array"]["value"]["Struct"]["value"]
    #Weapon Mod in array item   ["Struct"]["WeaponModDA"]["Object"]["value"] - use parseWeaponMod() to get parsed and formated name 
    #Weapon Mod in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]
    
    #Grenade Mod Slots           ["NumGrenadeModSlots"]["Byte"]["value"]["Byte"]
    #Grenade Mod Array           ["GrenadeMods"]["Array"]["value"]["Struct"]["value"]
    #Grenade Mod in array item   ["Struct"]["GrenadeModDA"]["Object"]["value"] - use parseGrenadeMod() to get parsed and formated name 
    #Grenade Mod in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]

    #Perk Slots           ["NumPerkSlots"]["Byte"]["value"]["Byte"]
    #Perk Array           ["Perks"]["Array"]["value"]["Struct"]["value"]
    #Perk in array item   ["Struct"]["PerkDA"]["Object"]["value"] - use parsePerk() to get parsed and formated name 
    #Perk in array Level  ["Struct"]["Level"]["Byte"]["value"]["Byte"]
    #print(GameJSON.keys())
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NextIslandInfo"]["Struct"]["value"]["Struct"]["CurrentIsland"]["Int"]["value"] = preset["IslandNum"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["Crystals"]["UInt32"]["value"] = preset["Crystals"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["Difficulty"]["Enum"]["value"] = "ECrabDifficulty::"+preset["Diff"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NextIslandInfo"]["Struct"]["value"]["Struct"]["Biome"]["Enum"]["value"] = "ECrabBiome::"+preset["Biome"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NextIslandInfo"]["Struct"]["value"]["Struct"]["IslandName"]["Name"]["value"] = dynamicIslandName(preset["IslandName"])
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NextIslandInfo"]["Struct"]["value"]["Struct"]["RewardLootPool"]["Enum"]["value"] = "ECrabLootPool::"+dynamicLootType(preset["LootType"])
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NextIslandInfo"]["Struct"]["value"]["Struct"]["IslandType"]["Enum"]["value"] = "ECrabIslandType::"+dynamicIslandType(preset["IslandType"],preset["IslandName"])
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentHealth"]["Float"]["value"] = preset["Health"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentMaxHealth"]["Float"]["value"] = preset["MaxHealth"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlates"]["Int"]["value"] = preset["ArmorPlates"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["HealthInfo"]["Struct"]["value"]["Struct"]["CurrentArmorPlateHealth"]["Float"]["value"] = preset["ArmorPlatesHealth"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["HealthMultiplier"]["Float"]["value"] = preset["HealthMultiplier"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["DamageMultiplier"]["Float"]["value"] = preset["DamageMultiplier"]
    array = []
    for dif in preset["DiffMods"]:
        array.append("ECrabDifficultyModifier::"+dif.replace(" ",""))
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["DifficultyModifiers"]["Array"]["value"]["Base"]["Enum"] = array
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["WeaponDA"]["Object"]["value"] = dynamicWeapon(preset["Inventory"]["Weapon"])
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NumWeaponModSlots"]["Byte"]["value"]["Byte"] = preset["Inventory"]["WeaponMods"]["Slots"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NumGrenadeModSlots"]["Byte"]["value"]["Byte"] = preset["Inventory"]["GrenadeMods"]["Slots"]
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["NumPerkSlots"]["Byte"]["value"]["Byte"] = preset["Inventory"]["Perks"]["Slots"]
    
    keyItem = False
    if(preset["keyTotemItem"]):
        keyItem = getKeyTotemItem()
    
    
    array = []
    for wepMod in preset["Inventory"]["WeaponMods"]["Mods"]:
        wepMod = json.loads(str(wepMod).replace("'","\""))
        array.append(convertMyItemtoGameItem(wepMod))
    if(keyItem and keyItem in WEAPONMODS["Names"]):
        keyItemJSON = json.loads("{\"Name\":\"\",\"Rarity\":\"\",\"Level\":1}")
        keyItemJSON["Name"] = keyItem
        keyItemJSON["Rarity"] = WEAPONMODS[keyItem]
        array.append(convertMyItemtoGameItem(keyItemJSON))
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["WeaponMods"]["Array"]["value"]["Struct"]["value"] = array

    array = []
    for wepMod in preset["Inventory"]["GrenadeMods"]["Mods"]:
        wepMod = json.loads(str(wepMod).replace("'","\""))
        array.append(convertMyItemtoGameItem(wepMod))
    if(keyItem and keyItem in GRENADEMODS["Names"]):
        keyItemJSON = json.loads("{\"Name\":\"\",\"Rarity\":\"\",\"Level\":1}")
        keyItemJSON["Name"] = keyItem
        keyItemJSON["Rarity"] = GRENADEMODS[keyItem]
        array.append(convertMyItemtoGameItem(keyItemJSON))
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["GrenadeMods"]["Array"]["value"]["Struct"]["value"] = array
    
    array = []
    for wepMod in preset["Inventory"]["Perks"]["Perks"]:
        wepMod = json.loads(str(wepMod).replace("'","\""))
        array.append(convertMyItemtoGameItem(wepMod))
    if(keyItem and keyItem in PERKS["Names"]):
        keyItemJSON = json.loads("{\"Name\":\"\",\"Rarity\":\"\",\"Level\":1}")
        keyItemJSON["Name"] = keyItem
        keyItemJSON["Rarity"] = PERKS[keyItem]
        array.append(convertMyItemtoGameItem(keyItemJSON))
    GameJSON["AutoSave"]["Struct"]["value"]["Struct"]["Perks"]["Array"]["value"]["Struct"]["value"] = array
    
    return GameJSON

def dynamicLootType(lootType):
    Types = ["Critical","Damage","Economy","Elemental","Greed","Health","Luck","Random","Skill","Speed","Upgrade"]
    if(lootType in Types):
        return lootType
    else:
        return Types[random.randint(0,len(Types))]
    
def dynamicIslandName(name):
    global ISLANDS
    
    try:
        options = ISLANDS[name]
        return options[random.randint(0,len(options)-1)]
    except:
        return name
        
def setUpIslands():
    global ISLANDS
    #["Tropical Arena Island","Tropical Horde Island","Tropical Elite Island","Tropical Parkour Island","Arctic Arena Island","Arctic Horde Island","Arctic Elite Island","Arctic Parkour Island","Volcanic Arena Island","Volcanic Horde Island","Volcanic Boss Island","Tropical_Arena_01","Tropical_Arena_02","Tropical_Arena_03","Tropical_Arena_04","Tropical_Arena_05","Tropical_Arena_06","Tropical_Arena_07","Tropical_Arena_08","Tropical_Boss_01","Tropical_Boss_02","Tropical_Horde_01","Tropical_Horde_02","Tropical_Horde_03","Tropical_Horde_04","Tropical_Horde_05","Tropical_Horde_06","Tropical_Horde_07","Tropical_Parkour_01","Tropical_Shop_01","Arctic_Arena_01","Arctic_Arena_02","Arctic_Boss_01","Arctic_Boss_02","Arctic_Boss_03","Arctic_Horde_01","Arctic_Horde_02","Arctic_Horde_03","Arctic_Horde_04","Arctic_Horde_05","Arctic_Horde_06","Arctic_Horde_07","Arctic_Horde_08","Arctic_Parkour_01","Volcanic_Arena_01","Volcanic_Arena_02","Volcanic_Arena_03","Volcanic_Arena_04","Volcanic_Arena_05","Volcanic_Arena_06","Volcanic_Boss_01","Volcanic_Horde_01","Volcanic_Horde_02","Volcanic_Horde_03","Volcanic_Horde_04","Volcanic_Horde_05","CrabIsland","Lobby"]
    ISLANDS = json.loads("{}")
    ISLANDS["Tropical"] = ["Tropical_Arena_01","Tropical_Arena_02","Tropical_Arena_03","Tropical_Arena_04","Tropical_Arena_05","Tropical_Arena_06","Tropical_Arena_07","Tropical_Arena_08","Tropical_Boss_01","Tropical_Boss_02","Tropical_Horde_01","Tropical_Horde_02","Tropical_Horde_03","Tropical_Horde_04","Tropical_Horde_05","Tropical_Horde_06","Tropical_Horde_07","Tropical_Parkour_01","Tropical_Shop_01"]
    
    ISLANDS["Arctic"] = ["Arctic_Arena_01","Arctic_Arena_02","Arctic_Boss_01","Arctic_Boss_02","Arctic_Boss_03","Arctic_Horde_01","Arctic_Horde_02","Arctic_Horde_03","Arctic_Horde_04","Arctic_Horde_05","Arctic_Horde_06","Arctic_Horde_07","Arctic_Horde_08","Arctic_Parkour_01"]
    
    ISLANDS["Volcanic"] = ["Volcanic_Arena_01","Volcanic_Arena_02","Volcanic_Arena_03","Volcanic_Arena_04","Volcanic_Arena_05","Volcanic_Arena_06","Volcanic_Boss_01","Volcanic_Horde_01","Volcanic_Horde_02","Volcanic_Horde_03","Volcanic_Horde_04","Volcanic_Horde_05"]
    
    ISLANDS["All"] = ["Tropical_Arena_01","Tropical_Arena_02","Tropical_Arena_03","Tropical_Arena_04","Tropical_Arena_05","Tropical_Arena_06","Tropical_Arena_07","Tropical_Arena_08","Tropical_Boss_01","Tropical_Boss_02","Tropical_Horde_01","Tropical_Horde_02","Tropical_Horde_03","Tropical_Horde_04","Tropical_Horde_05","Tropical_Horde_06","Tropical_Horde_07","Tropical_Parkour_01","Tropical_Shop_01","Arctic_Arena_01","Arctic_Arena_02","Arctic_Boss_01","Arctic_Boss_02","Arctic_Boss_03","Arctic_Horde_01","Arctic_Horde_02","Arctic_Horde_03","Arctic_Horde_04","Arctic_Horde_05","Arctic_Horde_06","Arctic_Horde_07","Arctic_Horde_08","Arctic_Parkour_01","Volcanic_Arena_01","Volcanic_Arena_02","Volcanic_Arena_03","Volcanic_Arena_04","Volcanic_Arena_05","Volcanic_Arena_06","Volcanic_Boss_01","Volcanic_Horde_01","Volcanic_Horde_02","Volcanic_Horde_03","Volcanic_Horde_04","Volcanic_Horde_05","CrabIsland","Lobby"]
    
    ISLANDS["Tropical Arena Island"] = ["Tropical_Arena_01","Tropical_Arena_02","Tropical_Arena_03","Tropical_Arena_04","Tropical_Arena_05","Tropical_Arena_06","Tropical_Arena_07","Tropical_Arena_08"]
    ISLANDS["Tropical Horde Island"] = ["Tropical_Horde_01","Tropical_Horde_02","Tropical_Horde_03","Tropical_Horde_04","Tropical_Horde_05","Tropical_Horde_06","Tropical_Horde_07"]
    ISLANDS["Tropical Elite Island"] = ["Tropical_Boss_01","Tropical_Boss_02"]
    ISLANDS["Tropical Parkour Island"] = ["Tropical_Parkour_01"]
    ISLANDS["Shop"] = ["Tropical_Shop_01"]
    
    ISLANDS["Arctic Arena Island"] = ["Arctic_Arena_01","Arctic_Arena_02"]
    ISLANDS["Arctic Horde Island"] = ["Arctic_Horde_01","Arctic_Horde_02","Arctic_Horde_03","Arctic_Horde_04","Arctic_Horde_05","Arctic_Horde_06","Arctic_Horde_07","Arctic_Horde_08"]
    ISLANDS["Arctic Elite Island"] = ["Arctic_Boss_01","Arctic_Boss_02","Arctic_Boss_03"]
    ISLANDS["Arctic Parkour Island"] = ["Arctic_Parkour_01"]
    
    ISLANDS["Volcanic Arena Island"] = ["Volcanic_Arena_01","Volcanic_Arena_02","Volcanic_Arena_03","Volcanic_Arena_04","Volcanic_Arena_05","Volcanic_Arena_06"]
    ISLANDS["Volcanic Horde Island"] = ["Volcanic_Horde_01","Volcanic_Horde_02","Volcanic_Horde_03","Volcanic_Horde_04","Volcanic_Horde_05"]
    ISLANDS["Volcanic Boss Island"] = ["Volcanic_Boss_01"]
    
    ISLANDS["Other"] = ["CrabIsland","Lobby"]
    
def dynamicWeapon(wep):
    if(wep == "Lobby Dependant"):
        return ""
    if( wep in WEAPONS):
        return f"/Game/Blueprint/Weapon/{wep.replace(' ','')}/DA_Weapon_{wep.replace(' ','')}.DA_Weapon_{wep.replace(' ','')}"
    else:
        return dynamicWeapon(WEAPONS[random.randint(0,len(WEAPONS)-1)])
      
def updatePreset(preset):
    try:
        preset["IslandType"]
    except:
        preset["IslandType"] = "Automatic"
    
    try:
        preset["HealthMultiplier"]
    except:
        preset["HealthMultiplier"] = 1.0
        
    try:
        preset["DamageMultiplier"]
    except:
        preset["DamageMultiplier"] = 1.0
        
    try:
        preset["keyTotemItem"]
    except:
        preset["keyTotemItem"] = False
    
    return preset
    
def dynamicIslandType(islandType,islandName):
    global ISLANDTYPE
    
    if(islandType == "Automatic"):
        if("arena" in islandName.lower()):
            return "Arena"
        elif("horde" in islandName.lower()):
            return "Horde"
        elif("parkour" in islandName.lower()):
            return "Parkour"
        elif("shop" in islandName.lower()):
            return "Shop"
        elif("boss" in islandName.lower() and ("tropical" in islandName.lower() or "arctic" in islandName.lower())):
            return "Elite"
        elif("boss" in islandName.lower()):
            return "Boss"
        elif("crabisland" in islandName.lower()):
            return "CrabIsland"
        
    else:
        return ISLANDTYPE[ISLANDTYPE.index(islandType)]

def getKeyTotemItem():
    itemType = random.randint(0,2)
    rare = random.randint(0,1)
    if(itemType == 0):
        if(rare == 0):
            return WEAPONMODS["Epic"][random.randint(0,len(WEAPONMODS["Epic"])-1)]
        elif(rare == 1):
            return WEAPONMODS["Legendary"][random.randint(0,len(WEAPONMODS["Legendary"])-1)]
    elif(itemType == 1):
        if(rare == 0):
            return GRENADEMODS["Epic"][random.randint(0,len(GRENADEMODS["Epic"])-1)]
        elif(rare == 1):
            return GRENADEMODS["Legendary"][random.randint(0,len(GRENADEMODS["Legendary"])-1)]
    elif(itemType == 2):
        if(rare == 0):
            return PERKS["Epic"][random.randint(0,len(PERKS["Epic"])-1)]
        elif(rare == 1):
            return PERKS["Legendary"][random.randint(0,len(PERKS["Legendary"])-1)]

global DIFFMODS
DIFFMODS = ["Random Islands","Regenerating Enemies","Locked Slots","Buffed Enemies","Manual Collection","Double Challenge","Resurrecting Enemies","Evolved Enemies","Unfair Bosses","Eternal Punishment","Volatile Explosions","No Safety Net"]
global DIFFMODSDETAILS
global ISLANDTYPE
ISLANDTYPE = ["Automatic","Arena","Horde","Elite","Boss","Shop","Parkour","CrabIsland"]
DIFFMODSDETAILS = ["Island types are chosen randomly instead of in a set order","Enemies regenarate health a short time after taking damage","Some inventory slot are locked and must be unlocked with crystals","Enemies have a chance to spawn with a powerful buff","Crystals must be manually picked up by walking near them before they expire","Double challenge modifiers on challenge portals","Enemies have a chance to spawn copies of themselves when eliminated","New enemies appear","All elite and boss islands have double the enmeies to fight","Taking damage lowers max health","No damage immunity when eliminating exploding enemies at close range","No more death prevention when reaching 1 health"]
global WEAPONMODS
global GRENADEMODS
global PERKS
global WEAPONS
global ISLANDS
setUpIslands()
WEAPONMODS = json.loads("{}")
GRENADEMODS = json.loads("{}")
PERKS = json.loads("{}")
WEAPONS = []
RARECOLOR = 3
EPICCOLOR = 13
LEGENDARYCOLOR = 14
GREEDCOLOR = 12

try:
    curses.init_pair(1, RARECOLOR, -1)
    curses.init_pair(2, EPICCOLOR, -1)
    curses.init_pair(3, LEGENDARYCOLOR, -1)
    curses.init_pair(4, GREEDCOLOR, -1)
    colors = "ItemRarityColor"
except:
    colors = "None"


global owd
owd = os.getcwd()
owd = owd.replace("\\","/")



# start = time.time()
# print(getPresets())
# print(getPresets(moreInfo=True))
# stop = time.time()
# print(round(stop-start,2))
# exiting(0)


# os.remove("CrabChampionSaveManager/backupDataCache.json")
# time.sleep(1)

makeScreen()
infoScreen("Starting Crab Champion Save Manager\nThis may take a few seconds")
loadSettings()




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





uepath = getUesavePath()
if(uepath == ""):
    scrollInfoMenu("This script uses uesave a lot,it is highly reccomended to download it\nyou can still use this program but i can not guarantee that it will fully work\nPress Enter to continue")
else:
    start = time.time()
    loadCache()
    loadPresets()
    stop = time.time()
# print(round(stop-start,2))
# exiting(0)
start = time.time()
getUnlocked()
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



            




#time.sleep(20)
mainMenuPrompt += "\n\nWelcome to Crab Champion Save Manager"
mainMenuPrompt += "\nMade By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager\nWhat do you want to do\n"
while(True):
    options = "Manage Backups\nManage Presets\nInfo/How to use\nSettings\nExit"
    #options = "Manage Backups\nInfo/How to use\nSettings\nExit"
    #options = "Edit save game\nBackup Save\nUpdate backup\nRestore Save from backup (Warning : Deletes current save)\nDelete backup\nList Backups\nInfo/How to use\nSettings\nExit"
    choice = scrollSelectMenu(mainMenuPrompt,options,-1,1)+1
    # if(choice == 1):
    #     editBackup() # turned to curse
    # elif(choice == 2):
    #     backupSave()
    # elif(choice == 3):
    #     updateBackup() # turned to curse
    # elif(choice == 4):
    #     restoreBackup()# turned to curse
    # elif(choice == 5):
    #     deleteBackup() # turned to curse
    # elif(choice == 6):
    #     listBackups()
    # if(choice>1):
    #     choice+=1
    if(choice == 1):
        manageBackups()
    elif(choice == 2):
        managePresets()    
    elif(choice == 3):
        infoList = """
Crab Champion Save Manager
Welcome to Crab Champion Save Manager, a script designed to help you manage your save files for the game Crab Champion.
Made By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager
This program provides the following options:\n

\nManage Backups

\n - Edit Save Game:
       - Uses uesave to allow the user to edit the SaveSlot.sav file in a backup or your current save

\n - Backup Save:
       - backup up your current save with a custom name

\n - Update backup:
       - Update a already made backup with the current saved run

\n - Restore Save from Backup:
       - Restores a run from a backup

\n - Delete Backup:
       - Deletes a backup
       - Note: Deleting a backup cannot be undone, so be careful when removing backups.

\n - List Backups:
       - Lists all backups and trys to list some info about the run
       - Allows the user to select a backup at which more info about that run is displayed
       - DPB - Damage Per Bullt
       - SPS - Shots Per Second
       - DPS - Damage Per Second

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
    elif(choice == 4):
        settings()
    elif(choice == 5):
        break
    
exiting(0)
