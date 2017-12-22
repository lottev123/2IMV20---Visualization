# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 15:05:04 2017

@author: s134277
"""

import pandas as pd
import os
import numpy as np

working_dir = r'C:\Users\s134277\Documents\Top40 dataset\ '
os.chdir(working_dir)
artists = pd.read_csv("artists.csv", engine='python', delimiter="\t")
songs = pd.read_csv("songs.csv", engine = 'python', delimiter="\t")

working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\Results '
os.chdir(working_dir)
firstFound = pd.read_csv("firstAllResults.csv", engine='python')
spData = pd.read_csv("secondAllResults.csv", engine = 'python')

"""Check whether trackID's occur multiple times"""
spData.duplicated(['song_id']).sum()    #No double songs, as expected

"""Check whether certain artists have multiple id's"""
artistIds = spData[['artist_id','name_artist', 'artistnames', 'artistIDs']].drop_duplicates()
artistIds = artistIds.replace(to_replace='[None]', value = np.nan).dropna() #drop artist Id's that are not found by Spotify
artistIds.duplicated(['artistIDs']).sum()   #There are artists with multiple id's

#remove artists with karaoke in the name
artistIds.artistnames = artistIds.artistnames.str.lower()
artistIds.artistnames.str.contains("karaoke").sum()
artistIds = artistIds[artistIds.artistnames.str.contains("karaoke")==False]

#create df with duplicates
artistIds['is_duplicated'] = artistIds.duplicated(['artistIDs'], keep = False)
duplicates = artistIds[artistIds['is_duplicated']==True]

grouped = duplicates.groupby('artistnames')
list(grouped)
grouped.size()

d = dict()
"""Nog toevoegen: als count hoger is dan x, dan handmatig nog doorkijken"""
for id, group in grouped:
    for i in range(1, len(group)):
        d[group.iloc[i].artist_id] = group.iloc[0].artist_id

"""Nog toevoegen:
    check op artiestennaam: kijken of minstens 4 karakters overeen komen
    for loop om id's uit dictionary om te zetten in de spData
    """
