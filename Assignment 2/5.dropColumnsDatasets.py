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
songsAttributes.to_csv('songs_atrributes_trimmed.csv', index = False)
songsAttributes.to_pickle('songs_atrributes_trimmed.pkl')

#%%
songs = pd.read_csv("songs.csv", engine = 'python', delimiter=",")
"""songs that were wrongly matched as found in script 3"""
needToBeRemoved = ['2xrQS0PDuIoU19lwOxGuaO', '2o8MI4k9Ffys7LMizikJoV', '6BIel0aZTaHBh3EhdPhOGw',
 '2znfz3w0a9Yb7CG5YDDeqo', '28L6g25xXqjuE742YjxX71', '2gtAWpwS1Z9gn5z4gY8joj', '1gQPqkrPZ1RypZvSYEAygs',
 '2TDVv0j4Xwel5BH1DezX71', '3Q1QR8f7kYWTs5TlawHAa2', '4uZs5CJ916xdWmjwqLYvYH', '3PS67MAgYRrbAUsAClxBRx',
 '0WMQxuCIITuP4g9pLHQ7dr', '5ZgFjxPxFRGbhx8Qh37xG4', '5kF3B54u0oNkeXMBHTksij', '6hca73V4uCdpivMbukjMZL',
 '3QEN7zLbWiutDL5AvQXdNw', '7gfdDuc2Lx8hQ1GfU0OjmO', '7bwWuZ2hXWcb8KenR0xiXm', '14UOPc89sWZyaEPdKe1Grp',
 '0gjsAXbQTmM30ljk6s8svE', '75pOJywBC8n1xgbijx2yFp', '2rrAoe7crVi7XuiUzIJVeb', '1vSqsuJFphViMNq1lyjYU1',
 '6tGSl3ipN51Iy9vjz1Mzht', '7HY51OlJbxPv1r08kKC4o0', '3RUR13iOUGDc8AGiGS1axh', '1Ut4Oh4CdnTMj5LV1W0aQf',
 '1BQicUXQoUqcHKJ9VLYXbG', '0kninVFtOjEHujKTk8kArq', '7z7GWZxsW3vK14IHE3H2re', '6T0zdOkIHgapgfvtsuNjNm',
 '5CoLgtSDG2kvPAeTHGGIc6', '5cwdHuxSANrtI1mHQqCbZ7', '4sFbojhVXQv7dBC9PVCcRn', '3eNGdIH7IjPtnEm5BZPFBP',
 '0phT9WYvak5mt0lLe9nuKP', '5gmMa8nwzrkcPbHzSW3azN', '3odPjdX1SjxxjIr0EZjEht', '2oLAgYseygwLYu2I5nrTBb',
 '7C2uNHOfIYP9XH7ist0iAl', '3h916abrIpTX7O7UCpppWp', '3DijXDOWwsrg43D0Se345d', '2nmBKgK0SYt5cnFpfWOh0W',
 '2v5kYpbJ5RUAm3HIiOZeXB', '2DVBFvAj6flx2OWJxGVk2g', '21gTMHscCIlkqVKBx2JEu2', '3SBvJrZqxadgxvs457lP4n',
 '6XPWgoTMxKDu088vBfO2pG', '3FPG3aQq3DNvjXS1IZZWHv', '0By81TVzMzx8pMvg2RotFx', '7si5k4ui9pxKNp799VkNtY',
 '4Qu1776KUvofSZRE1SRekS', '7o7E1nrHWncYY7PY94gCiX', '6Nkt6RjB84HuLpno47TtIu', '6GmtW3yyH4onljFBTDz1dF',
 '0RC0rWxbZEMGEpYzFkhezL', '5Y4T4O5xy63BbgUfUkNPxA', '6wcY8neuebBTpvdyppASA1', '54z5yF6QYmxvjsAQ7BcOf7',
 '3Q1QR8f7kYWTs5TlawHAa2', '65E62rOSbm7SZbAMYjNTJq', '1G57qD7bUEFPZz24VwnRRu', '6gBcyxdwgcnA8UQnB9vwRc',
 '1jfcT6NRqjOhcH4h55mari', '6VoiY3rukFPoqzP4AoGPU8', '29lF0lJdbh6hY7vLfc65on', '3zxde5nDLecDQJt8q48s4z',
 '2jz33B72xM4sjZfxes6Okf', '64K7k7kejwakDFGuEwhyE3', '4PzKAS9jn8wVNtqAOt5Bo0', '6xuhxd6yeWL0530X3gNYSd',
 '6Qu0AGKiZeLV4LpI601KBT', '53hZCLhk8UgPNXXScV9l2x', '1rhRW4eqfp12h9FnB4HHGe', '3QsnFdPLZUNMLdq2jIg1YG',
 '066VpprkGzxtCrNMKFcVDD', '4KMhriFpKcXQ6wqzNZfWxq', '1BF3Y8qD37KtAfwTAs8KO2', '7JWdlf8DvnmgcM4fbOuswU',
 '1pEehXkwiTLzKgOV3ULU78', '1fr92Vupmcs2vgLMFVQ7rd', '6mcu7D7QuABVwUGDwovOEh', '6a8xKUtrUdHGkKpokFQ6a5',
 '2cq0GKhCzYHJ1nr4vWOL30', '3Ka2Ti5ZreEHlp9R7BXyOj', '5r3aYGutXgsxSqB6W3RrzJ']
songs['trackID'] = songs['trackID'].str[14:]
songs = songs[~songs['trackID'].isin(needToBeRemoved)]
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
#%%
charts = pd.read_pickle('ranklijst.pkl')
duplicates = songs[songs.duplicated(['trackID'])] #df with every first element of a duplicated group
songs = songs[~songs['trackID'].isin(duplicates['trackID'])]

songs = songs.reset_index(drop=True)

position = [None]*len(songs)
for index, row in charts.iterrows():
    if index%10000 == 0:
        print(index)
    if row['songID'] in songs['trackID'].values: 
        n = songs[songs['trackID']==row['songID']].index[0]
        if position[n] is None:
            position[n] = [[row['year'], row['week'], row['positionNr']]]
        else:
            position[n].append([row['year'], row['week'], row['positionNr']])
songs['position'] = position

#%%
songs = songs.drop(['Unnamed: 0', 'song_id', 'explicit', 'popularity', 'position'], axis=1)
songs.to_csv('songs_trimmed.csv', index = False)
songs.to_pickle('songs_trimmed.pkl')

#%%
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
artistsAttributes.to_csv('artists_attributes_trimmed.csv', index = False)
artistsAttributes.to_pickle('artists_attributes_trimmed.pkl')