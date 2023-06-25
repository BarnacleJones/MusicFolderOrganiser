import os
import logging
import mutagen
from mutagen import MutagenError
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from pydub.utils import mediainfo

#to run
#easiest to put within the folder you are tidying
#before running, install python and pip
#then run sudo pip install mutagen pydub
#then run sudo python3 musicOrganiser.py

# Configure logging
logging.basicConfig(filename='MusicOrganiserErrorLog.log', level=logging.ERROR)

# Start
print("Let's get this music organized!")

# Prompt for folder path or use the current folder
folder_choice = input("Do you want to use the current folder? (Y/N): ")
if folder_choice.lower() == "y":
    folder_path = os.path.dirname(os.path.abspath(__file__))
else:
    folder_path = input("Enter the path to the folder where the music is located: ")

# Check if the folder path is valid
if not os.path.isdir(folder_path):
    print("Invalid folder path. Exiting the script.")
    exit()

# Error handling function
def handle_error(file_path, error):
    error_message = f"Failed to process file '{file_path}': {error}"
    logging.exception(error_message)
    print(f"Error: {error_message}")

# Confirmation prompt
def confirm_action():
    response = input("Locked and loaded, ready to organise? (Y/N): ")
    return response.lower() == "y"

# Function to get metadata from audio file
def get_metadata(file_path):
    if file_path.endswith(".mp3"):
        try:
            tags = EasyID3(file_path)
            artist = tags.get("artist", [""])[0]
            album = tags.get("album", [""])[0]
            if not artist or not album:
                print("No tag information for {} found".format(file_path))
                print("You need to update the metadata functions for them to work")
                print("But if you continue the worst case scenario is the files don't get moved")
                continue_choice = input("Continue? (Y/N): ")
                if continue_choice.lower() == "y":
                    artist = tags.get("albumartist", [""])[0]
                    if not artist:
                        filename = os.path.basename(file_path)
                        artist, album = extract_metadata_from_filename(filename)
                        if not artist or not album:
                            artist, album = extract_metadata_from_properties(tags)
                    else:
                        exit()
            return artist, album
        except mutagen.MutagenError:
            # Handle the case when an error occurs during tag parsing
            return extract_metadata_from_filename(os.path.basename(file_path))
        except Exception as e:
            handle_error(file_path, e)
    elif file_path.endswith(".flac"):
        try:
            tags = FLAC(file_path)
            return tags.get("artist", [""])[0], tags.get("album", [""])[0]
        except Exception as e:
            handle_error(file_path, e)
    else:
        try:
            metadata = mediainfo(file_path)
            return metadata.get("artist", ""), metadata.get("album", "")
        except Exception as e:
            handle_error(file_path, e)

# Function to extract metadata from the file name
def extract_metadata_from_filename(filename):
    # Logic to extract artist and album from the file name
    # Customize this logic based on your file naming pattern
    # Example: artist_album_title.mp3
    parts = filename.split("_")
    if len(parts) >= 2:
        artist = parts[0]
        album = parts[1]
        return artist, album
    else:
        return "", ""

# Function to extract metadata from other available properties
def extract_metadata_from_properties(tags):
    # Logic to extract artist and album from other available properties
    # Customize this logic based on the properties available in your audio files
    artist = tags.get("artist", [""])[0]
    album = tags.get("album", [""])[0]
    return artist, album

# Function to create directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to move file to destination directory
def move_file(file_path, destination):
    new_file_path = os.path.join(destination, os.path.basename(file_path))
    os.rename(file_path, new_file_path)

# Function to organize the music files
def organize_music(folder_path):
    print("\nOrganizing music files...")
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith((".mp3", ".flac")):
                artist, album = get_metadata(file_path)
                if artist and album:
                    artist_directory = os.path.join(folder_path, artist)
                    album_directory = os.path.join(artist_directory, album)
                    create_directory(artist_directory)
                    create_directory(album_directory)
                    move_file(file_path, album_directory)
                    print(f"Moved: {file_path} -> {album_directory}")
                else:
                    print(f"Skipped: {file_path} (missing artist or album metadata)")

    print("\nMusic organization completed!")

# Prompt for confirmation
if confirm_action():
    organize_music(folder_path)
else:
    print("Operation canceled.")
