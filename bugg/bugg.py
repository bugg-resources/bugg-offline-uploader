#!/usr/bin/env python3

from tqdm import tqdm
import argparse
import json
import os 
from pathlib import Path
from datetime import datetime
from google.cloud import storage

def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str)
    except:
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return False
        return True
    return True


def main():
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(prog="bugg")
    parser.add_argument("--folder", help="The folder containing the SD card data. It should contain a config.json and a folder named audio. Defaults to the current directory", type=str, default=cwd,)

    args = parser.parse_args()

    configPath = os.path.join(args.folder, "config.json")
    audioPath = os.path.join(args.folder, "audio")

    # Check to see the files are here
    if not os.path.isfile(configPath):
        print(f"Cannot find config.json in the directory {args.folder}. \nYou can specify a folder containing the SD card data with the --folder option.")
        exit(1)

    storageClient = storage.Client.from_service_account_json(configPath)

    if not os.path.isdir(audioPath):
        print(f"Cannot find audio folder in the directory {args.folder}. \nYou can specify a folder containing the SD card data with --folder option.")
        exit(1)

    # Parse the config
    configfile = Path(configPath).read_text()
    config = json.loads(configfile)
    configId = config["device"]["config_id"]


    # Check the folder structure is the same as the config
    # the path should be audio/projectId/deviceId/configId
    projectPath = os.path.join(audioPath, config["device"]["project_id"])
    if not os.path.isdir(projectPath):
        print(f"Cannot find project folder {projectPath}. \nThe project folder needs to match the ID in the config file.")
        exit(1)


    projectPath = os.path.join(audioPath, config["device"]["project_id"])
    if not os.path.isdir(projectPath):
        print(f"Cannot find project folder {projectPath}. \nThe project folder needs to match the ID in the config file.")
        exit(1)

    # Get all the folders in this directory
    deviceFolderCandidates = os.listdir(projectPath)
    # filter out to only show folders with the prefix bugg_
    deviceFolders = [f for f in deviceFolderCandidates if os.path.isdir(os.path.join(projectPath, f)) and f.startswith("bugg_")]
    configFolders = []

    deviceIds = []

    # Ensure config ID in the folders match the config ID in the config file
    for deviceFolder in deviceFolders:
        deviceConfigPath = os.path.join(projectPath, os.path.join(deviceFolder, f"conf_{configId}"))
        if not os.path.isdir(deviceConfigPath):
            print(f"Expected to find folder \n {deviceConfigPath}\nbut it does not exist. Each device folder needs a folder with the config ID as it's name and the config ID needs to match the one in the config file (conf_{configId}) in the config file.")
            exit(1)
        else: 
            configFolders.append(deviceConfigPath)
            deviceIds.append(deviceFolder)

    filePathsToUpload = []
    # finally verify that all the mp3 files inside the configFolders have a valid ISO Date as their file name
    for configFolder in configFolders:
        mp3Files = [f for f in os.listdir(configFolder) if os.path.isfile(os.path.join(configFolder, f)) and f.endswith(".mp3")]
        for mp3File in mp3Files:
            #  Replace all the underscores with :
            fileName = mp3File[:-4].replace("_", ":")
            if not datetime_valid(fileName):
                print(f"All the mp3 files need to have a valid ISO Date as their names replacing colons ':' with underscores '_' (e.g. 2022-02-22T17_37_45.631Z.mp3). This one doesn't '{os.path.join(configFolder, mp3File)}'")
                exit(1)
            else:
                filePathsToUpload.append(os.path.join(configFolder, mp3File))

    print("""
        @                                                                            
        @@@@      @@@@@@@@@@@@@   (@@@@@@   ,@@@@@@    @@@@@@@@@@@@@@   %@@@@@@@@@@@@@
        &@@@@@@.    @@@@@@@@@@@@@@  (@@@@@@   ,@@@@@@  @@@@@@@@@@@@@@@@  @@@@@@@@@@@@@@@
            &@@@    @@@@@@@@@@@@@.  (@@@@@@   ,@@@@@@  @@@@@@#           @@@@@@         
                                    (@@@@@@   ,@@@@@@  @@@@@@#   ,,,,,.  @@@@@@    ,,,,,
                    @@@@@@@@@@&     (@@@@@@   ,@@@@@@  @@@@@@#  @@@@@@@  @@@@@@   %@@@@@
        ,@@@@    @@@@@@@@@@@@@/  (@@@@@@   (@@@@@@  @@@@@@%  #@@@@@@  @@@@@@*  %@@@@@
        @@@@@@#     @@@@@@@@@@@@@@  *@@@@@@@@@@@@@@@&  #@@@@@@@@@@@@@@@  @@@@@@@@@@@@@@@
        @@@@      @@@@@@@@@@@@(     (@@@@@@@@@@@#      /@@@@@@@@@@@@@    (@@@@@@@@@@@@
        
                                    Audio Uploader
    """);

    print(" ✔ Project: ", config["device"]["project_id"])
    print(" ✔ Config : ", config["device"]["config_id"])

    print(f" ✔ Device{'' if len(deviceIds) == 1 else 's'}: ")

    for deviceId in deviceIds:
        # count of filePathsToUpload containing the deviceId
        count = len([f for f in filePathsToUpload if deviceId in f])
        print(f"   -  {deviceId}    {count} file{ '' if count == 1 else 's'}")


    # Confim that the user wants to upload the files with a prompt

    print(f"\nYou are about to upload {len(filePathsToUpload)} file{'' if len(filePathsToUpload) == 1 else 's'}. Are you sure you want to continue? (y/n)")
    while True:
        userInput = input()
        if userInput.lower() == "y":
            break
        elif userInput.lower() == "n":
            print("Exiting...")
            exit(0)
        else:
            print("Please enter 'y' or 'n'")


    def upload_blob(client, bucket_name, source, dest, content_type=None):
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(dest)
        with open(source, "rb") as in_file:
            total_bytes = os.fstat(in_file.fileno()).st_size
            with tqdm.wrapattr(in_file, "read", total=total_bytes, miniters=1, desc="uploading to %s" % dest) as file_obj:
                blob.upload_from_file(
                    file_obj,
                    content_type=content_type,
                    size=total_bytes,
                )
                return blob


    deviceIdsSeen = []
    for filePath in filePathsToUpload:
        # Remove the args.folder prefix if there is one 
        remoteFile = filePath
        if args.folder: 
            remoteFile = filePath.replace(args.folder, "")
        
        # Add the proj_ prefix to the project ID
        remoteFile = remoteFile.replace(f"/{config['device']['project_id']}/", f"/proj_{config['device']['project_id']}/")
        remoteFile = remoteFile.replace("/audio/", "")
        # if remoteFile starts with audio/ remove it
        if remoteFile.startswith("audio/"):
            remoteFile = remoteFile[6:]

        upload_blob(storageClient, "bugg-audio-dropbox", filePath, remoteFile, "audio/mpeg")
    

        deviceId = remoteFile.split("/")[1]

        if deviceId not in deviceIdsSeen and len(filePathsToUpload) > 1:
            deviceIdsSeen.append(deviceId)
            # Confirm if the user is happy to continue. They may need to set the location for this new deviceId.
            print(f"\nNew device Id seen: '{deviceId}'\n\nYou may need to set the location for this device here: https://app.bugg.xyz/?bugg={deviceId}&tab=location")
            print(f"\nDo you want to continue? (y/n)")
            
            while True:
                userInput = input()
                if userInput.lower() == "y":
                    break
                elif userInput.lower() == "n":
                    print("Exiting...")
                    exit(0)
                else:
                    print("Please enter 'y' or 'n'")



    print("\nFiles uploaded successfully! 🚀")


# Run the main function
if __name__ == "__main__":
    main()






