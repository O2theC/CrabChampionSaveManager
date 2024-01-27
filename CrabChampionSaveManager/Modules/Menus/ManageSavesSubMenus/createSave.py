import os
import shutil
import time
import PySimpleGUI as sg
from CrabChampionSaveManager.Modules import ExitHandler
from CrabChampionSaveManager.Modules.Utils import Utils


def createSave(window: sg.Window):
    window["ManageSavesMenu"].update(visible=False)
    window["CreateSaveMenu"].update(visible=True)
    print(Utils.getSaves())
    TextBefore = ""
    errorTime = 0
    while True:
        event, values = window.read(timeout=1)
        if time.time() - errorTime > 5:
            window["SaveRunErrorMessage"].update(visible=False)
        if event == "SaveNameInput":
            currentText = window["SaveNameInput"].get()
            if TextBefore != currentText:
                forbiddenCharacters = '<>:"/\\|?*'
                nono = False
                for character in forbiddenCharacters:
                    if character in currentText:
                        nono = True
                        currentText = currentText.replace(character, "")
                if nono:
                    window.ding()
                    window["SaveNameInput"].update(value=currentText)
                    window["SaveRunErrorMessage"].update(
                        value='Save name can not contain any of these characters <>:"/\\|?*', visible=True, )
                    errorTime = time.time()

        if event == "SaveRun":
            saveName = window["SaveNameInput"].get()
            savePath = Utils.getSavesPath()
            maxSaveNameLength = 260 - (len(savePath) - 1)
            error = False
            # makes ure the name isn't nothing
            if len(saveName) == 0:
                error = True
                window.ding()
                window["SaveRunErrorMessage"].update(
                    value="Save name can be empty", visible=True
                )
                errorTime = time.time()
            # make sure the name doesn't start or end with a space or a period
            if saveName[-1:] in (" ", ".") or saveName[:1] in (" ", "."):
                error = True
                window.ding()
                window["SaveRunErrorMessage"].update(
                    value="Save name can not end or start with a space or period",
                    visible=True,
                )
                errorTime = time.time()
            # make sure the path length is below the max path length since windows has
            # that problem
            if len(saveName) > maxSaveNameLength:
                error = True
                window.ding()
                window["SaveRunErrorMessage"].update(
                    value=f"Save name can not be longer than {maxSaveNameLength} characters",
                    visible=True,
                )
                errorTime = time.time()
            # makes sure save name isn't any of the folders the game uses
            if saveName in ("Config", "Crashes", "Logs", "SaveGames"):
                error = True
                window.ding()
                window["SaveRunErrorMessage"].update(
                    value=f"Config, Crashes, Logs, and SaveGames are restricted names and can't be used",
                    visible=True,
                )
                errorTime = time.time()
            saves = Utils.getSaves()
            # make sure save name isn't the same as any other saves
            for save in saves:
                save = save.lower()
                if saveName.lower() == save:
                    error = True
                    window.ding()
                    window["SaveRunErrorMessage"].update(
                        value=f"Save name can not have the same name as another save",
                        visible=True,
                    )
                    errorTime = time.time()
                    break

            # create save if no error has happened
            if not error:
                savesPath = Utils.getSavesPath()
                saveGamePath = os.path.join(savePath, "SaveGames")
                newSavePath = os.path.join(savePath, saveName)
                shutil.copytree(saveGamePath, newSavePath)
                os.remove(
                    os.path.join(newSavePath, "SaveSlotBackupA.sav")
                )  # remove backup files to reduce folder size
                os.remove(os.path.join(newSavePath, "SaveSlotBackupB.sav"))
                break

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
                    sg.Input(key="SaveNameInput", enable_events=True),
                    sg.Text("", key="SaveRunErrorMessage", visible=False),
                ],
                [sg.Button("Save Run", key="SaveRun", size=(28, 2))],
                [sg.Button("Back", key="CreateSaveMenuBack", size=(28, 2))],
            ],
            key="CreateSaveMenu",
            visible=False,
        )
    ]
