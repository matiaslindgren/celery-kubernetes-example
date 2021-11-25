import os

from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import lyricsgenius
import Levenshtein as lv

import threading
import time
import datetime

import re

import shutil
from google.cloud import storage

import gc
from dotenv import load_dotenv

load_dotenv()
BUCKET_NAME = 'central-bucket-george'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ["SPOTIFY_client_id"],
                                                           client_secret=os.environ['SPOTIFY_client_secret'], ))

genius = lyricsgenius.Genius(os.environ['GENIUS_SECRET'], timeout=5, retries=3)
genius.response_format = 'plain'
genius.skip_non_songs = True  # Include hits thought to be non-songs (e.g. track lists)
# genius.excluded_terms = []
genius.verbose = False


def write_file_blob(bucket_name: str, path: str, file_name: str) -> None:
    # Instantiate a CGS client
    client = storage.Client()

    # Retrieve all blobs with a prefix matching the folder
    bucket = client.get_bucket(bucket_name)
    # Create a new blob and upload the file's content.
    my_file = bucket.blob(f'{path}/{file_name}')
    my_file.upload_from_filename(file_name)
    return None


def clean_lyrics(s: str) -> str:
    # currently unused the sq_brackets with [Verse 1] are useful for generation
    # for now the only cleaning i do is remove everything in the square brackets.
    # i have concerns about the repeating chorus and interlude parts but i have to get a baseline first
    # possible idea to replace all the numbers with there words
    """
    pip install num2words
    from num2words import num2words

    # Most common usage.
    print(num2words(36))
    """

    '''
    pip install langdetect
    from langdetect import detect
    if detect(cleaner_song) != 'en':
    '''

    s = s.replace('EmbedShare URLCopyEmbedCopy', '')
    # fixed the newline to save to csv correctly
    s = s.replace('\n', '\\n')
    pattern = r'\[.*?\]'
    r = re.sub(pattern, '', s)
    return r


def simple_clean(lyrics: str) -> str:
    """
    removes the last line that is not song
    replaces all newline characters as these characters would be removed during tokenizing
    :param lyrics: raw lyrics
    :return: cleaner lyrics
    """
    lyrics = lyrics.replace('EmbedShare URLCopyEmbedCopy', '')
    # fixed the newline to save to csv correctly
    lyrics = lyrics.replace('\n', '\\n')
    lyrics = lyrics.rstrip('0123456789')
    return lyrics


def make_file_name(found_song: object) -> str:
    """
    makes a more command line friendly file name
    :param found_song:
    :return: what that file should be named
    """

    def remove_space_slash(st):
        st = st.replace('/', '-')
        st = st.replace(' ', '_')
        return st

    art = remove_space_slash(found_song.artist)
    title = remove_space_slash(found_song.title)
    return f'{title}-{art}.txt'


class MyJob():
    def __init__(self, user: str, playlist_id: str, project_name: str, debug: bool = False,
                 num_threads: int = 4, threshold: int = 5):
        """
        This is now an object

        :param user: user to specify which "folder" in the bucket to save it to
        :param playlist_id: spotify playlist id (the end bit of the url)
        :param project_name: Model name user makes when setting playlist id on profile dashboard
        :param threshold: letter distance threshold for what should be flagged as a warning
        :param debug:
        """
        self.user = user
        self.playlist_id = playlist_id
        self.project_name = project_name
        self.num_threads = num_threads
        self.threshold = threshold
        self.debug = debug

        self.status = 'starting'
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.data = None  # have the master found failed and warning list for the job?

    def __repr__(self):
        return str(vars(self))

    def __str__(self):
        return str(vars(self))

    def to_dict(self):
        d = vars(self).copy()
        return d

    def get_spotify_playlist(self) -> (list, str):
        """
        Gets all the songs from a spotify playlist from the spotify api
        :return: playlist, playlist_name
        """
        pl_id = f'spotify:playlist:{self.playlist_id}'
        results = sp.playlist(pl_id)
        playlist_name = results['name']
        offset = 0

        # getting all the songs in the spotify playlist
        playlist = []
        while True:
            response = sp.playlist_items(pl_id,
                                         offset=offset,
                                         fields='items.track.name,items.track.artists.name,total',
                                         additional_types=['track'])
            if len(response['items']) == 0:
                break

            t = response['items']
            offset = offset + len(response['items'])
            print(offset, "/", response['total'])

            for spotify_song in range(len(t)):
                song, artists = t[spotify_song]['track']['name'], t[spotify_song]['track']['artists'][0]['name']
                playlist.append({'song': song, 'artist': artists})
        print(f"{playlist_name}: {len(playlist)}")
        return playlist, playlist_name

    def match_song(self, playlist: list, index: int, result: list) -> None:
        """
        matches spotify song titles and artists to genius songs.
        a found match is a song that's within the letter distance threshold.
        a song will be flagged with a warning if something is found but outside the threshold
        a song will fail if the genius api returns None
        and is then saved to its respected list

        :param playlist: list of spotify songs
        :param index: thread index
        :param result: cant return from thread so saves it in result[index]
        :return: None but saves work in result[(thread)index]
        """

        found = []
        failed = []
        # TODO going to have a problem when the user want to suppress the warning because im only saving the search
        warnings = []
        for spotify_song in playlist:

            if self.debug:
                print(f'{index} SEARCHING : {spotify_song["song"]}')

            song_search = genius.search_song(spotify_song['song'], spotify_song['artist'])

            if song_search is not None:
                if self.debug:
                    print(f"SONG SEARCH : {song_search.title} {song_search.artist}")

                distance = lv.distance(spotify_song['song'], song_search.title)

                # check for warning
                if distance >= self.threshold:
                    if self.debug:
                        print('WARNING')
                    warnings.append(f'{song_search.title} by {song_search.artist}')

                else:
                    if self.debug:
                        print("FOUND")
                    found.append(song_search)
            else:
                if self.debug:
                    print(f'SONG SEARCH : NONE')
                failed.append(f"{spotify_song['song']} by {spotify_song['artist']}")

            if self.debug:
                print('-' * 20)

        # return found, warnings, failed
        result[index] = {"found": found, "warnings": warnings, "failed": failed}

    def make_threads(self, playlist: list) -> (list, list, list):
        """
        makes threads to speed up the matching step.
        each thread gets a chunk of the playlist does its work to match the song and saves its partial lists to results
        which is then combined after all the threads finish to return the final lists
        :param playlist:
        :return:
        """
        found = []
        failed = []
        warnings = []

        # helper function to split lists into n chunks of similar length if not equal
        def chunk_it(seq, num):
            avg = len(seq) / float(num)
            out = []
            last = 0.0

            while last < len(seq):
                out.append(seq[int(last):int(last + avg)])
                last += avg

            return out

        part = chunk_it(playlist, self.num_threads)
        results = [None] * self.num_threads

        threads = list()
        for index in range(self.num_threads):
            x = threading.Thread(target=self.match_song, args=(part[index], index, results))
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()
            # thread finished add get there work and combine it back together
            # found += results[index]["found"] TypeError: 'NoneType' object is not subscriptable
            if results[index]:
                found += results[index]["found"]
                warnings += results[index]["warnings"]
                failed += results[index]["failed"]

        total = len(playlist)
        warns = len(warnings)
        fails = len(failed)
        # assert success_list = total-warns-fails ;)

        print(f"Warnings: {warns}/{total}")
        print(f'Failed:{fails}/{total}')
        print(f'Success:{total - warns - fails}/{total}')
        return found, warnings, failed

    def save_lyrics_to_drive(self, found: list, bucket_name: str) -> None:
        """
        saves all found song lyrics to file then zip and upload to google storage bucket then delete folder and zip file
        :param bucket_name: which bucket
        :param found: songs list
        :return: nothing
        """
        # the file structure of a users will be
        # /User_Jack
        #   /Project_Name
        #       /Data
        #           playlist_id.zip
        #       /Model

        # This is instantiating a new project
        os.mkdir(f'{self.playlist_id}/')
        for song in found:
            clean_song = simple_clean(song.lyrics)
            file_name = make_file_name(song)
            path = f'{self.playlist_id}/{file_name}'
            with open(path, 'w+') as fp:
                fp.write(clean_song)

        shutil.make_archive(f"{self.playlist_id}", "zip", f"{self.playlist_id}")
        write_file_blob(bucket_name, f'{self.user}/{self.project_name}/Data', f'{self.playlist_id}.zip')
        shutil.rmtree(self.playlist_id)
        os.remove(f"{self.playlist_id}.zip")

    def big_function(self) -> None:
        """
        bringing it all together
        :return: the songs titles of the found songs
        """
        # start_time = datetime.datetime.now()

        self.status = 'Getting Playlist'
        # getting playlist from spotify
        playlist, playlist_name = self.get_spotify_playlist()

        self.status = 'Matching Songs'
        found, warnings, failed = self.make_threads(playlist)

        self.status = 'Saving Lyrics'
        self.save_lyrics_to_drive(found, BUCKET_NAME)

        # was having some memory issues before when trying to save to TempFiles
        # which doesnt work with cloud run as it has no storage and saves everything in ram keeping gc bc why not
        gc.collect()
        found_song_titles = [str(song.title) for song in found]

        self.end_time = datetime.datetime.now()
        self.status = 'Done'
        print("--- %s seconds ---" % (self.end_time - self.start_time))
        self.data = {'found': found_song_titles, 'warnings': warnings, 'failed': failed}
        return None


# TODO let the user choose to suppress the warning or add them to failed
'''
def fix_warnings():

ans = ''
for search, found in zip(warning_list_search,warning_list_found):
  print(f'{search["song"]} , {found.title}')
  while ans.lower() != 'y' and ans.lower() != 'n':
    ans = input('is this the correct song? y/n (anything else for lyrics)')
    print(ans)
    if ans.lower() == 'y':
      success_list.append(found)
    elif ans.lower() == 'n':
      failed_list.append(search)
    else:
      print(found.lyrics)

  ans = ''
'''

# TODO fix BROKEN cant use link

# let the user add the genius url to the correct lyrics
# let the user add custom lyrics whether it be there own or the correct lyrics from another website

'''
def fix_failed();

for fail in failed_list:
  ans = input(f'Enter a genius url for {fail["song"]} by {fail["artist"]} or nothing to skip')
  #example url https://genius.com/Johnny-cash-folsom-prison-blues-lyrics
  if ans == '':
    pass
  else:
    if 'genius.com/' in ans:
      search = ans[ans.index('genius.com/'):]
      search = search.replace('genius.com/', '')
      search = search.replace('-', ' ')
      print(search)
      song = genius.search_song(search)
      confirm = input(f'got song {song.title} by {song.artist} is this correct')
      if confirm.lower() == 'y':
        print('adding song')
        success_list.append(song)
      else:
        print('not adding')
    else:
      print(f'{ans} not a valid genius url')





print(warning_list_search)
print(failed_list)
print(len(success_list))
'''

