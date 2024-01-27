import PySimpleGUI as sg
from CrabChampionSaveManager.Modules import ExitHandler
from CrabChampionSaveManager.Modules.Utils import Utils
from CrabChampionSaveManager.Modules.Menus.ManageSavesSubMenus import createSave
from CrabChampionSaveManager.Modules import ConfigManager


def ManageSaves(window: sg.Window):
    window["ManageSavesMenu"].update(visible=True)
    window["MainMenu"].update(visible=False)
    # print(ConfigManager.get("Secret","No Secret"))
    while True:
        event, values = window.read()
        if event == "CreateSave":
            createSave.createSave(window)
        elif event == "UpdateSave":
            Utils.UnfinishedFeaturePopup(window)
        elif event == "LoadSave":
            Utils.UnfinishedFeaturePopup(window)
        if event == "EditSave":
            Utils.UnfinishedFeaturePopup(window)
        elif event == "DeleteSave":
            Utils.UnfinishedFeaturePopup(window)
        elif event == "ConvertSave":
            Utils.UnfinishedFeaturePopup(window)
        elif event == "ManageSavesMenuBack":
            break
        elif event == sg.WIN_CLOSED:
            ExitHandler.Exit(0, "User Closed Window")
    window["ManageSavesMenu"].update(visible=False)
    window["MainMenu"].update(visible=True)


def getLayout():
    layout = [
        sg.Column(
            layout=[
                [
                    sg.Text(
                        "Managing Saves",
                        key="ManageSavesMenuTitle",
                        font=("Helvetica", 15),
                    )
                ],
                [
                    sg.Button("Save Current Run", key="CreateSave", size=(28, 2)),
                    sg.Text("Create a save using your current run"),
                ],
                [
                    sg.Button("Update Save", key="UpdateSave", size=(28, 2)),
                    sg.Text("Update a save using your current run"),
                ],
                [
                    sg.Button("Load Save", key="LoadSave", size=(28, 2)),
                    sg.Text("Load a saved run and overwrite your current run"),
                ],
                [
                    sg.Button("Edit Save", key="EditSave", size=(28, 2)),
                    sg.Text("Edit a saved run"),
                ],
                [
                    sg.Button("Delete Save", key="DeleteSave", size=(28, 2)),
                    sg.Text("Delete a saved run"),
                ],
                [
                    sg.Button("Make Preset From Save", key="ConvertSave", size=(28, 2)),
                    sg.Text("Create a preset based on a saved run"),
                ],
                [
                    sg.Button("Back", key="ManageSavesMenuBack", size=(28, 2)),
                    sg.Text("Go back to the main menu"),
                ],
            ],
            key="ManageSavesMenu",
            visible=False,
        )
    ]
    layout.extend(createSave.getLayout())
    return layout
