from SavConverter import sav_to_json,read_sav,get_object_by_path




print(get_object_by_path(sav_to_json(read_sav("./testing/SaveSlot.sav")),[{"name": "AutoSave"},"value"]))