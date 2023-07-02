import os
import time
import subprocess

print("\n\n\n\n\nthe error above is fine, no clue why it does it\nwaiting for SaveManager to stop")
time.sleep(5)
os.remove("CrabChampionSaveManager.exe")
os.rename("CrabChampionSaveManagerUpdated.exe","CrabChampionSaveManager.exe")
subprocess.Popen(["CrabChampionSaveManager.exe"], shell=True)
