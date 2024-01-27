import time
from CrabChampionSaveManager.Modules.Utils import BaseUtils

if(not BaseUtils.isEXE()):
    code = BaseUtils.EnsureExternalLibs()
    if code == 1:
        exit(1)

import PySimpleGUI as sg
import requests
from CrabChampionSaveManager.Modules.Menus import MainMenu
from CrabChampionSaveManager.Modules import VersionManager
from CrabChampionSaveManager.Modules.Menus import ManageSaves
from CrabChampionSaveManager.Modules.Utils import Utils
from CrabChampionSaveManager.Modules import ExitHandler
from CrabChampionSaveManager.Modules import ConfigManager
ConfigManager.__init__()

# sg.UserSettings("config1.json")
# sg.UserSettings.set("key1","meow","meow")

Cache = dict()


layout = []
layout.extend(
    MainMenu.getLayout(VersionManager.VERSION, VersionManager.getLatestVersion())
)
layout.extend(ManageSaves.getLayout())
layout.extend(ManageSaves.getLayout())
layout = [layout]
# print(layout)
# pre menu code
# ConfigManager.set("Secret","Cool Secret")
window = sg.Window(
    "Crab Champion Save Manager", resizable=True, size=(1120, 600), layout=layout
)

ExitHandler.window = window
while True:
    event, values = window.read()
    if event == "ManageSaves":
        ManageSaves.ManageSaves(window)
    elif event == "ManagePresets":
        Utils.UnfinishedFeaturePopup(window)
    elif event == "ManageAccount":
        Utils.UnfinishedFeaturePopup(window)
    if event == "Settings":
        Utils.UnfinishedFeaturePopup(window)

    if event == sg.WIN_CLOSED:
        ExitHandler.Exit(0,"User Closed Window")
    if event == "MainMenuExit":
        ExitHandler.Exit(0,"Exit Main Menu")


# time.sleep(123)
# main menu

# ManageMainMenu()
