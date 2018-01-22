# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 15:05:04 2017

@author: s134277
"""

import pandas as pd
import os
import numpy as np
import ast

working_dir = r'C:\Users\s134277\Documents\Top40 dataset\ '
os.chdir(working_dir)
artists_top40 = pd.read_csv("artists.csv", engine='python', delimiter="\t")
songs_top40 = pd.read_csv("songs.csv", engine = 'python', delimiter="\t")

working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\Results\_old\ '
os.chdir(working_dir)
spData = pd.read_csv('thirdAllResults.csv', engine = 'python')

"""Check whether trackID's occur multiple times"""
spData.duplicated(['song_id']).sum()    #No double songs, as expected

#%%
"NO OR FALSE MATCH IN SPOTIFY BASED ON ARTIST"
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
                    falseMatchesIds.append(row['song_id'])

spData = spData[~spData.song_id.isin(falseMatchesIds)]

"""Remove karaoke artists that slipped trough"""
removed = removed.append(spData[spData.artistnames.str.contains("karaoke")==True])
spData = spData[spData.artistnames.str.contains("karaoke")==False]


#%%
"""NOT ALL WRONGLY MATCHED SONGS WERE DELETED IN THE FIRST ROUND.
THUS, A LIST IS CREATED WITH ADDITIONAL WRONGLY MATCHED SONG-ID'S, 
SUCH THAT THESE CAN BE DELETED IN SCRIPT 5 """
needToBeRemoved = []

spData.name_song = spData.name_song.str.lower()
spData.trackName = spData.trackName.str.lower()

"""SONGS THAT IN SPOTIFY ARE MEDLEY, KARAOKE VERSIONS OR MIXES OF DIFFERENT SONGS TOGETHER"""
medley = spData[spData.trackName.str.contains("medley")]
medley = medley[~medley.name_song.str.contains("medley")] #some songs in the top40 are truely a medley, these should not be deleted.
needToBeRemoved.extend(medley['trackID'].str[14:].tolist())
spData = spData[~spData.index.isin(medley)]

needToBeRemoved.extend(spData[spData.trackName.str.contains("karaoke")]['trackID'].str[14:].tolist())
spData = spData[~spData.trackName.str.contains("karaoke")]

longsongs = spData[spData.trackName.str.len() > 60]
longsongsmix = longsongs[longsongs.trackName.str.contains("mix")]
needToBeRemoved.extend(spData[spData.index.isin([1994, 2631, 3113, 5796])]['trackID'].str[14:].tolist())
spData = spData[~spData.index.isin([1994, 2631, 3113, 5796])]


""" SONGS THAT ARE WRONGLY MATCHED BASED ON SONG NAME"""
falseNegatives =[1203, 2145, 2622, 7056, 8739, 9214, 9228, 9352, 9443, 10229, 10546, 10641, 11113, 11264, 12109, 12409]
falseMatchesIds = []

for index, row in spData.iterrows(): 
    strippedTop40Songname = ''.join(e for e in row['name_song'] if e.isalnum())
    strippedSpotifySongname = ''.join(e for e in row['trackName'] if e.isalnum())
    for i in range(0, len(strippedTop40Songname)-4+1):
        substring = strippedTop40Songname[i:i+4]
        if substring in strippedSpotifySongname:
            break
        else:
            if i == len(strippedTop40Songname)-4:
                if index not in falseNegatives:
                    falseMatchesIds.append(row['song_id'])

falseMatches = spData[spData.song_id.isin(falseMatchesIds)]
needToBeRemoved.extend(spData[spData.index.isin(falseMatchesIds)]['trackID'].str[14:].tolist())
spData = spData[~spData.song_id.isin(falseMatchesIds)]

#%%
"CREATE LIST WITH OCCURENCES IN TOP40"
spData = spData.reset_index(drop=True).reset_index(drop=True)
chartList = []
columns = ['year', 'week', 'positionNr', 'songID']

working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\data\top40 '
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
                #chartList.append([year, week, positionNr, songID])
                if songID in spData.song_id.values:
                    n = spData[spData['song_id']==songID].index[0]
                    chartList.append([year, week, positionNr, spData.iloc[n,9][14:]])
charts = pd.DataFrame(chartList, columns = columns)
working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\Results '
os.chdir(working_dir)
charts.to_csv('ranklijst.csv')
charts.to_pickle('ranklijst.pkl')


duplicates = spData[spData.duplicated(['trackID'])]
spData = spData[~spData['song_id'].isin(duplicates['song_id'])]
spData['trackID_trim'] = spData['trackID'].str[14:]
spData = spData.reset_index(drop=True).reset_index(drop=True)

position = [None]*len(spData)
for index, row in charts.iterrows():
    if index%10000 == 0:
        print(index)
    n = spData[spData['trackID_trim']==row['songID']].index[0]
    if position[n] is None:
        position[n] = [[row['year'], row['week'], row['positionNr']]]
    else:
        position[n].append([row['year'], row['week'], row['positionNr']])
spData['position'] = position


#%%
#"""Only relevent when song_id in charts is the song_id in the top40 dataset"""
#chartRowRemoved = [None]*len(charts)
#
#for index, row in charts.iterrows():
#    if row[3] in removed.song_id.values:
#        chartRowRemoved[index] = True
#    else:
#        chartRowRemoved[index] = False
#
#charts['chartRowRemoved'] = chartRowRemoved
#
#sum(charts.chartRowRemoved)

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
