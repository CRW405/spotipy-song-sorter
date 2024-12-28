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
            try:
                results = spotify.next(results)
                tracks.extend([Track(item["track"]["id"], spotify)
                              for item in results["items"]])
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 429:
                    time.sleep(5)  # wait 5 seconds if rate limited
                    results = spotify.next(results)
                else:
                    raise e
        return tracks
