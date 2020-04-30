from discord import Client
from discord import VoiceRegion

def init():
	global currencyPrices
	currencyPrices = []

	global currencies
	currencies = []

	global ffmpegPath
	ffmpegPath = "D:/Software/ffmpeg/bin/ffmpeg.exe"

	global client
	client = Client()