from discord import Activity
from discord import ActivityType
from discord import Embed
import string
import asyncio
from Key import Key
from bs4 import BeautifulSoup
import urllib3
import datetime
urllib3.disable_warnings()

import gvars
gvars.init()

from Currency import Currency

client = gvars.client

juul = 15.99/4
updateTime = 3600

def botPrint(s):
	print("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "] " + str(s))

def updateCurrencyConversions():
	pool = urllib3.PoolManager()
	Content = pool.request('GET', 'https://www.x-rates.com/table/?from=USD&amount=1')
	soup = BeautifulSoup(Content.data, 'html.parser')

	currenciesElements = soup.find_all('td', {'class': 'rtRates'})
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
	if (message.content.startswith("!juulpod help") or message.content.startswith("!jp help")):
		desc = "This bot was created in the hopes to normalize all world wide currencies into one essential value. The Cucumber Juul Pod has been a staple of modern day society, and thus it should be the basis for all world wide economies. This bot converts most prominent currencies found around the world into JP (Juul Pods). Below is a list of the supported currencies that can be converted into JP and their recognizable namespaces."

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

	if (message.content.startswith("!juulpod convert") or message.content.startswith("!jp convert")):
		for currency in gvars.currencies:
			if (currency.parseMessage(message)):
				await currency.sendConverstion(message)
				return

client.run(Key)