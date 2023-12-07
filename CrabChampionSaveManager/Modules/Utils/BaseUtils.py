import os
import time


def EnsureExternalLibs():
    while True:
        print("Checking Librays")
        good, libs = CheckLibrays()
        if good:
            print("All Required Librays are Installed")
            break
        else:
            print(
                "Not all required librays are installed, Permission to install the following librays? [Y/n]"
            )
            for key in libs.keys():
                if not libs[key]:
                    print(key)
            perm = input()
            if "n" in perm.lower():
                print(
                    "Permission Denied, Program can not run without librays\nShutting Down"
                )
                time.sleep(3)
                return 1
            else:
                libsDownload = ""
                for key in libs.keys():
                    if not libs[key]:
                        libsDownload += " " + key
                os.system("pip install" + libsDownload)


def CheckLibrays():
    libs = dict()
    good = True
    try:
        import PySimpleGUI as sg

        print("PySimpleGUi : Installed")
        libs["PySimpleGUI"] = True
    except:
        print("PySimpleGUi : Not Installed")
        libs["PySimpleGUI"] = False
        good = False

    try:
        import requests

        print("requests : Installed")
        libs["requests"] = True
    except:
        print("requests : Not Installed")
        libs["requests"] = False
        good = False
        
    try:
        import SavConverter

        print("SavConverter : Installed")
        libs["SavConverter"] = True
    except:
        print("SavConverter : Not Installed")
        libs["SavConverter"] = False
        good = False

    return good, libs
