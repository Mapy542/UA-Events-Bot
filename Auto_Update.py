import os
import urllib.request

import tinydb


def UpdatePackages():
    # Find and install all required Packages.
    os.system("python3 -m pip install --upgrade pip")  # update pip
    try:
        os.system("python3 -m pip install --upgrade discord")
    except:
        print("Error installing discord package")


def CheckForUpdate():
    url = "https://raw.githubusercontent.com/Mapy542/UA-Events-Bot/main/version.txt"
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode("utf-8")
        VersionIdentifier = text.split(".")
        VersionIdentifier = [int(i) for i in VersionIdentifier]
    except:
        print("Error checking for update")
        return False

    try:
        with open(
            os.path.join(os.path.realpath(os.path.dirname(__file__)), "version.txt"), "r"
        ) as f:
            CurrentVersionString = f.read()
    except:
        print("Error reading version.txt")
        return False
    CurrentVersion = CurrentVersionString.split(".")
    CurrentVersion = [int(i) for i in CurrentVersion]

    MaxCompare = len(VersionIdentifier)
    if len(CurrentVersion) < MaxCompare:
        MaxCompare = len(CurrentVersion)

    for i in range(MaxCompare):
        if VersionIdentifier[i] > CurrentVersion[i]:
            return True

    return False


def UpdateSoftware():
    if not CheckForUpdate():  # double check available update
        return

    import shutil

    # delete all files in current directory
    folder = os.path.realpath(os.path.dirname(__file__))
    for filename in os.listdir(folder):
        if filename == ".git":
            continue
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))

    import io
    import zipfile

    import requests

    r = requests.get(  # download latest version
        "https://github.com/Mapy542/UA-Events-Bot/archive/refs/heads/main.zip"
    )
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(folder)

    # move files from zip
    source = os.path.join(folder, "UA-Events-Bot-main")
    destination = folder

    # code to move the files from sub-folder to main folder.
    files = os.listdir(source)
    for file in files:
        file_name = os.path.join(source, file)
        shutil.move(file_name, destination)

    # delete zip folder
    os.rmdir(source)

    UpdatePackages()

    print("Update complete. Exiting...")
    os.system("python3 " + os.path.join(os.path.realpath(os.path.dirname(__file__)), "Bot.py"))
    exit()
