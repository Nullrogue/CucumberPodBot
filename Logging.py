from discord import Guild
from discord import User
from dateutil import tz
from pbwrap import Pastebin
from Key import pbKey
from Key import pbUser
from Key import pbPass

import traceback
import os
import datetime
import gvars

client = gvars.client

def botPrint(s, process=False):
	if (not process):
		print("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(s))
	else:
		print("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(s), end="")

@client.event
async def on_guild_join(guild):
	if (os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/logs/" + str(guild.id) + ".log")):
		logWrite(guild, "BOT RE-ADDED TO GUILD")
	else:
		createLogFile(guild)

	logWrite(None, "Bot joined guild: " + str(guild) + "(" + str(guild.id) + ")")

@client.event
async def on_guild_remove(guild):
	if (os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/logs/" + str(guild.id) + ".log")):
		logWrite(guild, "BOT REMOVED FROM GUILD")

	logWrite(None, "Bot removed from guild: " + str(guild) + "(" + str(guild.id) + ")")

def initLogs():
	if (not os.path.isdir(os.path.dirname(os.path.realpath(__file__)) + "/logs/")):
		botPrint("[LOGGING] No logging directory found, creating one...", process=True)
		os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "/logs/")
		print("DONE!")
		
	if (not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/logs/bot.log")):
		botPrint("[LOGGING] No bot log found, creating one...", process=True)
		open(os.path.dirname(os.path.realpath(__file__)) + "/logs/bot.log", 'a+', encoding="utf-8")
		print("DONE!")

	if (not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/logs/errors.log")):
		botPrint("[LOGGING] No error log found, creating one...", process=True)
		open(os.path.dirname(os.path.realpath(__file__)) + "/logs/errors.log", 'a+', encoding="utf-8")
		print("DONE!")

	for guild in client.guilds:
		if (not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/logs/" + str(guild.id) + ".log")):
			botPrint("[LOGGING] Creating log for GID: " + str(guild.id) + "...", process=True)
			createLogFile(guild)
			print("DONE!")

	botPrint("[LOGGING] Enabled...")

@client.event
async def errorWrite(string, exception):
	logFile = open(os.path.dirname(os.path.realpath(__file__)) + "/logs/errors.log", 'a+', encoding="utf-8")
	logFile.write("----------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
	logFile.write("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(string) + "\n" + traceback.format_exc())
	
	me = await client.fetch_user(157662210481586176)
	eMessage = "```" + str(string) + "\n" + traceback.format_exc() + "```"
	if (len(eMessage) >= 2000):
		pb = Pastebin(pbKey)
		pb.authenticate(pbUser, pbPass)
		url = pb.create_paste(eMessage, api_paste_private=1, api_paste_name="ERROR: " + type(exception).__name__)
		await me.send("ERROR: " + url)
	else:
		await me.send(eMessage)

	logFile.close()
	
def logWrite(guild, string):
	if (guild == None):
		logFile = open(os.path.dirname(os.path.realpath(__file__)) + "/logs/bot.log", 'a+', encoding="utf-8")
		logFile.write("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(string) + "\n")
		logFile.close()
	else:
		logFile = open(os.path.dirname(os.path.realpath(__file__)) + "/logs/" + str(guild.id) + ".log", 'a+', encoding="utf-8")
		logFile.write("[" + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "] " + str(string) + "\n")
		logFile.close()

def createLogFile(guild):
	logFile = open(os.path.dirname(os.path.realpath(__file__)) + "/logs/" + str(guild.id) + ".log", 'a+', encoding="utf-8")
	logFile.write("-------------------------------------\n")
	logFile.write("Log File Created: " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S") + "\n")
	logFile.write("Bot joined guild: " + str(guild.me.joined_at.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime("%m-%d-%Y %H:%M:%S\n")))
	logFile.write("GUILD INFO:\n")
	logFile.write("\tNAME: " + guild.name + "\n")
	logFile.write("\tOWNER: " + str(guild.owner) + "\n")
	logFile.write("\tOWNERID: " + str(guild.owner.id) + "\n")
	logFile.write("-------------------------------------\n")

@client.event
async def ErrorHandler(location, exception, member=None):
	numLines = 0
	for numLines, l in enumerate(open(os.path.dirname(os.path.realpath(__file__)) + "/logs/errors.log", 'r+', encoding="utf-8")):
		pass
	if (type(location) is Guild):
		logWrite(location, "ERROR: (User: " + str(member) + "(" + str(member.id) + ")" + " Logged on line " + str(numLines + 3) + " of error log file...")
		await errorWrite("ERROR IN GUILD: " + str(location) + "(" + str(location.id) + ")" + " TRIGGERED BY USER: " + str(member) + "(" + str(member.id) + ")", exception)
	elif (type(location)is User):
		logWrite(location, "ERROR IN DM: (UID: " + str(location.id) + ") Logged on line " + str(numLines + 3) + " of error log file...")
		await errorWrite("ERROR IN DM WITH USER: " + str(location.id), exception)
	elif (location == None):
		logWrite(None, "ERROR: Logged on line " + str(numLines + 3) + " of error log file...")
		await errorWrite("ERROR: ", exception)
