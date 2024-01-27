import hashlib
import os
import sys
import time
import platform


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
    except BaseException:
        print("PySimpleGUi : Not Installed")
        libs["PySimpleGUI"] = False
        good = False

    try:
        import requests

        print("requests : Installed")
        libs["requests"] = True
    except BaseException:
        print("requests : Not Installed")
        libs["requests"] = False
        good = False

    try:
        import SavConverter

        print("SavConverter : Installed")
        libs["SavConverter"] = True
    except BaseException:
        print("SavConverter : Not Installed")
        libs["SavConverter"] = False
        good = False

    return good, libs


def getOS():
    return platform.system()


def isEXE():
    return getattr(sys, "frozen", False)


def getHash(file_path):
    # Get the absolute path of the file
    absolute_path = os.path.abspath(file_path)
    absolute_path = absolute_path.replace("\\", "/")
    # Open the file in binary mode and read it in chunks
    with open(absolute_path, "rb") as file:
        # Create a SHA-512 hash object
        sha512_hash = hashlib.sha512()

        # Read the file in chunks to avoid loading the entire file into memory
        for chunk in iter(lambda: file.read(4096), b""):
            # Update the hash object with the current chunk
            sha512_hash.update(chunk)

    # Get the hexadecimal representation of the hash
    checksum = sha512_hash.hexdigest()

    return checksum
