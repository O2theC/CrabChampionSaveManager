import pandas as pd
import json
import tkinter as tk
from tkinter import filedialog
import os
import os.path

def get_inventory_data_frame_from_json(x):
    """Input is jsonified version of .sav file."""
    things = [{'key1':'WeaponMods', 'key2':"WeaponModDA"}, \
              {'key1':'GrenadeMods', 'key2':"GrenadeModDA"}, \
              {'key1':'Perks', 'key2':'PerkDA'}]
    out = list()
    for thing in things:
        try:
            tmp = x['root']['properties']['AutoSave']['Struct']['value']['Struct'][thing['key1']]['Array']['value']['Struct']['value']
        except:
            print("No save found")
            return ""
        for idx in range(0, len(tmp)):
            # get status and name
            parse_tmp = tmp[idx]['Struct'][thing['key2']]['Object']['value'].split("/")
            name = parse_tmp[6]
            # fix names (split by '.' grab first and split by '_' grab 2
            name = name.split('.')[0].split('_')[2]
            class_ = parse_tmp[5]
            type_ = parse_tmp[4]
            level = tmp[idx]['Struct']['Level']['Byte']['value']['Byte']
            out.append({"class": class_, "type": type_, "name": name, "level":level})

    df = pd.DataFrame(out)
    df = df.sort_values(['type', 'class', 'name'])

    return(df)

if __name__=="__main__":
    root = tk.Tk()
    root.withdraw()
    
    # select file to use with uesave
    appdata_roaming_dir = os.getenv("LOCALAPPDATA")
    crab_locale = os.path.normpath(appdata_roaming_dir + "/CrabChampions/Saved/")
    
    input_file = filedialog.askopenfilename(initialdir=crab_locale)
    output_file = "save.json"
    my_command = "uesave.exe to-json -i \"" + input_file + "\" -o " + output_file
    os.system(my_command)
    
    with open('save.json') as f:
        x = json.load(f)

    # remove blah.json
    os.remove("save.json")
    df = get_inventory_data_frame_from_json(x)
    pd.set_option('display.max_rows', None)  # Display all rows
    pd.set_option('display.max_columns', None)  # Display all columns
    pd.set_option('display.width', None)  # Disable column width restriction
    pd.set_option('display.max_colwidth', None)  # Disable column content truncation   
    print(df.to_string(index=False))

    
        
                
