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
artist_attributes = pd.read_csv('artists_attributes_trimmed.csv', engine = 'python')
songs = pd.read_csv('songs_trimmed.csv', sep=',', engine = 'python')
songs['artistIDs'] = songs['artistIDs'].apply(eval)
#%%
objs = [songs, pd.DataFrame(songs['artistIDs'].tolist())]
res = pd.concat(objs, axis=1).drop('artistIDs', axis=1)
#%%
res = pd.melt(_, var_name='artist_num', value_name='artistID', value_vars=[0, 1, 2], id_vars=['trackID'])
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
import seaborn as sns
sns.heatmap(adjacency)