from spotipy.oauth2 import SpotifyOAuth
import spotipy
import argparse
from settings import client_id, client_secret, redirect_uri
import pandas as pd


def get_args():
	parser = argparse.ArgumentParser(description='Creates a playlist from a Music League season')
	parser.add_argument('-l', '--league', required=True,
						help='League ID')
	return parser.parse_args()


args = get_args()
# Set the scope needed for playlist modification
scope = 'playlist-modify-public'
# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Read the leagues.csv file to get the League Name
leagues_df = pd.read_csv('leagues.csv')

# # Get the League Name and Created date based on the target League ID
league_info = leagues_df.loc[leagues_df['League ID'] == args.league]
league_name = league_info['Name'].values[0]
league_created_date = league_info['Created'].values[0]

# Read the rounds.csv file
df = pd.read_csv('rounds.csv')

# Remove rounds that haven't happened yet
df = df.dropna()

# Filter playlists based on the target League ID
target_playlists = df[df['League ID'] == args.league]['Playlist URL']

# Create a new combined playlist
combined_playlist_name = '{}'.format(league_name)
combined_playlist_description = "https://app.musicleague.com/l/{}/ started on {}.".format(args.league, league_created_date[0:10])

# Create a new playlist
combined_playlist = sp.user_playlist_create(sp.me()['id'], combined_playlist_name, public=True, description=combined_playlist_description)

tracks_data = []
# Add tracks from each playlist to the combined playlist
for playlist_url in target_playlists:
	# Get tracks from the playlist
	tracks = sp.playlist_items(playlist_url)

	# Add tracks to the combined playlist
	sp.playlist_add_items(combined_playlist['id'], [track['track']['uri'] for track in tracks['items']])

	# Extract relevant track information
	for track in tracks['items']:
		track_data = {
			'Track Name': track['track']['name'],
			'Artist(s)': ', '.join([artist['name'] for artist in track['track']['artists']]),
			'Album': track['track']['album']['name'],
			'Release Date': track['track']['album']['release_date'],
			'Track URI': track['track']['uri'],
			'Round Name': df[df['Playlist URL'] == playlist_url].iloc[0]['Name'],
		}
		tracks_data.append(track_data)

# Create a DataFrame from the tracks data
tracks_df = pd.DataFrame(tracks_data)

# Export the DataFrame to a CSV file
tracks_df.to_csv(f'{league_name}.csv', index=False)

print(f"Combined playlist created successfully: {combined_playlist['external_urls']['spotify']}")
print(f'Combined playlist tracks exported to {league_name}.csv')
