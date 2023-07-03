import os
import subprocess

if(not os.path.exists("CrabChampionSaveManagerUpdated.exe")):
    print("Update Error: Invalid execution of updater.exe.")
    print("Please do not run updater.exe manually. It is automatically executed by the main program.")
    exit(2)

print("\n\n\nthe error above is fine, no clue why it does it\nwaiting for SaveManager to stop")
os.remove("CrabChampionSaveManager.exe")
os.rename("CrabChampionSaveManagerUpdated.exe","CrabChampionSaveManager.exe")
subprocess.Popen(["CrabChampionSaveManager.exe"], shell=True)
print("CrabChampionSaveManager.exe has been updated")
