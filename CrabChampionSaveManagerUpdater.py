import os
import time
import subprocess

print("waiting for SaveManager to stop")
time.sleep(5)
os.remove("CrabChampionSaveManager.exe")
os.rename("CrabChampionSaveManagerUpdated.exe","CrabChampionSaveManager.exe")
subprocess.Popen(["CrabChampionSaveManager.exe"], shell=True)