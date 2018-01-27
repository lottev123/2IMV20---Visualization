# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 12:54:07 2018

@author: s134277
"""

import os
import pandas as pd

working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\Results '
os.chdir(working_dir)

songsAttributes = pd.read_pickle('songs_atrributes_trimmed.pkl')
songs = pd.read_pickle('songs_trimmed.pkl')
artists = pd.read_pickle('artists_attributes_trimmed.pkl')

join = pd.concat([artists]*2, ignore_index = True)
firstrow = []
for i in range (0, len(join)):
    if i%2==0:
        firstrow.append(0)
    else:
        firstrow.append(1)
join['rownr'] = firstrow


sum(artists['amountOfSongs'])

artists = artists.sort_values(by = ['amountOfSongs'], ascending = False)

n = 0
percentage_of_songs = 0.2 * sum(artists['amountOfSongs'])
for i in range(0, (len(artists))):
    if n > percentage_of_songs:
        break
    n = n + artists.iloc[i,5]

frames = [songsAttributes, songs]
join = pd.merge(left= songs, right = songsAttributes, left_on = 'trackID', right_on ='id' )

longsongs = join[join['duration_ms']>600000]

join.trackName = join.trackName.str.lower()

songs = join
songs = songs.sort_values(['amountOfNotations'], ascending = False)






