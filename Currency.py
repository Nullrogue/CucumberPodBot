import gvars
from discord import Embed
from math import ceil
import datetime

client = gvars.client

def botPrint(s):
	print("[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "] " + s)

class Currency:
	def __init__(self, name, currencyNameSpaces, conversionRate=None):
		self.name = name
		self.nameSpaces = currencyNameSpaces
		self.conversionRate = conversionRate
		gvars.currencies.append(self)

		if (self.conversionRate == None):
			self.conversionRate = gvars.currencyPrices[gvars.currencies.index(self)]

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
		embed = Embed(title="Juul Pod Currency Converter", description=message.author.mention + " `" + str(num) + " " + self.name + "` is approximately `" + str(ceil((num / self.conversionRate)*100)/100) + " JP (Juul Pods)`\n `Conversion Rate: ~" + str(self.conversionRate) + " " + self.name + " per JP.` What is this? !jp help", color=0x8ACC8A)
		botPrint("(GID: " + str(message.guild.id) + ") " + "Converting " + str(num) + " " + self.name + " for user: " + str(message.author) + "...")
		return embed