
import json
import os
import sys
from datetime import datetime, time, timedelta

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from default_config import (_CLIENT_ID, _CLIENT_SECRET, _DATE_FORMAT,
                            _INDICATOR_PLAYLIST, _PROMOTOR_PLAYLISTS, _TRACK)


class Track:

    def __init__(self, title=None, album=None,
                 artists=None, date=None):
        self.title: str = title
        self.album: str = album
        self.artists: list = artists
        self.date: str = date
        self.promoter_playlists: Playlist = []
        self.indicator_playlist: Playlist = Playlist()

    def json_repr(self):
        return dict(title=self.title,
                    album=self.album,
                    artists=self.artists,
                    date=self.date.strftime(_DATE_FORMAT),
                    promoter_playlists=[x.json_repr()
                                        for x in self.promoter_playlists],
                    indicator_playlist=self.indicator_playlist.json_repr())


class Playlist:

    def __init__(self, name: str = None, added_at: str = None, followers: int = None):
        self.name = name
        self.added_at = added_at
        self.rank: int = None
        self.promoted_time: int = None
        self.followers = followers
        self.points: int = None

    def json_repr(self):
        return dict(name=self.name,
                    added_at=self.added_at.strftime(_DATE_FORMAT),
                    rank=self.rank,
                    promoted_time=self.promoted_time,
                    followers=self.followers,
                    points=self.points)


def get_playlist_info(playlist_URI: str):
    results = request_playlist(playlist_URI)
    track_added_at = find_track_in_playlist(track, results['tracks'])
    if track_added_at:
        play_list_name = results['name']
        added_at = track_added_at
        followers = results['followers']['total']
        playlist = Playlist(play_list_name, added_at, followers)
        return playlist
    return


def request_playlist(playlist):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=_CLIENT_ID,
                                                               client_secret=_CLIENT_SECRET))
    return sp.playlist(playlist)


def find_track_in_playlist(track: Track, track_list: list):
    for item in track_list['items']:
        track_item = item['track']
        curr_track = Track()
        curr_track.title = track_item['name']
        curr_track.album = track_item['album']['name']
        curr_track.artists = [x['name'] for x in track_item['artists']]
        if track.title == curr_track.title\
                and track.album == curr_track.album\
                and track.artists == curr_track.artists:
            added_at = datetime.strptime(item['added_at'], _DATE_FORMAT)
            return added_at
    return


def rank_playlists():
    # number of followers each 100 gives a point
    # number of hours promoting each day gives a point
    # hardcoded but it can be a parameter

    for playlist in track.promoter_playlists:
        followers_points = playlist.followers // 1000

        promoted_time = track.indicator_playlist.added_at - playlist.added_at
        promoted_time = int(promoted_time.total_seconds())
        playlist.promoted_time = promoted_time if promoted_time > 0 else 0
        time_promoting_points = playlist.promoted_time // 3600
        playlist.points = followers_points + time_promoting_points

    rank = 1
    for playlist in sorted(track.promoter_playlists, key=lambda x: x.followers, reverse=True):
        playlist.rank = rank
        rank += 1


def main():
    for item in _PROMOTOR_PLAYLISTS:
        promoter_playlist = get_playlist_info(item)
        if promoter_playlist:
            track.promoter_playlists.append(promoter_playlist)

    indicator_playlist = get_playlist_info(_INDICATOR_PLAYLIST)
    if indicator_playlist:
        track.indicator_playlist = indicator_playlist

    rank_playlists()
    write_results()


def write_results():
    with open('results.json', 'a') as f:
        x = json.dumps(track.json_repr()) + '\n'
        f.write(x)


if __name__ == "__main__":
    print('Starting process')
    now = datetime.utcnow()
    track = Track(_TRACK['title'], _TRACK['album'], _TRACK['artists'], now)
    main()
    print('Process completed')
