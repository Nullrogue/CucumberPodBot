import gvars
gvars.init()

from mutagen.mp3 import MP3
from Currency import Currency
from discord import Activity
from discord import ActivityType
from discord import Embed
from discord import FFmpegPCMAudio
from discord import errors
from discord import Guild
from discord import User
from discord import TextChannel
from discord import DMChannel
from discord import ClientException
from discord import VoiceRegion
from asyncio import ensure_future
from asyncio import sleep
from Logging import *
from random import choice
from math import ceil
from glob import glob
from bs4 import BeautifulSoup

try:
	from Key import *
	x = dblKey
	x = Key
except Exception as e:
	print("Couldn't import API keys.")
	raise

import traceback
import datetime
import urllib3
import string
import dbl
import re
import os

urllib3.disable_warnings()
client = gvars.client

dblpy = dbl.DBLClient(client, dblKey)

audio_dir = os.path.dirname(os.path.realpath(__file__)) + "/audio_files/"
audio_files = glob(audio_dir + "*.mp3")

juul = 15.99/4
updateTime = 5

def updateCurrencyConversions():
	try:
		pool = urllib3.PoolManager()
		Content = pool.request('GET', 'https://www.x-rates.com/table/?from=USD&amount=1')
		soup = BeautifulSoup(Content.data, 'html.parser')

		currenciesElements = soup.find_all('td', {'class': 'rtRates'})

		currenciesElements = currenciesElements[:20]
		for k, v in enumerate(currenciesElements):
			if (k % 2 != 0 or k != 0):
				del currenciesElements[k]

		if (gvars.currencyPrices == []):
			for k, v in enumerate(currenciesElements):
				gvars.currencyPrices.append(float(v.contents[0].decode_contents()) * juul)
		else:
			for k, v in enumerate(currenciesElements):
				gvars.currencyPrices[k] = float(v.contents[0].decode_contents()) * juul
	except Exception as e:
		pass

updateCurrencyConversions()

Currency("Euros", ["euro", "€"])
Currency("British Pounds", ["pound", "£"])
Currency("Indian Rupees", ["rupee", "₹"])
Currency("Australian Dollars", "aud")
Currency("Canadian Dollars", "cad")
Currency("Singapore Dollars", "sgd")
Currency("Swiss Francs", ["franc", "fr."])
Currency("Malaysian Ringgits", ["ringgit", "rm", "myr"])
Currency("Japanese Yen", ["yen", "¥"])
Currency("Chinese Yuan", ["yuan", "cny", "元"])
Currency("US Dollars", ["dollar", "usd", "$"], 3.99)
Currency("Riot Points", ["riot point", "rp"], 518.7)
Currency("V-Bucks", ["v buck", "v-buck"], 399)
Currency("Robux", ["robux", "rbx"], 322.4)
Currency("Big Macs", ["big mac", "bigmac"], 3.99)
Currency("Chicken McNuggets", ["nugget", "mcnugget", "nuggies"], 8.886)

@client.event
async def update_stats():
	while not client.is_closed():
		try:
			await dblpy.post_guild_count()
			await sleep(1800)
		except Exception as e:
			if (e.response.status != None and not re.match("5[0-9]*", e.response.status)):
				await ErrorHandler(None, exception=e)
				await sleep(1800)
			else:
				await sleep(300)

def botPrint(s, process=False):
	if (not process):
		print("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(s))
	else:
		print("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(s), end="")
	
@client.event
async def timerTask(time):
	await sleep(time)
	updateCurrencyConversions()
	currencyTimer = ensure_future(timerTask(updateTime))

@client.event
async def on_ready():
	for guild in client.guilds:
		if (not guild.me):
			botPrint("Leaving guild: " + str(guild.id))
			await guild.leave()

	botPrint('------')
	botPrint('Logged in as')
	botPrint(client.user.name)
	botPrint(client.user.id)
	botPrint("Guilds: " + str(len(client.guilds)))
	botPrint('------')

	print("")
	initLogs()
	print("")

	await client.change_presence(activity=Activity(type=ActivityType.watching, name="!jp help"))
	
	currencyTimer = ensure_future(timerTask(updateTime))

	if (client.user.id == 445098740085161987):
		updateTask = client.loop.create_task(update_stats())

@client.event
async def on_message(message):
	try:
		if (not message.author.bot and message.content.lower().startswith("!juulpod ") or message.content.lower().startswith("!jp ")):
			if (type(message.channel) != DMChannel and not message.channel.permissions_for(message.guild.me).send_messages):
				await message.author.send("I cannot send messages in channel: " + message.channel.mention)
				return

			if (message.content.lower().startswith("!juulpod rip") or message.content.lower().startswith("!jp rip") and type(message.channel) == TextChannel):
				logWrite(message.guild, "COMMAND CALLED \"rip\" BY USER: " + str(message.author) + "(" + str(message.author.id) + ") IN TEXT CHANNEL: " + message.channel.name + "(" + str(message.channel.id) + ")")
				if (message.author.voice):
					try:
						if (message.author.voice.channel.permissions_for(message.guild.me).connect):
							vc = await message.author.voice.channel.connect()
							logWrite(message.guild, "\tJoined VoiceChannel: " + message.author.voice.channel.name + "(" + str(message.author.voice.channel.id) + ")")
						else:
							raise Exception("Don't have permission to join channel")
					except Exception as e:
						logWrite(message.guild, "\tAttempted to join VoiceChannel: " + message.author.voice.channel.name + "(" + str(message.author.voice.channel.id) + ") but failed because: " + str(e))
						if (type(e) == ClientException):
							await message.channel.send(message.author.mention + " I'm busy rippin' rn...")
						else:
							await message.channel.send(message.author.mention + " Bruh I don't have permissions to join...")
						return
					
					await message.delete()

					audio_file = choice(audio_files)
					try:
						vc.play(FFmpegPCMAudio(audio_file))
					except:
						vc.play(FFmpegPCMAudio(executable=gvars.ffmpegPath, source=audio_file))
					
					logWrite(message.guild, "\tPlaying audio file: " + audio_file.replace("\\", "/"))
					await sleep(ceil(MP3(audio_file).info.length))

					vc.stop()
					await vc.disconnect()
					logWrite(message.guild, "\tDisconnected from VoiceChannel")
				else:
					await message.channel.send(message.author.mention + " You aren't currently in a voice channel bro.")
					logWrite(message.guild, "\tUser is not connected to a VoiceChannel")

				return

			if (message.content.lower().startswith("!juulpod help") or message.content.lower().startswith("!jp help")):
				logWrite(message.guild, "COMMAND CALLED \"help\" BY USER: " + str(message.author) + "(" + str(message.author.id) + ") IN TEXT CHANNEL: " + ["DM", str(message.channel)][hasattr(message.channel, 'name')] + "(" + str(message.channel.id) + ")")
				
				desc = "This bot was created in the hopes to normalize all world wide currencies into one essential value. The Cucumber Juul Pod has been a staple of modern day society, and thus it should be the basis for all world wide economies. This bot converts most prominent currencies found around the world into JP (Juul Pods). Below is a list of the supported currencies that can be converted into JP and their recognizable namespaces.\n[[Nullvalue#8123](https://discordbots.org/user/157662210481586176)] [[Github](https://github.com/NullvaIue/CucumberPodBot)] [[Support Server](https://discord.gg/Nyy7C3n)] [[Invite Bot](https://discordapp.com/oauth2/authorize?client_id=445098740085161987&scope=bot&permissions=36727824)]"

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

				emb.add_field(name="Commands", value="`!jp rip`\n`!jp convert [number] [namespace] (Ex. !juulpod convert 500 usd)`\n", inline=False)
				emb.add_field(name="Currencies", value=currencyText, inline=True)
				emb.add_field(name="Namespaces", value=namespaceText, inline=True)
				await message.channel.send(embed=emb)

				logWrite(message.guild, "\tSent help message for user: " + str(message.author) + "(" + str(message.author.id) + ") in TextChannel: " + ["DM", str(message.channel)][hasattr(message.channel, 'name')] + "(" + str(message.channel.id) + ")")
				
				return

			if (message.content.lower().startswith("!juulpod convert") or message.content.lower().startswith("!jp convert")):
				logWrite(message.guild, "COMMAND CALLED \"convert\" BY USER: " + str(message.author) + "(" + str(message.author.id) + ") IN TEXT CHANNEL: " + ["DM", str(message.channel)][hasattr(message.channel, 'name')] + "(" + str(message.channel.id) + ")")
				for currency in gvars.currencies:
					if (currency.parseMessage(message)):
						logWrite(message.guild, "\tMatched currency: " + currency.name)
						if (any(char.isdigit() for char in message.content)):
							await currency.sendConversion(message)
							logWrite(message.guild, "\tSent conversion: " + str(currency.num) + " " + currency.name + " to JP = " + str(currency.num/currency.conversionRate))
						else:
							logWrite(message.guild, "\tNo number given in message.")
							await message.channel.send(message.author.mention + " You did not include a number to convert!")
							logWrite(message.guild, "\tSent message indicating no digits in string.")
						return

				await message.channel.send(message.author.mention + " Unknown currency, `!jp help` for a list of supported currencies.")
				logWrite(message.guild, "\tNo currency recognized in message: \"" + message.content + "\"")
				return

			await message.channel.send(message.author.mention + " Unknown command, `!jp help` for a list of commands.")
			logWrite(message.guild, "No command recognized in message: \"" + message.content + "\" BY USER: " + str(message.author) + "(" + str(message.author.id) + ")")
	except Exception as e:
		if (message.guild):
			await ErrorHandler(location=message.guild, member=message.author, exception=e)
		else:
			await ErrorHandler(location=message.author, exception=e)

		raise

client.run(Key)