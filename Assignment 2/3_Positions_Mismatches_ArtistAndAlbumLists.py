# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 15:05:04 2017

@author: s134277
"""

import pandas as pd
import os
import numpy as np
import ast

#working_dir = r'C:\Users\s134277\Documents\Top40 dataset\ '
working_dir = '/Users/hildeweerts/2IMV20---Visualization/Assignment 2/Data/data/' 

os.chdir(working_dir)
artists_top40 = pd.read_csv("artists.csv", engine='python', delimiter="\t")
songs_top40 = pd.read_csv("songs.csv", engine = 'python', delimiter="\t")

#working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\Results '
working_dir = '/Users/hildeweerts/2IMV20---Visualization/Assignment 2/Data/data/' 
os.chdir(working_dir)
spData = pd.read_csv("thirdAllResults.csv", engine = 'python')

"""Check whether trackID's occur multiple times"""
spData.duplicated(['song_id']).sum()    #No double songs, as expected

#%%
"CREATE LIST WITH OCCURENCES IN TOP40"
position = [None]*len(spData)

#working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\data\top40 '
working_dir = '/Users/hildeweerts/2IMV20---Visualization/Assignment 2/Data/top40/' 
os.chdir(working_dir)

for year in range(1965,2017+1):
    for week in range(1, 53+1):
        if (year==2017 and week>50):
            break
        document = "chart_"+str(year)+"_week_"+str(week)+".csv"
        try:
            chart = pd.read_csv(document, engine = 'python')
            fileFound = True
        except FileNotFoundError:
            fileFound = False
        if fileFound == True:
            chart.columns = ['posartsong']
            for index, row in chart.iterrows():
                temp = row.posartsong.split("\t")
                positionNr = pd.to_numeric(temp[0])
                songID = pd.to_numeric(temp[2])
                if songID in spData.song_id.values:
                    n = spData[spData['song_id']==songID].index[0]
                    if position[n] is None:
                        position[n] = [[year, week, positionNr]]
                    else:
                            position[n].append([year, week, positionNr])
spData['position'] = position   

#%%
"NO OR FALSE MATCH IN SPOTIFY"
"""Remove songs for which no additional info is found on Spotify"""
spData = spData.replace(to_replace='[None]', value = np.nan)
removed = spData[spData.trackName.isnull()]
spData = spData.dropna() #drop artist Id's that are not found by Spotify

"""Remove songs with artists which are falsely matched with Spotify data"""
spData.artistnames = spData.artistnames.str.lower()
spData.name_artist = spData.name_artist.str.lower()
falseNegatives =[5751, 183, 4919, 5108, 5940, 5563, 2387, 3756, 5648, 2231, 5647, 5216, 4299, 4837, 1764, 4246, 2719]
falseMatchesIds = []

for index, row in spData.iterrows(): 
    strippedTop40Artistname = ''.join(e for e in row['name_artist'] if e.isalnum())
    strippedSpotifyArtistname = ''.join(e for e in row['artistnames'] if e.isalnum())
    for i in range(0, len(strippedTop40Artistname)-4+1):
        substring = strippedTop40Artistname[i:i+4]
        if substring in strippedSpotifyArtistname:
            break
        else:
            if i == len(strippedTop40Artistname)-4:
                if row['artist_id'] not in falseNegatives:
                    removed = removed.append(row)
                    falseMatchesIds.append(row['artist_id'])

spData = spData[~spData.artist_id.isin(falseMatchesIds)]

"""Remove karaoke artists that slipped trough"""
removed = removed.append(spData[spData.artistnames.str.contains("karaoke")==True])
spData = spData[spData.artistnames.str.contains("karaoke")==False]

#%%
"FINAL SONG TABLE"
songs = spData[['song_id', 'artistnames', 'trackName', 'trackID', 'albumID', 'artistIDs', 'explicit', 'popularity', 'position']]
songs = songs.reset_index(drop=True)

songs.to_csv('3_Songs.csv')

#%%
"ARTIST AND ALBUM LISTS"
artistIDs = []
albumIDs = []

for index, row in songs.iterrows():
    temp = ast.literal_eval(row.artistIDs)
    for element in temp:
        artist_identifier = element.split(":")[2]
        if artist_identifier not in artistIDs:
            artistIDs.append(artist_identifier)
    album_identifier = row.albumID.split(":")[2]
    if album_identifier not in albumIDs:
        albumIDs.append(album_identifier)     

#Aantal keren in top40: sum(1 for x in b if isinstance(x, list))
