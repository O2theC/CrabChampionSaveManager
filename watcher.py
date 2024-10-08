import json
import os
import shutil
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
import SavConverter

cache = dict()
try:
    with open("watcherCache.json","r") as f:
        cache = json.loads(f.read())
except:
    None

def addThing(key,value):
    val = dict()
    val["validate"] = value
    value = json.loads(json.dumps(val,indent=4))["validate"]
    if(value == None or len(str(value))<5):
        return
    if(key in cache.keys()):
        if(isinstance(value,list)):
            for v in value:
                cache[key].append(v)
        else:
            cache[key].append(value)
    else:
        cache[key] = list(value)
    try:
        for k in cache.keys():
            cache[k] = list(set(cache[k]))
            cache[k].sort()
            values = cache[k]
            newVals = []
            for v in values:
                if(len(v)<5):
                    continue
                newVals.append(v)
            cache[k] = newVals
    except:
        print(f"ERROR\n{key}\n{value}")
    
    with open("watcherCache.json","w") as f:
        f.write(json.dumps(cache,indent=4))

def jsonFromSav(path):
    return SavConverter.sav_to_json(SavConverter.read_sav(path))

nullTime = 0
stacks = 0
shutil.copyfile(r"C:\Users\O2C\AppData\Local/CrabChampions/Saved/SaveGames\SaveSlot - Copy.sav",r"C:\Users\O2C\AppData\Local/CrabChampions/Saved/SaveGames\SaveSlot.sav")
class EventHandle(FileSystemEventHandler):
    """Logs all the events captured."""
    nullTime = 0
    stacks = 0

    def __init__(self, logger=None):
        super().__init__()
        self.nullTime = 0
        self.stacks = 0
        self.logger = logger or logging.root

    def on_modified(self, event):
        super().on_modified(event)

        if(event.src_path==r"C:\Users\O2C\AppData\Local/CrabChampions/Saved/SaveGames\SaveSlot.sav"):
            self.stacks+=1
            if(self.stacks>4):
                self.nullTime =time.time()
                self.stacks = 0
            if(time.time()-self.nullTime<=1):
                self.stacks = 0
            else:
                print("file changed"," - ",event.src_path)
                jsonnedSav = jsonFromSav(r"C:\Users\O2C\AppData\Local/CrabChampions/Saved/SaveGames\SaveSlot.sav")
                save = SavConverter.get_object_by_path(jsonnedSav,[{"name":"AutoSave"},"value",{"name": "NextIslandInfo"},"value"])
                addThing("biomes",SavConverter.get_object_by_path(save,[{"name":"Biome"},"value"]))
                addThing("islandNames",SavConverter.get_object_by_path(save,[{"name":"IslandName"},"value"]))
                addThing("islandTypes",SavConverter.get_object_by_path(save,[{"name":"IslandType"},"value"]))#Blessing
                addThing("challengeMods",SavConverter.get_object_by_path(save,[{"name":"ChallengeModifiers"},"value"]))
                addThing("blessings",SavConverter.get_object_by_path(save,[{"name":"Blessing"},"value"]))
                addThing("lootpools",SavConverter.get_object_by_path(save,[{"name":"RewardLootPool"},"value"]))
                with open("jsonnedSav.json","w") as f:
                    f.write(json.dumps(jsonnedSav,indent=4))
                shutil.copyfile(r"C:\Users\O2C\AppData\Local/CrabChampions/Saved/SaveGames\SaveSlot - Copy.sav",r"C:\Users\O2C\AppData\Local/CrabChampions/Saved/SaveGames\SaveSlot.sav")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = os.path.expandvars("%LocalAppData%/CrabChampions/Saved/SaveGames")
    print(path)
    event_handler = EventHandle()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()