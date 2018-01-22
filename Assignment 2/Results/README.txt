Following files come in csv only
	songs: all top40 songs retrieved from Spotify after cleaning
	adjacency_artists_edges: all edges in the related artist graph
	adjacency_artists_edges_top80: edges of the top 80 artists wrt number of songs in the top 40

Following files come in csv and pkl (Python object)
	songs_attributes: audio features retrieved from Spotify
	artists_attributes: artist info retrieved from Spotify
	albums_attributes: album info received from Spotify except for 
		tracks to limit file size

	Trimmed versions of the three abovementioned datasets, 
	containing only variables that are interesting at the first stage of the visualization:
		songs_Attributes_trimmed
			Dropped variables: 'analysis_url', 'key', 'track_href', 'type', 'trackID'
		artistsAttributes_trimmed
			Dropped variables: 'external_urls', 'followers', 'genres', 'href', 'images','popularity', 'type', 'artistID'
			Dropped rows: id[4208] (one duplicated artist was found (based on spotify-id)
			Added variables:
				firstNotation (year artist was in the top40 for the first time)
				lastNotation
				amountOfNotations
				amountofSongs (amount of songs in the top40)
		songs_trimmed
			Dropped variables: 'Unnamed: 0', 'song_id', 'explicit', 'popularity', 'position'
			Adjusted variables: 'trackID', 'artistsID', 'albumID' (removed "spotify:track:" part, hereby isolating the id)
			Added variables:
				firstNotation (year songs was in the top40 for the first time)
				lastNotation
				amountOfNotations (amount of times songs was in the top40)
Following files come in pkl (Python object) only:
	related_artists: dictionary with for each artist its related artists