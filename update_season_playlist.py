from spotipy.oauth2 import SpotifyOAuth
import spotipy
import argparse
from settings import client_id, client_secret, redirect_uri
import pandas as pd
import sys


def get_args():
	parser = argparse.ArgumentParser(description='Appends a playlist to another playlist')
	parser.add_argument('-p', '--playlist', required=True, default='',
						help='Playlist to append')
	parser.add_argument('-d', '--destination', required=True,
						help='Existing playlist to be appended')
	parser.add_argument('-c', '--csv', required=True,
						help='Existing CSV file to update with track info')
	return parser.parse_args()


args = get_args()

# Read the rounds.csv file
df = pd.read_csv('rounds.csv')
if args.playlist not in pd.unique(df['Playlist URL']):
	sys.exit("Playlist not found in rounds.csv")

# Set the scope needed for playlist modification
scope = 'playlist-modify-public'
# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Get tracks from the playlist
tracks = sp.playlist_items(args.playlist)

# Add tracks to the combined playlist
sp.playlist_add_items(args.destination, [track['track']['uri'] for track in tracks['items']])

tracks_data = []
# Extract relevant track information
for track in tracks['items']:
	track_data = {
		'Track Name': track['track']['name'],
		'Artist(s)': ', '.join([artist['name'] for artist in track['track']['artists']]),
		'Album': track['track']['album']['name'],
		'Release Date': track['track']['album']['release_date'],
		'Track URI': track['track']['uri'],
		'Round Name': df[df['Playlist URL'] == args.playlist].iloc[0]['Name'],
	}
	tracks_data.append(track_data)

# Create a DataFrame from the tracks data
tracks_df = pd.DataFrame(tracks_data)

# Export the DataFrame to a CSV file
tracks_df.to_csv(args.csv, mode='a', index=False, header=False)

print(f"Combined playlist updated successfully!")
print(f'Combined playlist tracks added to {args.csv}!')
