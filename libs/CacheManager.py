




import os


cache = {}



# cache stores run and presets ()

def updateCache():

    runfolder=os.path.expandvars("%LocalAppData%\\CrabChampions\\Saved")
    dataFolder = "./CCSM"