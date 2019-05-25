# youtube-helper
youtube-helper is a GUI application that helps you download & listen to videos and audio, discover music and much more.

## Installation

	git clone 'https://github.com/Toory/youtube-helper'
	cd youtube-helper/src/
	virtualenv env
	source ./env/bin/activate
	pip install -r requirements.txt #Download all dependencies needed
	python ytGUI.py

## Usage

<p align="center"> 
  <img src="https://i.imgur.com/OPa1VRu.gif">
</p>


- **Find..**: fetchs data from a youtube url or title

- **Download Audio**: downloads audio (mp3 format with embedded ID3 metadata of title,artist,album cover and lyrics)

- **Stream with mpv**: open the video on mpv (works only on linux, needs mpv installed) 

- **Download Video**: downloads video (highest resolution possible, usually mkw format)

- **Play/Pause/Stop**: Play/Pause/Stop song/video

- **Get lyrics**: Fetches lyrics 

- **Discover Music**: Plays a random song between the spotify weekly global top 200

It is necessary, to fetch lyrics, to put your own [genius](https://genius.com/) API access token in the `__init__` function (genius_access_token variable).
	
# youtube-helper cli

youtube-helper can also be used on the command line.

## Usage

	usage: yt.py [-h] [-v URL | -a URL | -p URL | -s URL]
	
	Arguments:
		-h, --help            show this help message and exit
		-v URL, --video URL   Downloads the video from a youtube url
		-a URL, --audio URL   Downloads the audio from a youtube url in mp3 format
		(embeds ID3 metadata of title,artist,album cover and lyrics)
		-p URL, --play URL    Streams a video from a youtube url 
		(needs mpv installed, only works on linux)
		-s URL, --search URL  Searches a youtube url from a keyword
