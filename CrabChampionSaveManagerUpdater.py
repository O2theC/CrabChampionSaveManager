import os
import subprocess

print("\n\n\nthe error above is fine, no clue why it does it\nwaiting for SaveManager to stop")
os.remove("CrabChampionSaveManager.exe")
os.rename("CrabChampionSaveManagerUpdated.exe","CrabChampionSaveManager.exe")
subprocess.Popen(["CrabChampionSaveManager.exe"], shell=True)
print("CrabChampionSaveManager.exe has been updated")
