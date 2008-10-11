import re, time
import lampstand.reactions.base

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	
	__name = 'Generic'
	
	cooldown_number = 2
	cooldown_time   = 360
	uses = []

	def __init__(self, connection):

		self.reactions = (('.*pokes %s', '', "Do I look like a facebook user? Fuck off."),
			('%s. What is best in life?', 'Not Telling', "To crush your enemies, see them driven before you, and to hear the lamentations of their women!"),
			('%s. Open the pod bay doors', "I think you have your AIs confused.", "I can't do that, Dave")
			)

		self.channelMatch = []

		for reaction in self.reactions:
			self.channelMatch.append(re.compile(reaction[0] % connection.nickname, re.IGNORECASE))

	def channelAction(self, connection, user, channel, message, matchindex):
		print "[Generic Reaction] called"


		if self.overUsed(self.uses, self.cooldown_number, self.cooldown_time):
			if self.reactions[matchindex][1] != '':
				connection.msg(channel, self.reactions[matchindex][1])
				return


		## Overuse Detectection ##
		self.uses.append(int(time.time()))
		if len(self.uses) > self.cooldown_number:
			self.uses = self.uses[0:self.cooldown_number-1]
		## Overuse Detectection ##

		if self.reactions[matchindex][2] != '':
			connection.msg(channel, self.reactions[matchindex][2])
			return
