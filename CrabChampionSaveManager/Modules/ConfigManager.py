import PySimpleGUI as sg


settings = sg.UserSettings()

defaults = {
    "SaveGamePath": "Automatic",
    "SaveGamePathWindows": "%LocalAppData%/CrabChampions/Saved",
    "SaveGamePathLinux": "$HOME/.steam/steam/steamapps/compatdata/774801/pfx/drive_c/users/steamuser/AppData/Local/CrabChampions/Saved",
}


def __init__():
    settings = sg.UserSettings("CCSMConfig.json", "./CrabChampionSaveManager")
    for k in defaults.keys():
        ensureConfig(k, defaults[k])


def set(key, value):
    settings.set(key, value)


def get(key, default="Automatic"):
    if default == "Automatic":
        try:
            default = defaults[key]
        except BaseException:
            default = None
    return settings.get(key, default)


def ensureConfig(key, default):
    config = get(key, None)
    if config is None:
        set(key, default)
