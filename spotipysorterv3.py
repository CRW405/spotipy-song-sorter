import spotipy
import csv
import time
import os
import json
from spotipy.oauth2 import SpotifyOAuth
import string
import time


class Filepath:  # class to store filepaths
    def __init__(self):
        self.this_path = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.this_path, "output")
        self.cache_path = os.path.join(self.this_path, ".cache")
        self.config_path = os.path.join(self.this_path, "config.json")


class Config:  # class to store and get config data
    def __init__(self):
        self.filepath = Filepath()
        self.config_file = self.filepath.config_path
        self.id = ""
        self.secret = ""
        self.redirect = "http://localhost:3000"
        self.scope = "playlist-read-private playlist-read-collaborative user-library-read playlist-modify-public"
        self.cache_path = self.filepath.cache_path
        self.readConfig()

    def writeConfig(self, id, secret):
        data = {
            "id": id,
            "secret": secret
        }
        with open(self.config_file, 'w') as file:
            json.dump(data, file)

    def readConfig(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                configJson = json.load(file)
                self.id = configJson["id"]
                self.secret = configJson["secret"]
        else:
            print("No config file found. Please enter client id and secret.")
            self.id = input("Enter client id: ")
            self.secret = input("Enter secret: ")
            self.writeConfig(self.id, self.secret)


class Tool:  # class to store Tool
    def __init__(self):
        pass

    def checkPath(self, path):  # checks if path exists, if not creates it
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def sanitize(self, input):  # removes special characters from string
        input = input.replace(" ", "")  # removes spaces
        input = input.translate(str.maketrans(
            '', '', string.punctuation))  # removes punctuation
        return input

    def idSplitter(self, string):  # splits id from url
        return string.split(r"/([^/]+/")[-1].split("?")[0]

    def clearOutput():
        for root, dirs, files in os.walk(Filepath.output):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))


class Playlist:  # class to store playlist data
    def __init__(self, id, spotify):
        self.id = ""
        self.name = ""
        self.tracks = []
        self.Playlist(id, spotify)

    def Playlist(self, id, spotify):
        self.id = id
        self.spotify = spotify
        self.name = spotify.playlist(self.id)["name"]

        self.tracks = self.get_tracks(spotify, id)

    def get_tracks(self, spotify, id):
        tracks = []
        results = spotify.playlist_tracks(id, limit=20)

        tracks.extend([Track(item["track"]["id"], spotify)
                      for item in results["items"]])
        while results["next"]:
            results = spotify.next(results)
            tracks.extend([Track(item["track"]["id"], spotify)
                          for item in results["items"]])
        return tracks


class Track:  # class to store track data
    def __init__(self, id, spotify):
        self.id = ""
        self.name = ""
        self.artists = []
        self.Track(id, spotify)

    def Track(self, id, spotify):
        self.id = id
        self.name = spotify.track(self.id)["name"]
        self.artists = spotify.track(self.id)["artists"]


class Convert:
    def __init__(self):
        self.playlist_to_csv()

    def playlist_to_csv(self, playlist, path):
        with open(path + playlist.name + ".csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Id", "Name", "Artists"])
            for track in playlist.tracks:
                writer.writerow([track.name, track.name, track.artists])

    def csv_to_playlist(self, path, name):
        with open(path + name + ".csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                print(row)


def main():
    config = Config()
    tool = Tool()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(  # creates spotipy object
        client_id=config.id, client_secret=config.secret, redirect_uri=config.redirect, scope=config.scope, cache_path=config.cache_path))
    playlist_id = tool.idSplitter(input("Enter playlist id: "))
    timeStart = time.time()
    playlist = Playlist(playlist_id, sp)
    timeEnd = time.time()
    for track in playlist.tracks:
        print(track.name)
    print(f"Time taken: {(timeEnd - timeStart):.2f}")

    # log
    # 134.91
    # 134.91
    
    # expected
    # 56.61.


if __name__ == "__main__":
    main()
