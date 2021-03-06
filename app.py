from cmd import Cmd

import spotipy
import spotipy.util
import lyricsgenius

from music_info_utils import *

class App(Cmd):

	'''Command-line application class'''

	credentials = {'USERNAME': '', 'ID': '', 'SECRET': '',											#credentials for running
				   'URI': '', 'TOKEN': ''}															#a session

	spotify_api = None																				#Spotify API object
	genius_api = None																				#Lyrics Genius API object

	def __init__(self, file=''):
		
		super(App, self).__init__()

		if file:

			credentials = txt_to_list(file)															#get file data
			if not credentials:
				return

			self.credentials = dict(zip(self.credentials.keys(), credentials))						#else, sets credentials from file

			for i in self.credentials.items():														#check if there are any empty credential
				if i[1] == '':
					print(i[0], 'not specified'+'\n')												#in this case, log error and return
					return																		

			try:																					#try to get spotify token
				token = spotipy.util.prompt_for_user_token(self.credentials['USERNAME'],
												   		   scope = None,
												   		   client_id = self.credentials['ID'],
												   		   client_secret = self.credentials['SECRET'],
												   		   redirect_uri = self.credentials['URI'])
			except:
				try:
					os.remove(f".cache-{self.credentials['USERNAME']}")
					token = spotipy.util.prompt_for_user_token(self.credentials['USERNAME'],
													   		   scope = None,
													   		   client_id = self.credentials['ID'],
													   		   client_secret = self.credentials['SECRET'],
													   		   redirect_uri = self.credentials['URI'])
				except Exception as e:
					print('\n'+e+'\n')																#if failed, log error and return
					return

			self.spotify_api = spotipy.Spotify(auth = token)										#define spotify API object
			self.genius_api = lyricsgenius.Genius(self.credentials['TOKEN'])						#define lyrics Genius API object


	def do_GET(self, arg):
		'''
Use: GET <PARAMETER1> <PATAMETER2>

Dedicated to show general information about an artist,
album or song.

Parameters:

	PARAMETER1:
		ARTIST:
			ALBUMS
			TOP_TRACKS		
		TRACKLIST
		LYRICS
		'''
		if check_arguments_number(arg, min=3) == -1:
			return
		
		first = arg.split(' ')[0]

		if first == 'ARTIST':

			arg = arg.strip().split(' ', 2)														#split arg string by spaces twice

			if check_arguments_number(arg, min=3) == -1:											#check number of arguments
				return																				#return if not correct

			if self.spotify_api == None:														#if spotify API not running
				print('Spotify API session not running'+'\n')									#log error and return
				return

			artist = arg[-1]																	#after two arguments, artist must be provided

			if arg[1] == 'ALBUMS':

				albums = get_artist_albums(artist, self.spotify_api)							#get albums
				if albums == -1:																#if failed
					print('Artist not found'+'\n')												#log error and return
					return
				
				print('\n'+artist.capitalize() + ' albums:'+'\n')								#else print table with requested content
				print_table(albums)

			elif arg[1] == 'TOP_TRACKS':
				
				top_tracks = get_artist_top_tracks(artist, self.spotify_api)					#get top tracks
				if top_tracks == -1:															#if failed
					print('Artist not found'+'\n')												#log error and return
					return
				
				print('\n'+artist.capitalize() + ' top tracks:'+'\n')							#else print table with requested content
				print_table(top_tracks)

			else:
				print('Invalid argument:', arg[1]+'\n')											#if invalid first argumernt, log error and return

		elif first == 'TRACKLIST':

			arg = arg.strip().split(' ', 1)														#split arg string by spaces once

			if self.spotify_api == None:														#if spotify API not running
				print('Spotify API session not running'+'\n')									#log error and return
				return

			album = arg[-1]																		#after first argument, album must be provided
			tracklist, artist = get_album_tracklist(album, self.spotify_api)					#get tracklist and artist

			if tracklist == -1:																	#if failed
				print('Album not found'+'\n')													#log error and return
				return	

			print('\n'+album.capitalize(), 'by', artist.capitalize(), 'tracklist:'+'\n')		#else print table with requested content
			print_table(tracklist)

		elif first == 'LYRICS':

			if self.genius_api == None:															#if Genius API not running
				print('Lyrics Genius API session not running'+'\n')								#log error and return
				return
			
			arg = arg.strip().split(' ', 1)														#split arg string by spaces once
			song, artist = arg[1].split(',', 1)													#plit song and artist by , once

			song_lyrics, artist = get_song_lyrics(song, artist, self.genius_api)				#get tracklist and artist
			if song_lyrics == -1:																#if failed
				return																			#return

			print('\n'+song.capitalize(), 'by', artist.capitalize()+':\n')			#else print table with requested content
			print_table(song_lyrics.split('\n'))

		else:
			print('Invalid argument:', first+'\n')												#if invalid first argumernt, log error and return
