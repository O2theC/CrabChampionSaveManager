import os
import subprocess
import time

if not os.path.exists("CrabChampionSaveManagerUpdated.exe"):
    print("Update Error: Invalid execution of updater.exe.")
    print(
        "Please do not run updater.exe manually. It is automatically executed by the main program."
    )
    exit(2)
print("\nUpdating CCSM\nThis may take a few minutes\n3/4")
try:
    os.remove("CrabChampionSaveManager.exe")
except:
    # f = open("no .exe", "w")
    # f.write("s")
    # f.close()
    None
try:
    os.rename("CrabChampionSaveManagerUpdated.exe", "CrabChampionSaveManager.exe")
except:
    # f = open("no update.exe", "w")
    # f.write("s")
    # f.close()
    None

os.system("start CrabChampionSaveManager.exe")
