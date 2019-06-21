from discord import Activity
from discord import ActivityType
from discord import Embed
from discord import FFmpegPCMAudio
from discord import errors

import string
import asyncio

from Key import Key
from bs4 import BeautifulSoup

from random import choice
from math import ceil

import urllib3
urllib3.disable_warnings()

from mutagen.mp3 import MP3

from glob import glob
import os

import datetime
import pafy

import gvars
gvars.init()

from Currency import Currency

client = gvars.client

audio_dir = os.path.dirname(os.path.realpath(__file__)) + "/audio_files/"
audio_files = glob(audio_dir + "*.mp3")

juul = 15.99/4
updateTime = 3600

def botPrint(s):
	print("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "] " + str(s))

def updateCurrencyConversions():
	pool = urllib3.PoolManager()
	Content = pool.request('GET', 'https://www.x-rates.com/table/?from=USD&amount=1')
	soup = BeautifulSoup(Content.data, 'html.parser')

	currenciesElements = soup.find_all('td', {'class': 'rtRates'})
	print("")
	botPrint("Updating conversion rates for national currencies...")

	currenciesElements = currenciesElements[:20]
	for k, v in enumerate(currenciesElements):
		if (k % 2 != 0 or k != 0):
			del currenciesElements[k]

	if (gvars.currencyPrices == []):
		for k, v in enumerate(currenciesElements):
			gvars.currencyPrices.append(float(v.contents[0].decode_contents()) * juul)
	else:
		for k, v in enumerate(currenciesElements):
			difference = (float(v.contents[0].decode_contents()) * juul) - gvars.currencyPrices[k]
			sign = "+" if difference >= 0 else "-" 
			botPrint(gvars.currencies[k].name + ": " + sign + str(abs(difference)))
			gvars.currencyPrices[k] = float(v.contents[0].decode_contents()) * juul
	botPrint("Done!...")
	
@client.event
async def timerTask(time):
	await asyncio.sleep(time)
	timerHandler()

def timerHandler():
	updateCurrencyConversions()
	currencyTimer = asyncio.ensure_future(timerTask(updateTime))

@client.event
async def on_ready():
	botPrint('------')
	botPrint('Logged in as')
	botPrint(client.user.name)
	botPrint(client.user.id)
	botPrint('------')

	await client.change_presence(activity=Activity(type=ActivityType.watching, name="!jp help"))

	currencyTimer = asyncio.ensure_future(timerTask(updateTime))
	updateCurrencyConversions()

	Currency("Euros", ["euro", "€"])
	Currency("British Pounds", ["pound", "£"])
	Currency("Indian Rupees", ["rupee", "₹"])
	Currency("Australian Dollars", "aud")
	Currency("Canadian Dollars", "cad")
	Currency("Singapore Dollars", "sgd")
	Currency("Swiss Francs", ["franc", "fr."])
	Currency("Malaysian Ringgits", ["ringgit", "rm", "myr"])
	Currency("Japanese Yen", ["yen", "yen", "¥"])
	Currency("Chinese Yuan", ["yuan", "cny", "元"])
	Currency("US Dollars", ["dollar", "usd", "$"], 3.99)
	Currency("Riot Points", ["riot points", "rp"], 518.7)
	Currency("V-Bucks", ["v bucks", "v-bucks"], 399)
	Currency("Robux", ["robux", "rbx"], 322.4)
	Currency("Big Macs", "big mac", 3.99)
	Currency("Chicken McNuggets", ["nugget", "mcnuggets", "nuggies"], 8.886)

@client.event
async def on_message(message):
	if (not message.author.bot):
		if (message.content.lower().startswith("!juulpod rip") or message.content.lower().startswith("!jp rip")):
			if (message.author.voice):
				channel = message.author.voice.channel
				vc = await channel.connect()
				audio_file = choice(audio_files)
				try:
					vc.play(FFmpegPCMAudio(audio_file))
				except:
					vc.play(FFmpegPCMAudio(executable="C:/Program Files (x86)/ffmpeg/bin/ffmpeg.exe", source=audio_file))

				await asyncio.sleep(ceil(MP3(audio_file).info.length))

				vc.stop()
				await vc.disconnect()
			else:
				await message.channel.send(message.author.mention + " You aren't currently in a voice channel bro.")
			return

		if (message.content.lower().startswith("!juulpod help") or message.content.lower().startswith("!jp help")):
			desc = "This bot was created in the hopes to normalize all world wide currencies into one essential value. The Cucumber Juul Pod has been a staple of modern day society, and thus it should be the basis for all world wide economies. This bot converts most prominent currencies found around the world into JP (Juul Pods). Below is a list of the supported currencies that can be converted into JP and their recognizable namespaces. -Nullvalue#8123"

			emb = Embed(title="Juul Pod Help", color=0x8ACC8A, description=desc)
			currencyText = ""
			namespaceText = ""
			for cur in gvars.currencies:
				currencyText += cur.name + "\n"
				if (type(cur.nameSpaces) is str):
					namespaceText += "(\'" + cur.nameSpaces + "\')\n"
				elif (type(cur.nameSpaces) is list):
					namespaceText += "("
					for nameSpace in cur.nameSpaces:
						if (nameSpace != cur.nameSpaces[len(cur.nameSpaces) - 1]):
							namespaceText += "\'" + nameSpace + "\', "
						else:
							namespaceText += "\'" + nameSpace + "\')\n"

			emb.add_field(name="Currencies", value=currencyText, inline=True)
			emb.add_field(name="Name Spaces", value=namespaceText, inline=True)
			await message.channel.send(embed=emb)
			return

		if (message.content.lower().startswith("!juulpod convert") or message.content.lower().startswith("!jp convert")):
			for currency in gvars.currencies:
				if (currency.parseMessage(message)):
					await currency.sendConverstion(message)
					return

			await message.channel.send(message.author.mention + " Unknown currency, `!jp help` for a list of supported currencies.")

client.run(Key)