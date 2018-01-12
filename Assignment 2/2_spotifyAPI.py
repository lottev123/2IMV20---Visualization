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

#working_dir = '/Users/hildeweerts/Desktop/TUe/2IMV20 Visualization/Assignment 2/'
#os.chdir(working_dir)
#%%
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
splitrules_songs = ["(", "-"]

translation_table = dict.fromkeys(map(ord, '()'), None) #necessary to remove the ( and ) characters in a string

for index, row in songs.iterrows():
    splittedSong = []
    for element in row["name"].split("/"):
        splittedSong.append(element)
    firstElement = row["name"].split("/")[0]
    for splitrule in splitrules_songs:
        if (splitrule) in firstElement:
            if (splitrule) in firstElement[0]:  #this means that the song starts with a bracket (see id = 152)
                break
            splittedSong.append(firstElement.split(splitrule)[0])
    if (firstElement.find("(")!= -1): #only then, firstElement contains (
            splittedSong.append(firstElement[firstElement.find("(")+1:firstElement.find(")")]) #add part between brackets to list of songs
            splittedSong.append(firstElement.translate(translation_table)) # add string, but then without the brackets
    # Remove [EP] from song title
    splittedSong = [x.replace(" [EP]", "") for x in splittedSong]
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
artistNameslist = []
trackNamelist = []
explicitlist = []
popularitylist = []

i = 0
# for each song we try to find the albumID, artistID(s) and trackID
for key, value in songs_artists[10781:13837].iterrows():
    i = i + 1
    print(i)
    for song in value['listOfNames_song']:
        for artist in value['listOfNames_artist']:
            result = searchTrack(artist, song)
            if result[0]:
                break #if a result is found, we can stop the loop
        if result[0]:
            break
    Bool, albumID, artistIDs, trackID, artistNames, trackName, explicit, popularity = result
    if not Bool:
        print('Nothing found for song:')
        print('\t' + str(value['name_song']))
        print('\t' + str(value['name_artist']))
    albumIDlist.append(albumID)
    artistIDslist.append(artistIDs)
    trackIDlist.append(trackID)
    artistNameslist.append(artistNames)
    trackNamelist.append(trackName)
    explicitlist.append(explicit)
    popularitylist.append(popularity)
    #%%
""" 
-------------------
Ad hoc dealing with results
-------------------
Search for each song in the spotify API
"""
songs_artists1000['artistnames']= artistNameslist
songs_artists1000['trackName'] = trackNamelist
songs_artists1000['trackID'] = trackIDlist
songs_artists1000['albumID'] = albumIDlist
songs_artists1000['artistIDs'] = artistIDslist
songs_artists1000['explicit'] = explicitlist
songs_artists1000['popularity'] = popularitylist
#%%
notfound = songs_artists1000[songs_artists1000['trackName'].isnull()]
notfound = notfound.append(songs_artists.loc[10780])
notfound = notfound.drop(['artistnames', 'trackName', 'trackID', 'albumID', 'artistIDs', 'explicit', 'popularity'], 1)
#%%
# export found results to csv
songs_artists1000.to_csv('firstResults.csv') # does not include song index 10780 (Country Grammar (Hot S+++), Nelly)
# all songs that were not found
notfound.to_csv('firstNotFound.csv')
#%%
""" 
-------------------
DATA PREP 2
-------------------
"""

namesArtists = [None] * len(notfound)
splitrules_artists = ["ft.", "featuring", "-", "feat.", ",", "x", "with", '&', 'and', 'en']

for index, row in notfound.reset_index().iterrows():
    splittedArtist = []
    for element in row["name_artist"].split("/"):
        splittedArtist.append(element)
    for splitrule in splitrules_artists:
        if (splitrule) in row["name_artist"].split("/")[0]:
            splittedArtist.append(row["name_artist"].split("/")[0].split(splitrule)[0]) 
            splittedArtist.append(row["name_artist"].split("/")[0].split(splitrule)[1]) 
    if '((' in row["name_artist"].split("/")[0]:
        splittedArtist.append(row["name_artist"].split("/")[0].split('((')[0]) 
    namesArtists[index] = splittedArtist

notfound["listOfNames2_artists"] = namesArtists

namesSongs = [None] * len(notfound)
splitrules_songs = ["(", "-"]

translation_table = dict.fromkeys(map(ord, '()'), None) #necessary to remove the ( and ) characters in a string

for index, row in notfound.reset_index().iterrows():
    splittedSong = []
    for element in row["name_song"].split("/"):
        splittedSong.append(element)
    firstElement = row["name_song"].split("/")[0]
    for splitrule in splitrules_songs:
        if (splitrule) in firstElement:
            if (splitrule) in firstElement[0]:  #this means that the song starts with a bracket (see id = 152)
                break
            splittedSong.append(firstElement.split(splitrule)[0])
    if (firstElement.find("(")!= -1): #only then, firstElement contains (
            splittedSong.append(firstElement[firstElement.find("(")+1:firstElement.find(")")]) #add part between brackets to list of songs
            splittedSong.append(firstElement.translate(translation_table)) # add string, but then without the brackets
    # Remove [EP] from song title
    splittedSong = [x.replace(" [EP]", "") for x in splittedSong]
    namesSongs[index] = splittedSong

notfound["listOfNames_songs2"] = namesSongs

#%%
""" 
-------------------
SEARCH ROUND 2
-------------------
"""
albumIDlist1 = []
artistIDslist1 = []
trackIDlist1 = []
artistNameslist1 = []
trackNamelist1 = []
explicitlist1 = []
popularitylist1 = []

i = 0
# for each song we try to find the albumID, artistID(s) and trackID
for key, value in notfound.iterrows():
    i = i + 1
    print(i)
    for song in value['listOfNames_songs2']:
        for artist in value['listOfNames2_artists']:
            song = song.replace('+', ' ').replace('*', ' ')
            artist = artist.replace('+', ' ').replace('*', ' ').replace('-', ' ')
            result = searchTrack(artist, song)
            if result[0]:
                break #if a result is found, we can stop the loop
        if result[0]:
            break
    Bool, albumID, artistIDs, trackID, artistNames, trackName, explicit, popularity = result
    if not Bool:
        print('Nothing found for song:')
        print('\t' + str(value['name_song']))
        print('\t' + str(value['name_artist']))
    albumIDlist1.append(albumID)
    artistIDslist1.append(artistIDs)
    trackIDlist1.append(trackID)
    artistNameslist1.append(artistNames)
    trackNamelist1.append(trackName)
    explicitlist1.append(explicit)
    popularitylist1.append(popularity)
        
#%%
notfound['artistnames']= artistNameslist1
notfound['trackName'] = trackNamelist1
notfound['trackID'] = trackIDlist1
notfound['albumID'] = albumIDlist1
notfound['artistIDs'] = artistIDslist1
notfound['explicit'] = explicitlist1
notfound['popularity'] = popularitylist1
#%%

secondNotFoundAdapted = secondNotFound.drop([
 'listOfNames_song',
 'listOfNames_artist',
 'artistnames',
 'trackName',
 'trackID',
 'albumID',
 'artistIDs',
 'explicit',
 'popularity'], axis = 1)
#%%
""" 
-------------------
DATA PREP 3
-------------------
"""

namesArtists = [None] * len(secondNotFoundAdapted)
splitrules_artists = ["ft.", "featuring", "-", "feat.", ",", "x", "with", '&', 'and', 'en']

for index, row in secondNotFoundAdapted.reset_index().iterrows():
    splittedArtist = []
    for element in row["name_artist"].split("/"):
        splittedArtist.append(element)
    for splitrule in splitrules_artists:
        if (splitrule) in row["name_artist"].split("/")[0]:
            splittedArtist.append(row["name_artist"].split("/")[0].split(splitrule)[0]) 
            splittedArtist.append(row["name_artist"].split("/")[0].split(splitrule)[1]) 
    if '((' in row["name_artist"].split("/")[0]:
        splittedArtist.append(row["name_artist"].split("/")[0].split('((')[0]) 
    namesArtists[index] = splittedArtist

secondNotFoundAdapted["listOfNames2_artists"] = namesArtists

namesSongs = [None] * len(secondNotFoundAdapted)
splitrules_songs = ["(", "-"]

translation_table = dict.fromkeys(map(ord, '()'), None) #necessary to remove the ( and ) characters in a string

for index, row in secondNotFoundAdapted.reset_index().iterrows():
    splittedSong = []
    for element in row["name_song"].split("/"):
        splittedSong.append(element)
    firstElement = row["name_song"].split("/")[0]
    for splitrule in splitrules_songs:
        if (splitrule) in firstElement:
            if (splitrule) in firstElement[0]:  #this means that the song starts with a bracket (see id = 152)
                break
            splittedSong.append(firstElement.split(splitrule)[0])
    if (firstElement.find("(")!= -1): #only then, firstElement contains (
            splittedSong.append(firstElement[firstElement.find("(")+1:firstElement.find(")")]) #add part between brackets to list of songs
            splittedSong.append(firstElement.translate(translation_table)) # add string, but then without the brackets
    # Remove [EP] from song title
    splittedSong = [x.replace(" [EP]", "") for x in splittedSong]
    namesSongs[index] = splittedSong

secondNotFoundAdapted["listOfNames_songs2"] = namesSongs
#%%
""" 
-------------------
SEARCH ROUND 3
-------------------
"""
albumIDlist2 = []
artistIDslist2 = []
trackIDlist2 = []
artistNameslist2 = []
trackNamelist2 = []
explicitlist2 = []
popularitylist2 = []

i = 0
# for each song we try to find the albumID, artistID(s) and trackID
for key, value in secondNotFoundAdapted.iterrows():
    i = i + 1
    print(i)
    for song in value['listOfNames_songs2']:
        for artist in value['listOfNames2_artists']:
            song = song.replace('+', ' ').replace('*', ' ')
            artist = artist.replace('+', ' ').replace('*', ' ').replace('-', ' ')
            result = searchTrack(artist, song)
            if result[0]:
                break #if a result is found, we can stop the loop
        if result[0]:
            break
    Bool, albumID, artistIDs, trackID, artistNames, trackName, explicit, popularity = result
    if not Bool:
        print('Nothing found for song:')
        print('\t' + str(value['name_song']))
        print('\t' + str(value['name_artist']))
    albumIDlist2.append(albumID)
    artistIDslist2.append(artistIDs)
    trackIDlist2.append(trackID)
    artistNameslist2.append(artistNames)
    trackNamelist2.append(trackName)
    explicitlist2.append(explicit)
    popularitylist2.append(popularity)
        
#%%
secondNotFoundAdapted['artistnames']= artistNameslist2
secondNotFoundAdapted['trackName'] = trackNamelist2
secondNotFoundAdapted['trackID'] = trackIDlist2
secondNotFoundAdapted['albumID'] = albumIDlist2
secondNotFoundAdapted['artistIDs'] = artistIDslist2
secondNotFoundAdapted['explicit'] = explicitlist2
secondNotFoundAdapted['popularity'] = popularitylist2
#%%
""" Ad hoc repairs """
thirdResults = secondNotFoundAdapted.dropna()
secondAllResults = pd.read_csv('secondAllResults.csv', index_col = None).drop('Unnamed: 0', axis = 1)
thirdAllResults = secondAllResults
j = 0
for i in thirdResults.iterrows():
    song_idtje = i[1]['song_id']    
    index = secondAllResults.index[secondAllResults['song_id'] == song_idtje][0]
    thirdAllResults.set_value(index, 'artistnames', i[1]['artistnames'])
    thirdAllResults.ix[index, 'trackName'] = i[1]['trackName']
    thirdAllResults.ix[index, 'trackID'] = i[1]['trackID']
    thirdAllResults.ix[index, 'albumID'] = i[1]['albumID']
    thirdAllResults.set_value(index, 'artistIDs', i[1]['artistIDs'])
    thirdAllResults.ix[index, 'explicit'] = i[1]['explicit']
    thirdAllResults.ix[index, 'popularity'] = i[1]['popularity']
""" 
-------------------
RETRIEVE DATA
-------------------
Retrieve audio features of all songs
Retrieve genre of all artists
"""
info = getTrackInfo(filter(None, trackIDlist[0:50]))

