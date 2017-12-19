#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 11:22:33 2017

@author: hildeweerts
"""

#%%
import os
import pandas as pd
import spotipy
import spotipy.util as util
from json.decoder import JSONDecodeError

working_dir = '/Users/hildeweerts/Desktop/TUe/2IMV20 Visualization/Assignment 2/top40'
os.chdir(working_dir)

""" 
-------------------
IMPORT DATA 
-------------------
"""

charts = {}
import glob
for file in glob.glob("*.csv"):
    if 'chart' in file:
        file_split = file.split('_') 
        year = file_split[1] #find year
        week = file_split[3][:-4] #find week
        file_df = pd.read_csv(file, delimiter = '\t') #import dataframe
        charts[year+week] = file_df #add to charts
        
# Import songs and artists
artists = pd.read_csv('artists.csv', delimiter  = '\t')
songs = pd.read_csv('songs.csv', delimiter  = '\t')

#%%
""" 
-------------------
PREPARE DATA
-------------------
Split each artist name
Split each song name
Create dataframe to search for songs
"""

""" Split rules """
namesArtists = [None] * len(artists)
splitrules_artists = ["ft.", "featuring", "-", "feat.", ",", "x", "with"]

for index, row in artists.iterrows():
    splittedArtist = []
    for element in row["name"].split("/"):
        splittedArtist.append(element)
    for splitrule in splitrules_artists:
        if (splitrule) in row["name"].split("/")[0]:
            splittedArtist.append(row["name"].split("/")[0].split(splitrule)[0]) 
    namesArtists[index] = splittedArtist

artists["listOfNames"] = namesArtists

namesSongs = [None] * len(songs)
splitrules_songs = ["("]

translation_table = dict.fromkeys(map(ord, '()'), None) #necessary to remove the ( and ) characters in a string

for index, row in songs.iterrows():
    splittedSong = []
    for element in row["name"].split("/"):
        splittedSong.append(element)
    firstElement = row["name"].split("/")[0]
    for splitrule in splitrules_songs:
        if (splitrule) in firstElement:
            splittedSong.append(firstElement.split(splitrule)[0])
    if (firstElement.find("(")!= -1): #then, firstElement contains (
            splittedSong.append(firstElement[firstElement.find("(")+1:firstElement.find(")")]) #add part between brackets to list of songs
            splittedSong.append(firstElement.translate(translation_table)) # add string, but then without the brackets
    namesSongs[index] = splittedSong

songs["listOfNames"] = namesSongs
#%%
""" Create dataframe for API """
songs['artist_id'] = ''

# find artist_id of a song
for key, value in charts.items():
    for index, row in value.iterrows():
        song_id = row['song_id']
        if songs.ix[song_id, 'artist_id'] == '':
            artist_id = row['artist_id']
            songs.ix[song_id, 'artist_id'] = artist_id

# find name of artist for each song using artist_id
songs_artists = songs.merge(artists, left_on='artist_id', right_on='artist_id', suffixes=['_song', '_artist'])
#%%
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
def searchTrack(artist, song):
    
    result = sp.search(q = 'artist:' + artist + ' track:' + song, type = 'track', limit = 1)['tracks']['items']
    if len(result) > 0:
        albumID = result[0]['album']['uri']
        artistIDs = [x['uri'] for x in result[0]['artists']] #list of artist id's
        trackID = result[0]['uri']
    else: # search without stating song + artist
        result = sp.search(q = artist + ' ' + song, type = 'track', limit = 1)['tracks']['items']
    if len(result) > 0:
        albumID = result[0]['album']['uri']
        artistIDs = [x['uri'] for x in result[0]['artists']] #list of artist id's
        trackID = result[0]['uri']
    else:
        print('Could not find anything...')
        return False, None, [None], None
    print('We found something!')
    return True, albumID, artistIDs, trackID 

# Get audio features given a list of trackIDs
def getTrackInfo(trackIDs):
    return sp.audio_features(trackIDs)

# Get artist info given a list of artist IDs
def getArtistInfo(artistIDs):
    return sp.artists(artistIDs)
#%%
""" Initialize spotipy """
token = getToken()
sp = spotipy.Spotify(auth=token)
#%%

""" 
-------------------
SEARCH SONG 
-------------------
Search for each song in the spotify API
"""
albumIDlist = []
artistIDslist = []
trackIDlist = []

# for each song we try to find the albumID, artistID(s) and trackID
for key, value in songs_artists[1:30].iterrows():
    for song in value['listOfNames_song']:
        for artist in value['listOfNames_artist']:
            print(song)
            print(artist)
            result = searchTrack(artist, song)
            if (result[0]):
                break #if a result is found, we can stop the loop
                break
    Bool, albumID, artistIDs, trackID = result
    albumIDlist.append(albumID)
    artistIDslist.append(artistIDs)
    trackIDlist.append(trackID)
#%%
print(song)
print(artist)
result = searchTrack(artist, song)
#print(result)
#%%

    #%%
list(songs_artists)
#%%
""" 
-------------------
RETRIEVE DATA
-------------------
Retrieve audio features of all songs
Retrieve genre of all artists
"""