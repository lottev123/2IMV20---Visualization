#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 14:24:26 2018

@author: hildeweerts
"""
#%%
import os
import pandas as pd
import pickle 
import numpy as np
import ast

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)
    
    
working_dir = '/Users/hildeweerts/2IMV20---Visualization/Assignment 2/Results/'
os.chdir(working_dir)

# load dicstionary 
related_artists = load_obj('related_artists')

# load artist attributes
artist_attributes = pd.read_csv('artists_attributes_trimmed.csv', engine = 'python')

#%%

# create dataframe with all source -target combinations
source  = []
target = []
for key, related_list in related_artists.items():
    for i in related_list:
        source.append(str(key).replace('spotify:artist:', ''))
        target.append(i['uri'].replace('spotify:artist:', ''))
df = pd.DataFrame()
source_unique = np.unique(source)
df['source'] = source
df['target'] = target

# remove duplicates
df2 = pd.DataFrame({'target': df['source'], 'source': df['target']})
df = df.append(df2)
df = df[df['target'].isin(source_unique)]
df = df[df['source'].isin(source_unique)]
df = df.drop_duplicates()
df['1'] = [1] * len(df)

# select only top 80 based on number of songs in the top 40
top80 = artist_attributes.nlargest(80, 'amountOfSongs')

df = df[df['target'].isin(top80['id'])]
df = df[df['source'].isin(top80['id'])]

#%%
adjacency = pd.crosstab(index = df['source'], columns = df['target'])
#%%
#adjacency.to_csv('adjacency_artists_matrix.csv')
df.to_csv('adjacency_artists_edges_top80.csv')
#%%
""" expand list of songs per artist and get average song attributes per artist """
songs = load_obj('songs_trimmed')
songs_attributes = pd.read_csv('songs_attributes_trimmed.csv', engine = 'python')
s = songs.apply(lambda x: pd.Series(x['artistIDs']),axis=1).stack().reset_index(level=1, drop=True)
s.name = 'artistID'
songs2 = songs.drop(['artistIDs','trackName', 'artistnames', 'albumID', 'firstNotation', 'lastNotation', 'amountOfNotations'], axis=1).join(s)
songs_attributes_artists = pd.merge(songs2, songs_attributes, left_on ='trackID', right_on = 'id')
songs_attributes_artists = songs_attributes_artists.drop('id', axis = 1)
artists_averages = songs_attributes_artists.groupby(['artistID']).mean()
artists_averages['artistID'] = artists_averages.index
artists_averages.to_csv('artists_average_songattributes.csv')
#%%
#songs2.to_csv('songs_trimmed_expanded.csv')
