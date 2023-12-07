import time
from CrabChampionSaveManager.Modules.Utils import BaseUtils

code = BaseUtils.EnsureExternalLibs()
if(code == 1):
    exit(1)

import PySimpleGUI as sg
import requests
from CrabChampionSaveManager.Modules.Menus import MainMenu



Cache = dict()




# pre menu code

window = sg.Window(
    "Crab Champion Save Manager", resizable=True, size=(1120, 600), layout=MainMenu.getLayout()
)

while True:
    event, values = window.read()
    # print(window["Test"].get_size())
    # print(window["texasd"].Font)
    if event in (sg.WIN_CLOSED, "OK"):
        break


# time.sleep(123)
# main menu

# ManageMainMenu()
