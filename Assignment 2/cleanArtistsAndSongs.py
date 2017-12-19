# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 15:09:49 2017

@author: s134277
"""

import pandas as pd
import os

working_dir = r'C:\Users\s134277\Documents\Top40 dataset\ '
os.chdir(working_dir)
artists = pd.read_csv("artists.csv", engine='python', delimiter="\t")
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


songs = pd.read_csv("songs.csv", engine = 'python', delimiter="\t")
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
            if (splitrule) in firstElement[0]:  #this means that the song starts with a bracket (see id = 152)
                break
            splittedSong.append(firstElement.split(splitrule)[0])
    if (firstElement.find("(")!= -1): #only then, firstElement contains (
            splittedSong.append(firstElement[firstElement.find("(")+1:firstElement.find(")")]) #add part between brackets to list of songs
            splittedSong.append(firstElement.translate(translation_table)) # add string, but then without the brackets
    namesSongs[index] = splittedSong

songs["listOfNames"] = namesSongs
