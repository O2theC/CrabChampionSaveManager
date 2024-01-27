import PySimpleGUI as sg


def getLayout(currentVersion, latestVersion):
    layout = layout = [
        sg.Column(
            layout=[
                [
                    sg.Text(
                        "Crab Champion Save Manager",
                        size=(None, None),
                        font=("Helvetica", 20),
                        key="Title",
                    )
                ],
                [
                    sg.Text(
                        "Made by O2theC",
                        size=(None, None),
                        font=("Helvetica", 10),
                        pad=(5, 0),
                        key="Author",
                    )
                ],
                [
                    sg.Text(
                        f"Version {currentVersion}",
                        size=(None, None),
                        font=("Helvetica", 9),
                        pad=(5, 0),
                        key="CurrentVersion",
                    )
                ],
                [
                    sg.Text(
                        f"Latest Version {latestVersion}",
                        size=(None, None),
                        font=("Helvetica", 9),
                        pad=(5, 0),
                        key="LatestVersion",
                    )
                ],
                [sg.Sizer(0, 30)],
                [sg.Button("Manage Saves", key="ManageSaves", size=(28, 2)),sg.Text("Manage the saves of runs")],
                [sg.Button("Manage Presets", key="ManagePresets", size=(28, 2)),sg.Text("Manage presets that can be used to create runs")],
                [sg.Button("Manage Account Stuff", key="ManageAccount", size=(28, 2)),sg.Text("Manage account related stuff")],
                [sg.Button("Settings", key="Settings", size=(28, 2)),sg.Text("Manage the settings of the save manager")],
                [sg.Button("Exit", key="MainMenuExit", size=(28, 2)),sg.Text("Exit the save manager")],
            ],
            key="MainMenu",
        )
    ]

    return layout
