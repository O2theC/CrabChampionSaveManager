import PySimpleGUI as sg


def getLayout():
    layout = layout = [
        [
            sg.Text(
                "Crab Champion Save Manager",
                size=(None, None),
                font=("Helvetica", 20),
                key="texasd",
            )
        ],
        [
            sg.Text(
                "Made by O2theC",
                size=(None, None),
                font=("Helvetica", 10),
                pad=(5, 0),
                key="texasd",
            )
        ],
        [
            sg.Text(
                "Version 1.0.0",
                size=(None, None),
                font=("Helvetica", 9),
                pad=(5, 0),
                key="texasd",
            )
        ],
        [
            sg.Text(
                "Latest Version 1.0.0",
                size=(None, None),
                font=("Helvetica", 9),
                pad=(5, 0),
                key="texasd",
            )
        ],
        [sg.Sizer(0, 30)],
        [sg.Button("Manage Backups", key="ManageBackups", size=(28, 2))],
        [sg.Button("Manage Presets", key="ManagePresets", size=(28, 2))],
        [sg.Button("Manage Account Stuff", key="ManageAccount", size=(28, 2))],
        [sg.Button("Settings", key="Settings", size=(28, 2))],
        [sg.Button("Exit", key="Exit", size=(28, 2))],
    ]
    return layout