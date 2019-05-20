# youtube-helper
youtube-helper is a command line interface that helps you download videos and audio (mp3 format with embedded ID3 metadata of title,artist,album cover and lyrics) from youtube urls.

## Installation

	git clone 'https://github.com/Toory/youtube-helper'
	cd youtube-helper/src/
	virtualenv env
	source ./env/bin/activate
	pip install -r requirements.txt #Download all dependencies needed
	python yt.py

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

It is necessary, to fetch lyrics, to put your own [genius](https://genius.com/) API access token in the `__init__` function (genius_access_token variable).

## Coming soon

A graphical interface is coming soon! At first will be in the gui branch.
