import spotipy
import csv
import time
import os
import json
# import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
import string

########################## TO DO ##########################
# 2. Sort CSV
#   - Sort by artist
#   - add option to sort by genre, maybe only include genres with specific amount of files
# 3. Convert CSV to playlist
#   - add artist genres to description
#   - add option to loop through all playlists in folder

# 4. Analyze playlist
#   - would require storing of genres and music data
#   - use pandas

###########################################################
# gets current path and creates needed filepaths
this_path = os.path.dirname(os.path.abspath(__file__))
output = os.path.join(this_path, "output")
cache = os.path.join(this_path, ".cache")
config = os.path.join(this_path, "config.json")

id = ""
secret = ""
redirect = "http://localhost:3000"
scope = "playlist-read-private playlist-read-collaborative user-library-read playlist-modify-public"
# setup^ ###########################################################################################


def writeConfig(id, secret):  # writes config with keys
    data = {
        "id": id,
        "secret": secret
    }
    with open(config, 'w') as file:
        json.dump(data, file)


if os.path.exists(config):  # reads config for keys
    with open(config, 'r') as file:
        configJson = json.load(file)
        id = configJson["id"]
        secret = configJson["secret"]
else:
    print("No config file found. Please enter client id and secret.")
    id = input("Enter client")
    secret = input("Enter secret")
    writeConfig(id, secret)


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=id, client_secret=secret, redirect_uri=redirect, scope=scope, cache_path=cache))
# config^ ###########################################################################################


def checkPath(path):  # checks if path exists, if not creates it
    if not os.path.exists(path):
        os.makedirs(path)
    return path


checkPath(output)  # ensures output folder exists


def sanitize(input):  # removes special characters from string
    input = input.replace(" ", "")  # removes spaces
    input = input.translate(str.maketrans(
        '', '', string.punctuation))  # removes punctuation
    return input


def idSplitter(string):  # splits id from url
    return string.split(r"/([^/]+/")[-1].split("?")[0]


# tools^ ##########################################################################################


def playlistToCSV(playlist):  # converts spotify playlist to csv of id, song name, artists
    artists = []  # stores artists for a track
    playlistInfo = sp.playlist(playlist)  # spotipy playlist object
    # sanitizes playlist name for file name
    playlistName = sanitize(playlistInfo["name"])

    os.makedirs(os.path.join(output, playlistName),
                exist_ok=True)  # creates folder for playlist
    # creates file path for csv
    newFile = os.path.join(output, playlistName, f"{playlistName}.csv")

    startTimer = time.time()  # starts timer

    try:
        with open(newFile, 'w', newline='', encoding='utf-8') as file:  # opens file for writing
            writer = csv.writer(file)  # creates csv writer object

            # gets 20 tracks from playlist, we do this this to save on bandwidth
            results = sp.playlist_tracks(playlist, limit=20)

            writer.writerow(["ID", "Song", "Artists"])  # writes header

            iteration = 0  # iteration counter

            while results:  # if there are results
                # prints iteration so that the user knows the program is running
                print(f"Running iteration: {iteration}...")

                for item in results['items']:  # loop through items in results
                    track = item['track']  # get track object from results

                    trackArtists = [artist['name']
                                    # gets all artists for a track
                                    for artist in track['artists']]
                    artists.extend(trackArtists)  # store artists

                    # write track id, name, and artists to csv
                    writer.writerow([track['id'], track['name'], trackArtists])

                if results['next']:  # if there are more results
                    time.sleep(5)  # sleep to avoid rate limiting

                    try:
                        results = sp.next(results)
                    except spotipy.exceptions.SpotifyException as e:  # if we have been rate limited
                        if e.http_status == 429:  # 429 is the status code for rate limiting
                            time.sleep(5)
                            results = sp.next(results)
                        else:
                            raise e
                    iteration += 1
                else:
                    results = None
            endTimer = time.time()
            dTime = endTimer - startTimer  # calculate time taken
            print(f"Done in {dTime:.2f} seconds with {iteration} iterations.")
    except Exception as e:
        print(f"Error: {e}")


# def sortCSV(csv):
#     basepath = os.path.dirname(csv)  # gets directory of parent csv

#     with open(csv, 'r', newline='', encoding='utf-8') as file:  # open csv
#         reader = csv.reader(file)

#         header = next(reader)  # skips header

#         data = [row for row in reader]  # reads data from csv

#         for row in data:
#             artists = row[2].split(",")  # splits artists into list

#             for artist in artists:
#                 artist = sanatize(artist)  # sanitizes artist name

#                 # creates path for artist folder
#                 path = os.path.join(basepath, artist)

#                 if not os.path.exists(path):
#                     with open(path, 'a')


def csvToPlaylist(csv):
    pass

# main functions ^ #########################################################################################


def main():
    on = True
    while on:
        menu = input("""
                    Spotipy PLaylist Sorter and Analyzer
                    ------------------------------------
                    1 - Convert playlist to CSV
                    2 - Sort CSV
                    3 - Convert CSV to playlist
                    4 - Sign in
                    ------------------------------------
                    """)
        if menu == "1":
            playlist = input("Enter playlist link: ")
            playlistToCSV(playlist)
        elif menu == "2":
            csv = input("Enter CSV file: ")
            # sortCSV(csv)
        elif menu == "3":
            csv = input("Enter CSV file: ")
            csvToPlaylist(csv)
        elif menu == "4":
            id = input("Enter client id: ")
            secret = input("Enter client secret: ")
            writeConfig(id, secret)
        else:
            on = False
            print("Goodbye!")
# menu^ ###########################################################################################


if __name__ == "__main__":
    main()
