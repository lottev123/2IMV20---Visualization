# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 13:42:03 2018

@author: s134277
"""

import os
import pandas as pd
from ast import literal_eval

working_dir = r'C:\Users\s134277\Documents\GitHub\2IMV20---Visualization\Assignment 2\Results '
os.chdir(working_dir)

songsAttributes = pd.read_pickle('songs_Attributes.pkl')
songsAttributes = songsAttributes.drop(['analysis_url', 'key', 'track_href', 'type', 'trackID'], axis=1)
songsAttributes.to_csv('songs_Atrributes_trimmed.csv', index = False)

songs = pd.read_csv("songs.csv", engine = 'python', delimiter=",")
songs['trackID'] = songs['trackID'].str[14:]
songs['albumID'] = songs['albumID'].str[14:]
artistIDs = []
for element in songs['artistIDs']:
    temp = literal_eval(element)
    templist = []
    for element in temp:
        templist.append(element[15:])
    artistIDs.append(templist)
songs["artistIDs"] = artistIDs

firstNotation = []
lastNotation = []
amountOfNotations = []
for row in songs['position']:
    row = literal_eval(row)
    firstNotation.append(min(row)[0])
    lastNotation.append(max(row[0]))
    amountOfNotations.append(len(row))
songs['firstNotation'] = firstNotation
songs['lastNotation'] = lastNotation
songs['amountOfNotations'] = amountOfNotations
songs = songs.drop(['Unnamed: 0', 'song_id', 'explicit', 'popularity', 'position'], axis=1)
songs.to_csv('songs_trimmed.csv', index = False)

artistsAttributes = pd.read_pickle('artists_attributes.pkl')
artistsAttributes = artistsAttributes.reset_index(drop=True)
a = artistsAttributes[artistsAttributes.duplicated(['id'])==True]
artistsAttributes = artistsAttributes.drop(['external_urls', 'followers', 'genres', 'href', 'images',
       'popularity', 'type', 'artistID'], axis = 1)
artistsAttributes = artistsAttributes.drop(artistsAttributes.index[4208])

zeros = [0] * len(artistsAttributes)
temp = artistsAttributes['id']
temp = pd.DataFrame(temp)
temp['firstNotation'] = zeros
temp['lastNotation'] = zeros
temp['amountOfNotations'] = zeros
temp['amountOfSongs'] = zeros
tempdict = temp.set_index('id').to_dict('index')

for index, row in songs.iterrows():
    artists = row['artistIDs']
    for element in artists:
        if element in tempdict:
            temp = tempdict[element]
            temp['amountOfSongs'] = temp['amountOfSongs']+1
            temp['amountOfNotations'] = temp['amountOfNotations'] + row['amountOfNotations']
            if temp['firstNotation']==0:
                temp['firstNotation'] = row['firstNotation']
                temp['lastNotation'] = row['lastNotation']
            elif temp['firstNotation'] > row['firstNotation']:
                temp['firstNotation'] = row['firstNotation']
            if temp['lastNotation'] < row['lastNotation']:
                temp['lastNotation'] = row['lastNotation']
            tempdict.update({element:temp})

dicttodf = pd.DataFrame.from_dict(tempdict, orient = 'index')
artistsAttributes = pd.merge(artistsAttributes,dicttodf, how= 'outer',left_on="id" , right_index= True )
artistsAttributes.to_csv('artistsAttributes_trimmed.csv', index = False)