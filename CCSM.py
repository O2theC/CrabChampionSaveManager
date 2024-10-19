import datetime
import hashlib
import os
import random
import shutil
import time
import subprocess
import platform
import sys
import json
import threading
import re
from tkinter import filedialog
import tkinter
import traceback
import orjson
import xxhash


global isExe
global isLinux
global VERSION
isExe = False
isLinux = False

VERSION = "5.0.0"

if platform.system() == "Linux":
    isLinux = True

if getattr(sys, "frozen", False):
    isExe = True


def unhandledExeceptionHandle(exc_type, exc_value, exc_traceback):
    trace = ""
    ar = traceback.format_tb(exc_traceback)
    for i in ar:
        trace += i

    f = open("traceback.log", "w")
    f.write(
        "An Execption/Error happened, contact dev to report or check wiki\n\nType : "
        + str(exc_type)
        + "\nValue : "
        + str(exc_value)
        + "\nTraceback : \n"
        + trace
    )
    f.close()
    infoScreen(
        "An Execption/Error happened, contact dev to report or check wiki\n\nType : "
        + str(exc_type)
        + "\nValue : "
        + str(exc_value)
        + "\nTraceback : \n"
        + trace
    )
    time.sleep(10)
    pass


sys.excepthook = unhandledExeceptionHandle


def closeScreen():
    global screen
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


StopBackupWatcherEvent = threading.Event()


def exiting(var, force=False):
    global infoScreen
    StopBackupWatcherEvent.set()
    try:
        AccountStatsWatcherThread.join()
    except BaseException:
        None
    try:
        screen.clear()
        closeScreen()
        saveSettings()
        
    except BaseException:
        None
    if force:
        os._exit(var)
    else:
        try:
            sys.exit(var)
        except SystemExit:
            os._exit(var)


try:
    import requests
    import curses
    from SavConverter import (
        sav_to_json,
        read_sav,
        json_to_sav,
        load_json,
        obj_to_json,
        print_json,
        get_object_by_path,
        insert_object_by_path,
        replace_object_by_path,
        update_property_by_path,
    )
except BaseException:
    print("Not all libraries are installed")
    perm = input("Permission to download libraries? (requests, SavConverter, windows-curses (windows only)) [y/N]\n")
    if "y" in perm.lower():
        if not isLinux:
            os.system("pip install windows-curses")
        os.system("pip install requests")
        os.system("pip install SavConverter")
        import requests
        import curses
        from SavConverter import (
            sav_to_json,
            read_sav,
            json_to_sav,
            load_json,
            obj_to_json,
            print_json,
            get_object_by_path,
            insert_object_by_path,
            replace_object_by_path,
            update_property_by_path,
        )
    else:
        print("no permission given, script can't start")
        exiting(0)


def isValidPathName(name):
    """tests the string to see if it's a valid folder or file name

    Args:
        name (str): the name of the file or folder to test

    Returns:
        bool: is it valid or not
    """

    WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
    "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3",
    "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

    # Invalid characters in Windows filenames
    WINDOWS_INVALID_CHARS = r'[<>:"/\\|?*]'

    # Check for null character (invalid in both Windows and Linux)
    if '\0' in name:
        return False
    
    # Check for Windows-specific rules
    if not isLinux:
        # Check for invalid characters in Windows
        if re.search(WINDOWS_INVALID_CHARS, name):
            return False
        
        # Check for reserved Windows names
        if name.upper() in WINDOWS_RESERVED_NAMES:
            return False
        
        # Check if the name ends with a space or period
        if name.endswith(' ') or name.endswith('.'):
            return False

    # Check for Linux-specific rules
    elif isLinux:
        # In Linux, `/` and `\0` are the only invalid characters for file/folder names
        if '/' in name:
            return False

    # Ensure name length is within limits (both OSes generally limit to 255 chars for filenames)
    if len(name) > 255:
        return False

    return True


def makeScreen():
    global screen
    screen = curses.initscr()
    curses.noecho()  # Don't display user input
    curses.cbreak()  # React to keys immediately without Enter
    screen.keypad(True)  # Enable special keys (e.g., arrow keys)
    try:
        curses.start_color()
        curses.use_default_colors()
    except BaseException:
        None











# # Create a cProfile object
# profiler = cProfile.Profile()

# # Start profiling
# profiler.enable()


global DIFFMODS
global DIFFMODSDETAILS
global ISLANDTYPE
global WEAPONMODS
global GRENADEMODS
global PERKS
global WEAPONS
global ISLANDS
global BLESSINGS
global CHALLENAGES
global RARECOLOR
global EPICCOLOR
global LEGENDARYCOLOR
global GREEDCOLOR
global GameInfo
# name , description , dev name
BLESSINGS = [["Flawless","Don't take any damage to get an extra chest","Flawless"]]
CHALLENGES = [
    "One Hit - Enemies can be eliminated in one hit but so can you",
    "Energy Rings - Enemies spawn energy rings when eliminated",
    "Shrapnel - Enemies explode into a burst of projectiles when eliminated",
    "Spike Strikes - Enemies spawn spike strikes when eliminated",
    "Elemental Explosions - Enemies explode into a random elemental damage area when elminated ",
    "Mirrored Projectiles - Enemies fire projectiles back at you when hit",
    "Homing Thorns - Enemies explode into a cluster of homing thorns when eliminated",
    "Homing Barrels - Enemies spawn homing explosive barrels when eliminated",
]
DIFFMODS = [
    ["Random Islands", "Island types are chosen randomly instead of in a set order"],
    [
        "Regenerating Enemies",
        "Enemies regenarate health a short time after taking damage",
    ],
    ["Locked Slots", "Some inventory slot are locked and must be unlocked with crystals"],
    ["Buffed Enemies", "Enemies have a chance to spawn with a powerful buff"],
    [
        "Resurrecting Enemies",
        "Enemies have a chance to spawn copies of themselves when eliminated",
    ],
    ["Double Challenge", "Double challenge modifiers on challenge portals"],
    ["Surging Enemies", "Enemies spawn in much faster"],
    ["Evolved Enemies", "New enemies appear"],
    ["Unfair Bosses", "All elite and boss islands have double the enmeies to fight"],
    ["Eternal Punishment", "Taking damage lowers max health"],
    ["Limited Heals", "All healing is reduced by 50%"],
    ["No Safety Net", "No more death prevention when reaching 1 health"],
]
ISLANDTYPE = [
    "Automatic",
    "Arena",
    "Horde",
    "Elite",
    "Boss",
    "Shop",
    "Parkour",
    "CrabIsland",
    "Lobby",
]
DIFFMODSDETAILS = []
for d in range(len(DIFFMODS)):
    DIFFMODSDETAILS.append(DIFFMODS[d][1])
    DIFFMODS[d] = DIFFMODS[d][0]


setUpIslands()
WEAPONMODS = json.loads("{}")
GRENADEMODS = json.loads("{}")
PERKS = json.loads("{}")
WEAPONS = []
RARECOLOR = 3
EPICCOLOR = 13
LEGENDARYCOLOR = 14
GREEDCOLOR = 12


global owd
owd = os.getcwd()
owd = owd.replace("\\", "/")


# start = time.time()
# print(getPresets())
# print(getPresets(moreInfo=True))
# stop = time.time()
# print(round(stop-start,2))
# exiting(0)


# os.remove("CrabChampionSaveManager/backupDataCache.json")
# time.sleep(1)

if True and isLinux:
    os.system("export TERM=xterm-256color")

makeScreen()
for i in range(1, 256):
    try:
        curses.init_pair(i, i, -1)
    #        infoScreen(str(i))
    except BaseException:
        None
# time.sleep(30)
# exiting(0)
infoScreen("Starting Crab Champion Save Manager\nThis may take a few seconds")
loadSettings()

global AccountStatsWatcherThread
AccountStatsWatcherThread = threading.Thread(target=AccountStatsWatcher)
AccountStatsWatcherThread.start()
# watches for when the game starts or stops and backups account data/stats



if isSavesDir():
    if SaveGamePath == "Automatic" or isSavesDir(SaveGamePath):
        try:
            if isLinux:
                new_dir = os.path.expandvars(
                    "$HOME/.steam/steam/steamapps/compatdata/774801/pfx/drive_c/users/steamuser/AppData/Local/CrabChampions/Saved"
                )
            else:
                new_dir = os.path.expandvars("%LocalAppData%\\CrabChampions\\Saved")
            os.chdir(new_dir)
        except BaseException:
            infoScreen(
                "Could not find save game directory\nYou either don't have Crab Champions installed\n or you have it installed in a different spot than the default\n if it is installed in a different spot than the defualt then put this file in the equivalent of CrabChampions\\Saved or set the folder in the config \nPress any key to continue . . ."
            )
            screen.getch()
            exiting(0)
    else:
        os.chdir(SaveGamePath)


# print(round(stop2-start,2),"\n","Cache - ",round(stop-start,2),"\n","presets - ",round(stop2-start2,2))
# exiting(0)
start = time.time()
getUnlocked()
stop = time.time()
# print(round(stop-start,2))
# exiting(0)

curses.resize_term(TermHeight, TermWidth)

# 30 x 120

LatestVersion = VERSION
latestReleaseURL = "https://github.com/O2theC/CrabChampionSaveManager/releases/latest"
try:
    response = requests.get(latestReleaseURL)
    final_url = response.url
    final_url = final_url.removeprefix(
        "https://github.com/O2theC/CrabChampionSaveManager/releases/tag/"
    )
    LatestVersion = final_url
except BaseException:
    None

VersionValue = versionToValue(VERSION)
LatestValue = versionToValue(LatestVersion)


updatePrompt = True


# profiler.disable()

# # Print the profiling results
# profiler.dump_stats("profile_results.prof")
# exiting(0)
# time.sleep(20)
lastSel = 0
while True:
    mainMenuPrompt = makeMainMenuPrompt(
        VERSION, LatestVersion, VersionValue, LatestValue, updatePrompt
    )
    updatePrompt = False
    options = "Manage Backups\nManage Presets\nManage Account Stuff\nInfo/How to use\nSettings\nExit"
    # options = "Manage Backups\nInfo/How to use\nSettings\nExit"
    # options = "Edit save game\nBackup Save\nUpdate backup\nRestore Save from backup (Warning : Deletes current save)\nDelete backup\nList Backups\nInfo/How to use\nSettings\nExit"
    choice, lastSel = scrollSelectMenu(
        mainMenuPrompt,
        options,
        -1,
        1,
        returnAnything=True,
        startChoice=lastSel,
        loop=True,
    )
    choice += 1

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
    if choice == 1:
        manageBackups()
    elif choice == 2:
        managePresets()
    elif choice == 3:
        manageAccount()
    elif choice == 4:
        infoList = """
Crab Champion Save Manager
Welcome to Crab Champion Save Manager, a script designed to help you manage your save files for the game Crab Champion.
Made By O2C, GitHub repo at https://github.com/O2theC/CrabChampionSaveManager
Credit to afkaf for the sav converter - https://github.com/afkaf/Python-GVAS-JSON-Converter
This script has some elements that require access to the internet, this includes:
Version Checking
Downloading an updater for the .exe version of the program"""
        scrollInfoMenu(infoList, -1)
    elif choice == 5:
        settings()
    elif choice == 6:
        break

exiting(0)
