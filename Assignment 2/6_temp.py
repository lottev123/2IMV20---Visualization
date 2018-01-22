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

frames = [songsAttributes, songs]
join = pd.merge(left= songs, right = songsAttributes, left_on = 'trackID', right_on ='id' )

longsongs = join[join['duration_ms']>600000]

join.trackName = join.trackName.str.lower()

songs = join
songs = songs.sort_values(['amountOfNotations'], ascending = False)


top80 = 0.8*sum(songs['amountOfNotations'])
numOfNotations = 0
for n in range(0, len(songs)):




