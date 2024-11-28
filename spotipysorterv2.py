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
#   - Sort by artist - done
#       - minimum number of entries before file is created, eg if artist has 1 song, don't create file, if artist has n songs, create file
#   - add option to sort by genre, maybe only include genres with specific amount of files
# 3. Convert CSV to playlist - done
#   - add artist genres to description
#   - add option to loop through all playlists in folder
#   -

# 4. Analyze playlist
#   - would require storing of genres and music data
#   - use pandas

# 5. Refactor code !!!!!!!!!!

# 6. add clear output folder option - done
#    - ask if to delete parent files

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
                    time.sleep(2)  # sleep to avoid rate limiting

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


def sortCSV(parentCsv):
    basepath = os.path.dirname(parentCsv)  # gets directory of parent csv

    with open(parentCsv, 'r', newline='', encoding='utf-8') as file:  # open csv
        reader = csv.reader(file)

        header = next(reader)  # skips header

        data = [row for row in reader]  # reads data from csv

        for row in data:  # iterates through rows in parent csv
            artists = row[2].split(",")  # splits artists into list

            for artist in artists:  # iterates through each artist for a song
                artist = sanitize(artist)  # sanitizes artist name

                # creates path for artist folder
                path = os.path.join(basepath, f"{artist}.csv")

                if not os.path.exists(path):  # checks if artist folder exists
                    # creates file if it doesn't exist
                    with open(path, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)  # creates csv writer object
                        writer.writerow(header)  # writes header
                        writer.writerow(row)  # writes row
                        file.close()  # closes file
                else:  # if artist folder exists
                    with open(path, 'a', newline='', encoding='utf-8') as file:  # append
                        writer = csv.writer(file)
                        writer.writerow(row)
                        file.close()


def csvToPlaylist(sourceCsv):
    artist = os.path.basename(sourceCsv).split(
        ".")[0]  # gets artist name from csv
    sp.user_playlist_create(
        sp.me()["id"], artist, public=True)  # creates playlist
    playlist_id = sp.current_user_playlists(
    )["items"][0]["id"]  # gets playlist id
    with open(sourceCsv, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)

        header = next(reader)

        data = [row for row in reader]

        for row in data:
            sp.playlist_add_items(playlist_id, [row[0]])


def clearOutput():
    for root, dirs, files in os.walk(output):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))

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
                    5 - Clear output folder
                    ------------------------------------
                    """)
        if menu == "1":
            playlist = input("Enter playlist link: ")
            playlistToCSV(playlist)
        elif menu == "2":
            csv = input("Enter CSV file: ")
            sortCSV(csv)
        elif menu == "3":
            csv = input("Enter CSV file: ")
            csvToPlaylist(csv)
        elif menu == "4":
            id = input("Enter client id: ")
            secret = input("Enter client secret: ")
            writeConfig(id, secret)
        elif menu == "5":
            clearOutput()
        else:
            on = False
            print("Goodbye!")
# menu^ ###########################################################################################


if __name__ == "__main__":
    main()
