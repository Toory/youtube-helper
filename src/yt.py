from __future__ import unicode_literals
import youtube_dl
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.request import urlopen, Request
import os
import re
import eyed3
import argparse
import logging

YDL_OPTS = {
	'outtmpl': '~/Downloads/%(title)s.%(ext)s', 
	"quiet": True,
}

class Video:

	def __init__(self, url=''):
		"""Plays audio from (or searches for) a URL."""
		self.url = url
		self.genius_access_token = '<your genius access token here>'

	def searchVideo(self,keySearch):
		'''
		Downloads the video from a youtube url
		'''

		ydl_opts = {
			"default_search": "ytsearch",
			'outtmpl': '~/Downloads/%(title)s.%(ext)s', 
			"quiet": True,
			'extractaudio' : False,
		}

		try:
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				print(keySearch)
				video = ydl.extract_info(f'ytsearch:{keySearch}',download=False)
				tempUrl = video['entries'][0]['id']
				yturl = 'https://www.youtube.com/watch?v=' + str(tempUrl)
				print(yturl)
				self.url = yturl
				return yturl
		except Exception:
			log.exception('')

	def youtubeToMp3(self):
		'''
		Downloads the audio from a youtube url in mp3 format, then embeds title , artist, coverart and lyrics (ID3 metadata)
		'''

		try:
			videoInfo, fileName = self.downloadMp3()
			print(fileName)
			track,fileName = self.info(fileName,videoInfo)
			artist, title = track.split(' - ')
			albumArt = self.getAlbumArt(track)
			lyrics = self.getLyrics(title)
			self.setData(fileName,artist,title,lyrics,albumArt)
			self.getData(fileName)
		except Exception:
			log.exception('')

	def downloadMp3(self,codec='mp3',quality='192'):

		ydl_opts = {
			'format': 'bestaudio/best',
			'no_warnings': True,
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': codec,
				'preferredquality': quality,
			}],
			'outtmpl': '~/Downloads/%(artist)s - %(track)s.%(ext)s', 
			"quiet": False,
			"extract_flat": "in_playlist",
			'prefer_ffmpeg': True,
			'keepvideo': False
		}

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			info = ydl.extract_info(self.url, download=True)
			videoInfo = None
			if "_type" in info and info["_type"] == "playlist":
				return self.downloadMp3(info["entries"][0]["url"])  # get info for first video
			else:
				videoInfo = info
			fileName = ydl.prepare_filename(videoInfo)
			#replaces the extention of the video (usually .webm/.m4a) to .mp3 since youtube_dl doesn't update the file automatically after ffmpeg's conversion to mp3
			fileName = re.sub(r'\.(.*)','.mp3',fileName)
			return videoInfo, fileName

	def info(self,fileName,videoInfo):
		'''
		Fetches title & artist from youtube metadata, if not found uses the whole video title
		'''
		artist = videoInfo.get('artist')
		title = videoInfo.get('track')
		track = f'{artist} - {title}'
		print(track)
		# if artist & title were not found use video title
		if title is None or artist is None:
			track = videoInfo.get('title')
			tempFile = fileName
			#changes fileName from artist - title -> video title
			fileName = re.sub(fileName.split('/')[-1].split('.')[0],track,fileName)
			os.rename(tempFile,fileName)
			
		return track,fileName

	def getAlbumArt(self,album):
		'''
		Fetches album art from google image search
		'''

		album = album + " Album Art"
		#&source is the advanced search url for a square image with with definition higher than 400x300 
		url = ("https://www.google.com/search?q=" + quote(album.encode('utf-8')) + 
			"&source=imghp?as_st=y&tbm=isch&as_q=&as_epq=&as_oq=&as_eq=&cr=&as_sitesearch=&safe=images&tbs=isz:lt,islt:qsvga,iar:s")
		header = {'User-Agent':
				  '''Mozilla/5.0 (Windows NT 6.1; WOW64)
				  AppleWebKit/537.36 (KHTML,like Gecko)
				  Chrome/43.0.2357.134 Safari/537.36'''
				 }

		soup = BeautifulSoup(urlopen(Request(url, headers=header)), "html.parser")

		albumart_div = soup.find("div", {"class": "rg_meta"})
		albumart = json.loads(albumart_div.text)["ou"]
	
		return albumart

	def getLyrics(self,title):
		'''
		Fetches lyrics from genius.com
		'''
		flag = False
		# Format a request URI for the Genius API
		try:
			search_term = str(title).lower().split('lyrics',1)[0].split('official',1)[0].split('audio',1)[0].replace('(','').replace(')','').replace('[','').replace(']','')
			#print(search_term)
			url = f"https://api.genius.com/search?q={search_term}&access_token={self.genius_access_token}"
			response = requests.get(url)
			json_obj = response.json()
			x=0
			while flag == False:
				#print(x,str(json_obj['response']['hits'][x]['result']['primary_artist']['name'].lower()),flag)
				if 'translations' in str(json_obj['response']['hits'][x]['result']['primary_artist']['name'].lower()):
					flag = False
					x+=1
				elif 'spotify' in str(json_obj['response']['hits'][x]['result']['primary_artist']['name'].lower()):
					flag = False
					x+=1
				else:
					flag = True
			URL = json_obj['response']['hits'][x]['result']['url']
			page = requests.get(URL)
			# Extract the page's HTML as a string
			html = BeautifulSoup(page.text, "html.parser") 
			# Scrape the song lyrics from the HTML
			lyrics = html.find("div", class_="lyrics").get_text().strip()
			return lyrics
		except Exception:
			print(f'Couldn\'t find any lyrics for {title}')
			log.exception('')

	def setData(self,file,artist,title,lyrics,album):
		'''
		Sets artist,title,album cover and lyrics of the specified song (ID3 metedata)
		'''
		audiofile = eyed3.load(file)
		audiofile.tag.artist = artist
		audiofile.tag.title = title
		imagedata = requests.get(album).content
		audiofile.tag.images.set(3, imagedata , "image/jpeg" ,u"Description")
		audiofile.tag.lyrics.set(lyrics)
		audiofile.tag.save()

	def getData(self,file):
		'''
		Fetches artist,title,album cover and lyrics of the specified song (ID3 metedata)
		'''
		audiofile = eyed3.load(file)
		print(f'METADATA:\nArtist: {audiofile.tag.artist}\nTitle: {audiofile.tag.title}\nAlbum: {audiofile.tag.images}')
		print('Lyrics:')
		for lyrics in audiofile.tag.lyrics:
			print(lyrics.text)

	def youtubeToVideo(self):
		'''
		Downloads the video of a youtube url
		'''
		ydl_opts = {
			"format": "bestvideo+bestaudio",
			'outtmpl': '~/Downloads/%(title)s.%(ext)s', 
			"quiet": False,
			'extractaudio' : False,
		}

		try:
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				ydl.download([self.url])
		except Exception:
			log.exception('')
		
	def quality(self):
		with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
			meta = ydl.extract_info(self.url, download=False)
			formats = meta.get('formats')
		for f in formats:
			print(f"{f['ext']}\t{f['format']}")

	def streamVideo(self):
		os.system('mpv --loop --window-scale 0.5 ' + self.url)
		return

if __name__ == '__main__':
	log = logging.getLogger(__name__)
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-v', '--video', help='Downloads the video from a youtube url', action='store', type=str, metavar='URL',nargs=1)
	group.add_argument('-a', '--audio', help='Downloads the audio from a youtube url in mp3 format (embeds album cover and lyrics)', action='store', type=str, metavar='URL',nargs=1)
	group.add_argument('-p', '--play', help='Streams a video from a youtube url (needs mpv installed, only works on linux)', action='store', type=str, metavar='URL',nargs=1)
	group.add_argument('-s', '--search', help='Searches a youtube url from a keyword', action='store', type=str, metavar='URL',nargs=1)

	args = parser.parse_args()

	if args.video:
		video = Video(args.video[0])
		video.youtubeToVideo()
	elif args.audio:
		print(args.audio)
		audio = Video(args.audio[0])
		audio.youtubeToMp3()
	elif args.play:
		play = Video(args.play[0])
		play.streamVideo()
	elif args.search:
		search = Video()
		search.searchVideo(args.search[0])
	else:
		parser.print_help()
