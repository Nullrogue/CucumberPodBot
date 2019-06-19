import discord

def init():
	global currencyPrices
	currencyPrices = []

	global currencies
	currencies = []

	global client
	client = discord.Client()