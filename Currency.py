import gvars
from discord import Embed
from discord import TextChannel
from math import ceil
import datetime

client = gvars.client

def botPrint(s):
	print("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "] " + s)

class Currency:
	def __init__(self, name, currencyNameSpaces, conversionRate=None):
		self.name = name
		self.num = 0
		self.nameSpaces = currencyNameSpaces
		self.conversionRate = conversionRate
		gvars.currencies.append(self)

		if (self.conversionRate == None):
			self.conversionRate = gvars.currencyPrices[gvars.currencies.index(self)]

	def parseMessage(self, message):
		if (type(self.nameSpaces) == str):
			self.nameSpaces = [self.nameSpaces]

		self.nameSpaces.append(self.name.lower())

		for nameSpace in self.nameSpaces:
			if (message.content.lower().find(nameSpace) != -1):
				for s in message.content.lower().replace(",", "").replace(nameSpace, "").split(" "):
					try:
						self.num = float(s)
						return True
					except:
						continue

		return False

	@client.event
	async def sendConverstion(self, message):
		await message.channel.send(embed=self.generateEmbed(message))

	def generateEmbed(self, message):
		embed = Embed(title="Juul Pod Currency Converter", description=message.author.mention + " `" + str(self.num) + " " + self.name + "` is approximately `" + str(ceil((self.num / self.conversionRate)*100)/100) + " JP (Juul Pods)`\n `Conversion Rate: ~" + str(self.conversionRate) + " " + self.name + " per JP.`", color=0x8ACC8A)
		embed.set_footer(text="What is this? !jp help | Nullvalue#8123")
		return embed