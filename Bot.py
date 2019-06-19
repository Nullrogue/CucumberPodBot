import discord
import string
import asyncio
from Key import Key
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()
from math import ceil

client = discord.Client()

juul = 15.99/4

currencyPrices = []
currencies = []

def updateCurrencyConversions():
	pool = urllib3.PoolManager()
	Content = pool.request('GET', 'https://www.x-rates.com/table/?from=USD&amount=1')
	soup = BeautifulSoup(Content.data, 'html.parser')

	currenciesElements = soup.find_all('td', {'class': 'rtRates'})
	print("Updating conversion rates for national currencies...")

	currenciesElements = currenciesElements[:20]
	for k, v in enumerate(currenciesElements):
		if (k % 2 != 0 or k != 0):
			del currenciesElements[k]

	if (currencyPrices == []):
		for k, v in enumerate(currenciesElements):
			currencyPrices.append(float(v.contents[0].decode_contents()) * juul)
	else:
		for k, v in enumerate(currenciesElements):
			currencyPrices[k] = float(v.contents[0].decode_contents()) * juul
	print("Done!...")

@client.event
async def timerTask(time):
	await asyncio.sleep(time)
	timerHandler()

def timerHandler():
	updateCurrencyConversions()
	currencyTimer = asyncio.ensure_future(timerTask(300))

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!jp help"))

	currencyTimer = asyncio.ensure_future(timerTask(300))
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
		#HELP COMMAND
	if (message.content.startswith("!juulpod convert") or message.content.startswith("!jp convert")):
		for currency in currencies:
			if (currency.parseMessage(message)):
				await currency.sendConverstion(message)
				return

class Currency:
	def __init__(self, name, currencyNameSpaces, conversionRate=None):
		self.name = name
		self.nameSpaces = currencyNameSpaces
		self.conversionRate = conversionRate
		currencies.append(self)

		if (self.conversionRate == None):
			self.conversionRate = currencyPrices[currencies.index(self)]

	def parseMessage(self, message):
		if (type(self.nameSpaces) is str):
			if (message.content.lower().find(self.nameSpaces) != -1):
				msg = message.content.lower().replace(self.nameSpaces, "")

				for s in msg.split(" "):
					if (s.isdigit()):
							self.num = float(s)
							break
				return True
			else:
				return False
		elif (type(self.nameSpaces) is list):
			for nameSpace in self.nameSpaces:
				if (message.content.lower().find(nameSpace) != -1):
					for nameSpace in self.nameSpaces:
						msg = message.content.lower().replace(nameSpace, "")
					for s in msg.split(" "):
						if (s.isdigit()):
							self.num = float(s)
							break
					return True

			return False

	@client.event
	async def sendConverstion(self, message):
		await message.channel.send(embed=self.generateEmbed(self.num, message))

	def generateEmbed(self, num, message):
		embed = discord.Embed(title="Juul Pod Currency Converter", description=message.author.mention + " `" + str(num) + " " + self.name + "` is approximately `" + str(ceil((num / self.conversionRate)*100)/100) + " JP (Juul Pods)`\n `Conversion Rate: ~" + str(self.conversionRate) + " " + self.name + " per JP.` [What is this?](https://pastebin.com/raw/PbggM78C)", color=0x8ACC8A)
		return embed

client.run(Key)