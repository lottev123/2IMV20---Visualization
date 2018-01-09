#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 11:26:49 2018

@author: hildeweerts
"""

import os
import pandas as pd
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError


""" 
-------------------
INITIALIZE API
-------------------
Get a token and set up spotify API
"""

""" Functions """
# Get authorisation token
def getToken():
    client_id = '980994ee3e504ad489ae2f0ff67edc4a'
    client_secret = '09ac800012264b788f6660a335ea731a'
    try:
        token = util.prompt_for_user_token('1111650679',None,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost:8888/callback')
    except (AttributeError, JSONDecodeError):
        os.remove(".cache-1111650679")
        token = util.prompt_for_user_token('1111650679',None,client_id=client_id,client_secret=client_secret,redirect_uri='http://localhost:8888/callback')
    return token

# Search track on Spotify and return a tuple with album, artist(s) and track id
def saveResults(result):
    albumID = result[0]['album']['uri']
    artistIDs = [x['uri'] for x in result[0]['artists']] #list of artist id's
    trackID = result[0]['uri']
    artistNames = [x['name'] for x in result[0]['artists']]
    trackName = result[0]['name']
    explicit = result[0]['explicit']
    popularity = result[0]['popularity']
    return albumID, artistIDs, trackID, artistNames, trackName, explicit, popularity

def searchTrack(artist, song):
    
    result = sp.search(q = 'artist:' + artist + ' track:' + song, type = 'track', limit = 1)['tracks']['items']
    if len(result) > 0:
        albumID, artistIDs, trackID, artistNames, trackName, explicit, popularity = saveResults(result)
    else: # search without stating song + artist
        result = sp.search(q = artist + ' ' + song, type = 'track', limit = 1)['tracks']['items']
    if len(result) > 0:
        albumID, artistIDs, trackID, artistNames, trackName, explicit, popularity = saveResults(result)
    else:
        return False, None, [None], None, [None], None, None, None
    return True, albumID, artistIDs, trackID, artistNames, trackName, explicit, popularity

# Get audio features given a list of trackIDs
def getTrackInfo(trackIDs):
    return sp.audio_features(trackIDs)

# Get artist info given a list of artist IDs
def getArtistInfo(artistIDs):
    return sp.artists(artistIDs)

def getAlbumInfo(albumIDs):
    return sp.albums(albumIDs)

def getRelatedArtists(artistIDs):
    return sp.artist_related_artists(artistIDs)
#%%
""" Initialize spotipy """
token = getToken()
sp = spotipy.Spotify(auth=token)
#%%
""" 
-------------------
RETRIEVE DATA
-------------------
Retrieve audio features of all songs (song_attributes)
Retrieve genre of all artists
"""

working_dir = '/Users/hildeweerts/2IMV20---Visualization/Assignment 2/Results/'
os.chdir(working_dir)

# read songs data
songs_3 = pd.read_csv('3_Songs.csv', engine = 'python')
#%%
""" retrieve audio features of all songs """
song_ids = songs_3.reset_index()['trackID']
song_attributes = pd.DataFrame()

# retrieve attributes in groups of 50 from API
for i in range(0, len(songs_3), 50):
    j = 50
    if ((i + 50) > len(songs_3)):
        j = len(songs_3) - i
    info = pd.DataFrame(getTrackInfo(filter(None, song_ids[i:i+j])))
    song_attributes = song_attributes.append(info)
    
# rename uri attribute and write to csv
song_attributes['trackID'] = song_attributes['uri']
song_attributes = song_attributes.drop('uri', axis=1)
song_attributes.to_csv('songs_attributes.csv')
#%%
""" retrieve artist features """
# load artist id's
songs_3a = songs_3.copy()
songs_3a['artistIDs'] = songs_3['artistIDs'].str.replace(']',"")
songs_3a['artistIDs'] = songs_3a['artistIDs'].str.replace('[',"")
songs_3a['artistIDs'] = songs_3a['artistIDs'].str.replace("'", "")
songs_3a['artistIDs'] = songs_3a['artistIDs'].str.split(', ')
artists = list(songs_3a['artistIDs'])
artistIDs = [y for x in artists for y in x]

artistIDs_unique = list(set(artistIDs))
artist_attributes = pd.DataFrame()

# retrieve attributes in groups of 50 from API
for i in range(0, len(artistIDs_unique), 50):
    j = 50
    if ((i + j) > len(artistIDs_unique)):
        j = len(artistIDs_unique) - i
    info = pd.DataFrame(getArtistInfo(artistIDs_unique[i:i+j])['artists'])
    artist_attributes = artist_attributes.append(info)

# rename uri attribute and write to csv
artist_attributes['artistID'] = artist_attributes['uri']
artist_attributes = artist_attributes.drop('uri', axis=1)
artist_attributes.to_csv('artists_attributes.csv')
#%%
""" retrieve album features """

album_ids = list(set(songs_3.reset_index()['albumID']))
album_attributes = pd.DataFrame()

# retrieve attributes in groups of 20 from API
num = 20
for i in range(0, len(album_ids), num):
    j = num
    if ((i + j) > len(album_ids)):
        j = len(album_ids) - i
    print(i)
    info = pd.DataFrame(getAlbumInfo(album_ids[i:i+j])['albums'])
    album_attributes = album_attributes.append(info)

# rename uri attribute and write to csv
album_attributes['albumID'] = album_attributes['uri']
album_attributes = album_attributes.drop('uri', axis=1)
album_attributes.to_csv('albums_attributes.csv')

#%%
""" Retrieve related artists """
songs_3a = songs_3.copy()
songs_3a['artistIDs'] = songs_3['artistIDs'].str.replace(']',"")
songs_3a['artistIDs'] = songs_3a['artistIDs'].str.replace('[',"")
songs_3a['artistIDs'] = songs_3a['artistIDs'].str.replace("'", "")
songs_3a['artistIDs'] = songs_3a['artistIDs'].str.split(', ')
artists = list(songs_3a['artistIDs'])
artistIDs = [y for x in artists for y in x]

artistIDs_unique = list(set(artistIDs))
related_artists = {}

# retrieve related artist info
for i in artistIDs_unique:
    info = getRelatedArtists(i)['artists']
    related_artists[i] = info
#%%
import pickle 

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
#%%
# save related artists dictionary
save_obj(related_artists, 'related_artists')