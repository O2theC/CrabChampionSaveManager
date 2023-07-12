import os
import subprocess
import time

if(not os.path.exists("CrabChampionSaveManagerUpdated.exe")):
    print("Update Error: Invalid execution of updater.exe.")
    print("Please do not run updater.exe manually. It is automatically executed by the main program.")
    exit(2)

time.sleep(2)
try:
    os.remove("CrabChampionSaveManager.exe")
except:
    None
try:
    os.rename("CrabChampionSaveManagerUpdated.exe","CrabChampionSaveManager.exe")
except:
    None
subprocess.Popen(["CrabChampionSaveManager.exe"], shell=True)
