import yt
import sys
import time
import math
import asyncio
import aiohttp
import logging
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from asyncqt import QEventLoop, asyncSlot, asyncClose, QThreadExecutor

class MainWindow(QMainWindow):

	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.form_widget = YtMainWindow(self)
		self.left = 10
		self.top = 10
		self.width = 500
		self.height = 400
		self.title = 'Youtube Helper'
		self.initUI()
		self.setCentralWidget(self.form_widget)

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		#Icon from Freepik
		self.setWindowIcon(QIcon(QPixmap(('yt-icon.png'))))

class YtMainWindow(QWidget):

	def __init__(self, parent):
		super(YtMainWindow,self).__init__(parent)
		self._SESSION_TIMEOUT = 1.
		self.title = 'Youtube Helper'
		self.player = QMediaPlayer()
		self.playlist = QMediaPlaylist()
		self.userAction = -1  # 0: stopped, 1: playing 2: paused
		#self.buttonList = ['audioButton', 'mpvButton','videoButton','lyricsButton','playButton','pauseButton','stopButton']
		self.lastUrl = ''
		self.streamUrl = ''
		self.initUI()

	def initUI(self):
		self.createGridLayout()
		windowLayout = QVBoxLayout()
		windowLayout.addWidget(self.horizontalGroupBox)
		self.setLayout(windowLayout)
		self.startSession()
		self.show()

	@asyncSlot()
	async def startSession(self):
		self.session = aiohttp.ClientSession(
			loop=asyncio.get_event_loop(),
			timeout=aiohttp.ClientTimeout(total=self._SESSION_TIMEOUT))

	def createGridLayout(self):
		self.label = QLabel('Insert youtube url or search title:')
		self.label.setAlignment(Qt.AlignCenter)
		self.linedit = QLineEdit('https://www.youtube.com/watch?v=pWn7PYm-W90')
		self.Urllabel = QLabel('Url: ')
		self.Urllabel.setAlignment(Qt.AlignCenter)
		self.Urlline = QLineEdit()
		self.Titlelabel = QLabel('Title: ')
		self.Titlelabel.setAlignment(Qt.AlignCenter)
		self.Titleline = QLineEdit()
		self.infoText = QTextEdit()
		self.audioButton = QPushButton('Download audio!',self)
		self.mpvButton = QPushButton('Stream with mpv',self)
		self.videoButton = QPushButton('Download video!',self)
		self.urlButton = QPushButton('Find..',self)
		self.lyricsButton = QPushButton('Get lyrics',self)
		self.playButton = QPushButton('Play audio',self)
		self.pauseButton = QPushButton('Pause audio',self)
		self.stopButton = QPushButton('Stop audio',self)
		self.progressBar = QProgressBar()
		self.progressBar.setFormat(f'00:00 : 00:00 | 00%')
		self.progressBar.setMaximum(100)
		self.volumeslider = QSlider(Qt.Horizontal, self)
		self.volumeslider.setFocusPolicy(Qt.NoFocus)
		self.volumeslider.valueChanged[int].connect(self.changeVolume)
		self.volumeslider.setValue(50)
		self.songName = QLabel('-')
		self.songName.setAlignment(Qt.AlignCenter)
		# Disable buttons before fetch
		self.audioButton.setEnabled(False)
		self.mpvButton.setEnabled(False)
		self.videoButton.setEnabled(False)
		self.lyricsButton.setEnabled(False)
		self.playButton.setEnabled(False)
		self.pauseButton.setEnabled(False)
		self.stopButton.setEnabled(False)

		self.horizontalGroupBox = QGroupBox()
		layout = QGridLayout()

		layout.addWidget(self.label,0,0,1,3)
		layout.addWidget(self.linedit,1,0,1,2)
		layout.addWidget(self.urlButton,1,2,1,1)
		layout.addWidget(self.Urllabel,2,0,1,1)
		layout.addWidget(self.Urlline,2,1,1,2)
		layout.addWidget(self.Titlelabel,3,0,1,1)
		layout.addWidget(self.Titleline,3,1,1,2)
		layout.addWidget(self.audioButton,4,0,1,1)
		layout.addWidget(self.mpvButton,4,1,1,1)
		layout.addWidget(self.videoButton,4,2,1,1)
		layout.addWidget(self.infoText,5,0,1,3)
		layout.addWidget(self.playButton,6,0,1,1)
		layout.addWidget(self.pauseButton,6,1,1,1)
		layout.addWidget(self.stopButton,6,2,1,1)
		layout.addWidget(self.volumeslider,7,0,1,2)
		#layout.addWidget(self.repeatCb,7,1,1,1)
		layout.addWidget(self.lyricsButton,7,2,1,1)
		layout.addWidget(self.progressBar,8,0,1,3)
		self.horizontalGroupBox.setLayout(layout)

		self.urlButton.clicked.connect(self.fetch)
		self.audioButton.clicked.connect(self.downAudio)
		self.mpvButton.clicked.connect(self.openMpv)
		self.videoButton.clicked.connect(self.downVideo)
		self.lyricsButton.clicked.connect(self.getLyrics)
		self.playButton.clicked.connect(self.playAudio)
		self.stopButton.clicked.connect(self.stopAudio)
		self.pauseButton.clicked.connect(self.pauseAudio)
		#self.repeatCb.stateChanged.connect(self.repeatAudio)

	@asyncClose
	async def closeEvent(self, event):
		await self.session.close()

	@asyncSlot()
	async def fetch(self):
		self.urlButton.setEnabled(False)
		text = self.linedit.text()
		self.infoText.setText('Loading...')

		if not text:
			self.songName.setText('Error, box is empty!!')
			return
		try:
			if 'https' in text or '.com' in text: # means it's a url
				self.Urlline.setText(text)
				with QThreadExecutor(1) as exec:
					video = await loop.run_in_executor(exec, yt.Video,text)
					title = await loop.run_in_executor(exec,video.printInfo)
				self.Titleline.setText(title)
			else: # not an url, try to search it on youtube
				with QThreadExecutor(1) as exec:
					video = await loop.run_in_executor(exec, yt.Video,'')
					url = await loop.run_in_executor(exec,video.searchVideo,text)
					self.Urlline.setText(url)
					self.Titleline.setText(await loop.run_in_executor(exec,video.printInfo))
			self.infoText.setText(f'Done!\nFound {title}')
		except Exception as e:
			print(e)
		finally:
			self.audioButton.setEnabled(True)
			self.mpvButton.setEnabled(True)
			self.videoButton.setEnabled(True)
			self.lyricsButton.setEnabled(True)
			self.playButton.setEnabled(True)
			self.pauseButton.setEnabled(True)
			self.stopButton.setEnabled(True)
			self.urlButton.setEnabled(True)

	@asyncSlot()
	async def downAudio(self):
		self.audioButton.setEnabled(False)
		url = self.Urlline.text()

		if url == '':
			self.songName.setText('Error, Enter a youtube url!')
			return
		try:
			with QThreadExecutor(1) as exec:
				video = await loop.run_in_executor(exec,yt.Video,url)
				await loop.run_in_executor(exec,video.youtubeToMp3)
		except Exception as e:
			print(e)
		finally:
			self.audioButton.setEnabled(True)

	@asyncSlot()
	async def openMpv(self):
		self.mpvButton.setEnabled(False)
		
		url = self.Urlline.text()
		try:
			with QThreadExecutor(1) as exec:
				video = await loop.run_in_executor(exec,yt.Video,url)
				await loop.run_in_executor(exec,video.streamVideo)
		except Exception as e:
			print(e)
		finally:
			self.mpvButton.setEnabled(True)

	@asyncSlot()
	async def downVideo(self):
		self.videoButton.setEnabled(False)
		url = self.Urlline.text()

		if url == '':
			self.songName.setText('Error, Enter a youtube url!')
			return
		try:
			with QThreadExecutor(1) as exec:
				video = await loop.run_in_executor(exec,yt.Video,url)
				await loop.run_in_executor(exec,video.youtubeToVideo)
		except Exception as e:
			print(e)
		finally:
			self.videoButton.setEnabled(True)

	@asyncSlot()
	async def getLyrics(self):
		title = self.Titleline.text()
		if title == '':
			self.songName.setText('Error, Enter a title!')
			return
		with QThreadExecutor(2) as exec:
			video = await loop.run_in_executor(exec, yt.Video,'')
			lyrics = await loop.run_in_executor(exec, video.getLyrics,title)
		self.infoText.setText(lyrics)

	@asyncSlot()
	async def playAudio(self):
		#need code here that stops previous progressbar Threads..
		if self.userAction != 0:
			loop.call_soon_threadsafe(self.stopAudio)
		url = self.Urlline.text()
		if url == '':
			self.songName.setText('Error, Enter a youtube url!')
			return
		with QThreadExecutor(3) as exec:
			# if last song was the same there is no need to fetch streamUrl again
			if self.lastUrl != url:
				video = await loop.run_in_executor(exec, yt.Video,url)
				self.streamUrl = await loop.run_in_executor(exec, video.fetchStream)
			self.lastUrl = self.Urlline.text()
			mc = QMediaContent(QUrl(self.streamUrl))
			self.player.setMedia(mc)
			self.player.play()
			self.userAction = 1
			loop.call_soon_threadsafe(self.startProgressBar)

#	@asyncSlot()
#	async def repeatAudio(self):
#		if self.repeatCb.isChecked():
#			with QThreadExecutor(3) as exec:
#				url = self.Urlline.text()
#				if url == '':
#					self.songName.setText('Error, Enter a youtube url!')
#					return
#				video = await loop.run_in_executor(exec, yt.Video,url)
#				streamUrl = await loop.run_in_executor(exec, video.fetchStream)
#				duration = await loop.run_in_executor(exec, video.duration)-2
#				print(streamUrl)
#			while self.repeatCb.isChecked():
#				print(self.userAction)
#				if self.userAction != 1 and self.userAction != 2:
#					mc = QMediaContent(QUrl(streamUrl))
#					self.player.setMedia(mc)
#					self.player.play()
#					self.userAction = 1
#					loop.call_soon_threadsafe(self.startProgressBar)
#				else:
#					with QThreadExecutor(6) as exec:
#						await loop.run_in_executor(exec,time.sleep,duration)
#		else:
#			loop.call_soon_threadsafe(self.stopAudio)

#	@asyncSlot()
#	async def repeatAudio(self):
#		if self.repeatCb.isChecked():
#			while self.repeatCb.isChecked():
#				#	print(self.userAction,end='')
#				if self.userAction != 1 and self.userAction != 2:
#					loop.call_soon_threadsafe(self.playAudio)
#				else:
#					with QThreadExecutor(5) as exec:
#						await loop.run_in_executor(exec, self.wait_)
#		else:
#			loop.call_soon_threadsafe(self.stopAudio)


#	def wait_(self,timeout=500, period=0.25):
#		mustend = time.time() + timeout
#		while time.time() < mustend:
#			if self.userAction != 1 and self.userAction != 2:
#				return True
#			time.sleep(period)
#		return False

	@asyncSlot()
	async def pauseAudio(self):
		if self.userAction == 2:
			self.player.play()
			self.userAction = 1
		else:
			self.player.pause()
			self.userAction = 2
		return
		
	@asyncSlot()
	async def stopAudio(self):
		self.userAction = 0
		self.player.stop()
		self.progressBar.setValue(0)
		self.progressBar.setFormat(f'00:00 : 00:00 | 00%')

	@asyncSlot()
	async def startProgressBar(self):
		self.progressBar.setValue(0)
		url = self.Urlline.text()
		with QThreadExecutor(4) as exec:
			video = await loop.run_in_executor(exec, yt.Video,url)
			duration = await loop.run_in_executor(exec, video.duration)-1
			await loop.run_in_executor(exec,self.progress,duration)

	def progress(self,duration):
		count = 0

		Minutes = int(math.floor(duration/60))
		Seconds = int(duration % 60)
		songDuration = f'{Minutes:02d}:{Seconds:02d}'
		self.progressBar.setRange(0,duration)

		while count < duration:
			if self.userAction == 0:
				return
			elif self.userAction == 1:
				pass
			elif self.userAction == 2:
				timeout = self.wait_until()
				if timeout == False:
					return

			count += 1
			time.sleep(1)
			self.progressBar.setValue(count)
			if count >= 60:
				Minutes = int(math.floor(count/60))
				Seconds = int(count % 60)
				self.progressBar.setFormat(f'{Minutes:02d}:{Seconds:02d} : {songDuration} | {(int((count/duration)*100)):02d}%')
			else:
				self.progressBar.setFormat(f'00:{count:02d} : {songDuration} | {(int((count/duration)*100)):02d}%')
		
		#after player stops, put userAction to stopped
		self.userAction = 0

	def wait_until(self,timeout=200, period=0.25):
		mustend = time.time() + timeout
		while time.time() < mustend:
			if self.userAction == 1:
				return True
			time.sleep(period)
		return False

	def changeVolume(self, value):
		self.player.setVolume(value)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	loop = QEventLoop(app)
	asyncio.set_event_loop(loop)

	mainWindow = MainWindow()
	mainWindow.show()

	with loop:
		sys.exit(loop.run_forever())
