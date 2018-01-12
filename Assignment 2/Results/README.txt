Following files come in csv only
	songs: all top40 songs retrieved from Spotify after cleaning

Following files come in csv and pkl (Python object)
	songs_attributes: audio features retrieved from Spotify
	artists_attributes: artist info retrieved from Spotify
	albums_attributes: album info received from Spotify except for 
		tracks to limit file size

Following files come in pkl (Python object) only:
	related_artists: dictionary with for each artist its related artists