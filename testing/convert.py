import SavConverter





with open("./testing/savConvert-SaveSlot.sav.json","w") as f:
    f.write(SavConverter.sav_to_json(SavConverter.read_sav("./testing/SaveSlot.sav"),string=True))