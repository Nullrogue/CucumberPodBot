from discord import Client

def init():
	global currencyPrices
	currencyPrices = []

	global currencies
	currencies = []

	global client
	client = Client()