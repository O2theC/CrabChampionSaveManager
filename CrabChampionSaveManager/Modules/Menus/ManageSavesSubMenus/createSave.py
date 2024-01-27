import time
import PySimpleGUI as sg
from CrabChampionSaveManager.Modules import ExitHandler
from CrabChampionSaveManager.Modules.Utils import Utils


def createSave(window:sg.Window):
    window["ManageSavesMenu"].update(visible=False)
    window["CreateSaveMenu"].update(visible=True)
    print(Utils.getSaves())
    TextBefore = ""
    errorTime = 0
    while True:
        event, values = window.read(timeout=1)
        if(time.time()-errorTime>5):
            window["SaveRunErrorMessage"].update(visible=False)
        if event == "SaveNameInput":
            currentText = window["SaveNameInput"].get()
            if(TextBefore != currentText):
                forbiddenCharacters = "<>:\"/\\|?*"
                nono = False
                for character in forbiddenCharacters:
                    if(character in currentText):
                        nono = True
                        currentText = currentText.replace(character,"")
                if(nono):
                    window.ding()
                    window["SaveNameInput"].update(value =currentText)
                    window["SaveRunErrorMessage"].update(value="Save name can not contain any of these characters <>:\"/\\|?*",visible=True)
                    errorTime = time.time()
        
        if event == "SaveRun":
            None
        elif event == "CreateSaveMenuBack":
            break
        elif event == sg.WIN_CLOSED:
            ExitHandler.Exit(0, "User Closed Window")
    window["CreateSaveMenu"].update(visible=False)
    window["ManageSavesMenu"].update(visible=True)


def getLayout():
    return [
        sg.Column(
            layout=[
                [sg.Text("Save Current Run", font=("Helvetica", 15))],
                [
                    sg.Text("Save Name", key="SaveNameText"),
                    sg.Input(key="SaveNameInput",enable_events=True),
                    sg.Text("", key="SaveRunErrorMessage", visible=False),
                ],
                [sg.Button("Save Run", key="SaveRun", size=(28, 2))],
                [sg.Button("Back", key="CreateSaveMenuBack", size=(28, 2))],
            ],
            key="CreateSaveMenu",
            visible=False,
        )
    ]
