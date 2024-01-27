import hashlib
import os
import platform
import sys
import PySimpleGUI as sg
from CrabChampionSaveManager.Modules import ConfigManager


def UnfinishedFeaturePopup(window:sg.Window):
    sg.popup("This Feature is currently unfinished and can not be used",title="Unfinished Feature")
    
def getOS():
    return platform.system()


def isEXE():
    return getattr(sys, "frozen", False)


def getHash(file_path):
    # Get the absolute path of the file
    absolute_path = os.path.abspath(file_path)
    absolute_path = absolute_path.replace("\\", "/")
    # Open the file in binary mode and read it in chunks
    with open(absolute_path, "rb") as file:
        # Create a SHA-512 hash object
        sha512_hash = hashlib.sha512()

        # Read the file in chunks to avoid loading the entire file into memory
        for chunk in iter(lambda: file.read(4096), b""):
            # Update the hash object with the current chunk
            sha512_hash.update(chunk)

    # Get the hexadecimal representation of the hash
    checksum = sha512_hash.hexdigest()

    return checksum


def getSaves():
    savePath = getSaveGamePath()
    stuff = os.listdir(savePath)
    folders = []
    for thing in stuff:
        if(os.path.isdir(os.path.join(savePath,thing))):
            if(thing not in ("Config","Crashes","Logs","SaveGames")):
                folders.append(thing)
    
    saves = []
    for folder in folders:
        if(os.path.isfile(os.path.join(savePath,folder,"SaveSlot.sav"))):
            saves.append(folder)
    return saves
    
def getSaveGamePath():
    sameGamePath = ConfigManager.get("SaveGamePath","Automatic")
    if(sameGamePath == "Automatic"):
        if(getOS() == "Windows"):
            return os.path.expandvars(ConfigManager.get("SaveGamePathWindows"))
        else:
            return os.path.expandvars(ConfigManager.get("SaveGamePathLinux"))
    else:
        return os.path.expandvars(sameGamePath)