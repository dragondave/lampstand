import re, time, random, sys, urllib, os, datetime
import lampstand.reactions.base

from xml.dom.minidom import parse, parseString

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Steam Play'

	cooldown_number   = 5
	cooldown_time     = 120
	uses              = []

	def __init__(self, connection):

		self.channelMatch = (
			re.compile('%s: what should I play\?' % connection.nickname, re.IGNORECASE),
			re.compile('%s: my steam profile is (\S*)' % connection.nickname, re.IGNORECASE))

		self.privateMatch = (
			re.compile('what should I play\?', re.IGNORECASE),
			re.compile('my steam profile is (\S*)', re.IGNORECASE))

		self.dbconnection = connection.dbconnection
	
	
	def channelAction(self, connection, user, channel, message, matchIndex = False):

		if self.overUsed(self.uses):
				connection.msg(channel, self.overuseReactions[matchIndex])
				return True


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
				self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		if matchIndex == 0:
			output = self.playWhat(user)
		elif matchIndex == 1:
			result = self.channelMatch[matchIndex].findall(message)
			output = self.setSteam(user, result)

		output = "%s: %s" % (user, output)

		connection.msg(channel, output.encode("utf-8"))


	def privateAction(self, connection, user, channel, message, matchIndex = False):

		if matchIndex == 0:
			connection.msg(user, self.playWhat(user).encode("utf-8"))
		elif matchIndex == 1:
			result = self.privateMatch[matchIndex].findall(message)
			connection.msg(user, self.setSteam(user, result).encode("utf-8"))


	def playWhat(self, username):

		cursor = self.dbconnection.cursor()
		cursor.execute('SELECT steamname from gameaccounts where username = %s', username)
		result = cursor.fetchone()

		if result == None:
			return self.helptext()

		steam = self.getSteamXML(result[0])
		
		print steam

		if hasattr(steam, '__getitem__'):
			return steam[1]

		return self.pickAGame(steam)

	def helptext(self):

		return """I don't have a steam account for you, sorry. Set this by saying "my steam profile is [SOMETHING]" to me. To find what '[SOMETHING]' should be log in to steamcommunity.com and it's the word after "/id/" or the numbers after "/profile/" in the URL of your home page."""

	
	def setSteam(self, username, result):
		
		steamname = result[0]

		steam = self.getSteamXML(steamname)
		
		if hasattr(steam, '__getitem__'):
			return steam[1]

		nameElement = steam.getElementsByTagName('steamID')[0]
		accountName = nameElement.childNodes[0].data

		cursor = self.dbconnection.cursor()
		cursor.execute('REPLACE into gameaccounts (username, steamname) values (%s, %s)', (username, steamname) )
		self.dbconnection.commit()
		
		return "Okay, remembering that %s's steam name is %s, aka '%s'" % (username,steamname, accountName)

		return "Stub %s" % result



	def pickAGame(self, steam):
		
		if random.randint(0,100) == 25:
			return "Odyssey, obviously".
		

		if random.randint(0,2) == 1:
			games = steam.getElementsByTagName('game')
			game = random.choice(games)
		else:
			games = steam.getElementsByTagName('hoursLast2Weeks')
			game = random.choice(games).parentNode
			

		gamename = game.getElementsByTagName('name')[0].childNodes[0].data

		return gamename

	def getSteamXML(self, username):

		username = username.lower()

		try:
			i = int(username)
		except ValueError, TypeError:
			profiletype = 'id'
		else:
			profiletype = 'profiles'
		
		steamurl = "http://steamcommunity.com/%s/%s/games?tab=all&xml=1" % (profiletype, username)

		print steamurl

		cachename = "/tmp/steam.lampstand.%s.xml" % username;

		(fileopen, fileheaders) = urllib.urlretrieve(steamurl, cachename)

		stat = os.stat(fileopen)
		delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(stat.st_mtime)
		if delta.seconds > 60*60*12:
			os.remove(fileopen)
			(fileopen, fileheaders) = urllib.urlretrieve(steamurl, cachename)

		try:
			steam = parse(fileopen)
		except ParseError:
			return (16, "Error getting the response from steam")
		except:
			return (128, "Something crazy happened: <%s>" % sys.exc_info()[0])


		steamerror = steam.getElementsByTagName('error')
		if len(steamerror) > 0:
			return (32, "Sorry, Steam said: %s" % steamerror[0].childNodes[0].data)

		return steam