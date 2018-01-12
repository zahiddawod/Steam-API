# The purpose of this software is to retrieve public information from a steam account.
import urllib.request
import json
import sys
import os, platform
import datetime
from enum import Enum

key = '' # API key to access data
format = "json" # Format in which data will be interpreted
steamID = '' # Steam account that data will be retrieve from

# Enums for different api urls
class ApiLink(Enum):
	PLAYERDATA = 1
	FRIENDS = 2
	ACHIEVEMENTS = 3
	GAMES = 4
	BANS = 5

# Default game app id (Team Fortress 2)
appid = 440

# Variables to store list of player owned game data
appids = []
playTime = []
ownedGames = []

# Variable to store list of friends
friendNames = []

# Clear command to use to clear the console (dependant on OS)
clear = 'clear'

def main():
	global clear
	if (platform.system() == 'Windows'): # Check if user is running program on windows OS
		clear = 'cls'
	os.system(clear)
	
	changeAPIKey()
	changeSteamID()
	
	data = openURL(ApiLink.PLAYERDATA, steamID)
	
	menuOptions = ["(1) Change STEAM ID",
				"(2) Online status",
				"(3) Profile link",
				"(4) Avatar link",
				"(5) Game currently being played",
				"(6) List of friends",
				"(7) List of games",
				"(8) Player bans",
				"(9) Refresh player data",
				"(0) Quit Program"]
	
	option = '-1'
	while (option != '0'):
		os.system(clear)
		
		if (option == '1'):
			changeSteamID()
			data = openURL(ApiLink.PLAYERDATA, steamID)
			resetData()
			os.system(clear)
		elif (option == '2'):
			print("Player status is: " + getPlayerStatus(data) + "\n")
		elif (option == '3'):
			print(getProfileURL(data) + "\n")
		elif (option == '4'):
			print(getAvatarLink(data) + "\n")
		elif (option == '5'):
			print(getCurrentGame(data) + "\n")
		elif (option == '6'):
			getFriendsList()
		elif (option == '7'):
			getOwnedGames()
		elif (option == '8'):
			getPlayerBans()
		elif (option == '9'):
			data = openURL(ApiLink.PLAYERDATA, steamID)
			resetData()
		
		print("Display Name: " + getDisplayName(data))
		print("Real Name: " + getRealName(data))
		getCountryInfo(data)
		print("Account created in: " + getTimeFromUnix(data["response"]["players"][0]["timecreated"]))
		print("The visibility state of this profile is: " + getCommunityVisibilityState(data) + "\n")
		option = menu(menuOptions)
	os.system(clear)
	sys.exit()

def menu(menuOptions):
	print("STEAM ID: " + steamID + "\nAPI KEY: " + key)
	for i in range(len(menuOptions)):
		print(menuOptions[i])
	return input()

def resetData():
	global ownedGames, appids, playTime, friendNames
	ownedGames.clear()
	appids.clear()
	playTime.clear()
	friendNames.clear()

def changeSteamID():
	global steamID
	steamID = ''
	while (steamID == ''):
		steamID = str(input("Please enter the user's STEAMID64 (Enter '?' for help): "))
		if (steamID == '?'):
			print("If you don't know it try searching up the person's username on here: https://steamidfinder.com/\nExample: 76561197960287930\n")
			steamID = ''

def changeAPIKey():
	global key
	key = ''
	while (key == ''):
		key = str(input("Please enter a steam API key (Enter '?' for help): "))
		if (key == '?'):
			print("For this program to work you need an API key from steam.\nIf you don't have one, you can get it from here: http://steamcommunity.com/dev/apikey\n")
			key = ''

def openURL(link, id):
	req_headers = {'User-Agent': 'Python script'}
	if (link == ApiLink.PLAYERDATA):
		url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + key + "&format=" + format + "&steamids=" + id
	elif (link == ApiLink.FRIENDS):
		url = "http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key=" + key + "&format=" + format + "&steamid=" + id + "&relationship=friend"
	elif (link == ApiLink.ACHIEVEMENTS):
		url = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=" + str(appid) + "&key=" + key + "&format=" + format + "&steamid=" + id
	elif (link == ApiLink.GAMES):
		url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" + key + "&steamid=" + id + "&format=" + format
	elif (link == ApiLink.BANS):
		url = "http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key=" + key + "&steamids=" + id + "&format=" + format
	req = urllib.request.Request(url, data=None, headers=req_headers, origin_req_host=None)

	try:
		response = urllib.request.urlopen(req)
	except urllib.error.HTTPError as f: # checks for http forbidden request (invalid api key)
		if(f.code == 400): # http error 400: bad request
			return 'NULL'
		print("'" + key + "' is not a valid API Key!")
		changeAPIKey()
		return openURL(link, id)
		
	content = response.read()
	data = json.loads(content.decode('utf8'))
	
	if (link == ApiLink.PLAYERDATA):
		if (len(data["response"]["players"]) == 0):
			print("SteamID '" + id + "' does not exist!")
			changeSteamID()
			id = steamID
			return openURL(link, id)
	elif (link == ApiLink.ACHIEVEMENTS):
		if (data["playerstats"]["success"] == "false"):
			print("SteamID '" + id + "' does not exist!")
			changeSteamID()
			id = steamID
			return openURL(link, id)
	elif (link == ApiLink.BANS):
		if (len(data["players"]) == 0):
			print("SteamID '" + id + "' does not exist!")
			changeSteamID()
			id = steamID
			return openURL(link, id)
	return data
	

#RETURN VALUE MEANINGS: 0 = offline, 1 = online, 2 = busy, 3 = away, 4 = snooze, 5 = looking to trade, 6 looking to play
def getPlayerStatus(data):
	print("NOTE: Program will not be able to tell apart from users who are hidden or actually offline.")
	print("NOTE: Player's who have their profile as private will always show status as offline")
	
	state = ["OFFLINE", "ONLINE", "BUSY", "AWAY", "SNOOZE", "LOOKING TO TRADE", "LOOKING TO PLAY"]
	status = "ERROR: Unknown persona state"
	
	for i in range(len(state)):
		if (data["response"]["players"][0]["personastate"] == i):
			status = state[i]
	return status

def getDisplayName(data):
	return data["response"]["players"][0]["personaname"]

def getRealName(data):
	for i in data["response"]["players"]:
		if ("realname" not in i):
			return "UNKNOWN"
	return data["response"]["players"][0]["realname"]

def getCountryInfo(data):
	countryCode = "N/A"
	stateCode = "N/A"
	for i in data["response"]["players"]:
		if ("loccountrycode" in i):
			countryCode = data["response"]["players"][0]["loccountrycode"]
		if ("locstatecode" in i):
			stateCode = data["response"]["players"][0]["locstatecode"]
	print("Location: " + countryCode + ", " + stateCode)

def getProfileURL(data):
	return data["response"]["players"][0]["profileurl"]

def getAvatarLink(data):
	return data["response"]["players"][0]["avatarfull"]

def getCommunityVisibilityState(data):
	if (data["response"]["players"][0]["communityvisibilitystate"] == 1):
		return "PRIVATE/FRIENDS ONLY"
	elif (data["response"]["players"][0]["communityvisibilitystate"] == 3):
		return "PUBLIC"
	return "UNKNOWN"

def getCurrentGame(data):
	for i in data["response"]["players"]:
		if ("gameid" not in i):
			return "This user is currently not playing any games"
	global appid
	appid = data["response"]["players"][0]["gameid"]
	currentGame = openURL(ApiLink.ACHIEVEMENTS, steamID)
	return "This user is currently playing: " + currentGame["playerstats"]["gameName"]

def getFriendsList():
	data = openURL(ApiLink.FRIENDS, steamID)
	friendID = steamID
	friendNum = 0
	
	if (len(friendNames) == 0):
		for friends in data["friendslist"]["friends"]:
			os.system(clear)
			print("Loading in list of friends (" + str(friendNum + 1) + "/" + str(len(data["friendslist"]["friends"])) + ")..")
			print("This will only take a moment the first time it's executed and when player data is refreshed.\n")
			friendID = friends["steamid"]
			friendData = openURL(ApiLink.PLAYERDATA, friendID)
			friendNames.append(getDisplayName(friendData))
			friendNum += 1
		friendNum = 0
	
	for friends in data["friendslist"]["friends"]:
		friendNum += 1
		print("SteamID: " + friendID)
		print("Friend: " + str(friendNum))
		print("Display Name: " + friendNames[friendNum-1])
		print("Friends Since: " + getTimeFromUnix(friends["friend_since"]) + "\n")
	print("")

def getOwnedGames():
	global appid
	data = openURL(ApiLink.GAMES, steamID)
	
	if (len(ownedGames) == 0): # Checks if data of games was already loaded in
		i = 0
		numOfGames = str(data["response"]["game_count"])
		for games in data["response"]["games"]:
			os.system(clear)
			print("Loading in list of games (" + str(i + 1) + "/" + numOfGames + ")..")
			print("This will only take a moment the first time it's executed and when player data is refreshed.\n")
			appid = data["response"]["games"][i]["appid"]
			currentGame = openURL(ApiLink.ACHIEVEMENTS, steamID)
			if (currentGame == 'NULL'): # Requested app (game) has no stats
				i += 1 # So move on to next game
				continue
			appids.append(str(appid))
			ownedGames.append(currentGame["playerstats"]["gameName"])
			playTime.append(str(data["response"]["games"][i]["playtime_forever"]/60))
			i += 1
	
	for j in range(len(appids)):
		print("App ID: " + appids[j])
		print("Game: " + ownedGames[j])
		print("Playtime: " + playTime[j] + " hours\n")
	print("")

def getPlayerBans():
	data = openURL(ApiLink.BANS, steamID)
	info = ["SteamID", "Community Banned", "VAC Banned", "Number Of VAC Bans", "Days Since Last Ban", "Number of Game Bans", "Economy Ban"]
	
	i = 0
	for entry in data["players"][0]:
		print(info[i] + ": " + str(data["players"][0][entry]))
		i += 1
	
	print("")

def getTimeFromUnix(unixValue):
	return datetime.datetime.utcfromtimestamp(int(unixValue)).strftime('%Y-%m-%d')

if __name__ == "__main__":
	main()