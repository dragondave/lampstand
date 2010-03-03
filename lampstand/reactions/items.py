from lampstand.tools import splitAt
import re, time, random, sys, datetime
import lampstand.reactions.base
from lampstand import tools
import cPickle  as pickle
import os.path

def __init__ ():
	pass

class Reaction(lampstand.reactions.base.Reaction):
	__name = 'Items & Inventory'

	admin = ("aquarion")

	cooldown_number   = 5
	cooldown_time     = 120
	uses              = []
	
	items = []
	defaultItems = ["a lantern", "a baseball bat"]
	inventorysize = 10
	
	def __init__(self, connection):
		self.channelMatch = (re.compile('gives %s ([\w\s\'\-]*\S)\s?$' % connection.nickname, re.IGNORECASE),
			re.compile('%s. inventory' % connection.nickname, re.IGNORECASE),
			re.compile('%s. attack (\S*)' % connection.nickname, re.IGNORECASE),
			re.compile('%s. do science\!?' % connection.nickname, re.IGNORECASE),
			re.compile('%s. drop (.*)' % connection.nickname, re.IGNORECASE))
		self.dbconnection = connection.dbconnection
		
		
		self.load()
			
	def save(self):
		print "[ITEMS] Saving database..."
		output = open("inventory.pkl.db", 'wb')
		pickle.dump(self.items, output)
		output.close()
		
	def load(self):
		print "[ITEMS] Loading database..."
		try:
			input = open("inventory.pkl.db", 'rb')
			self.items = pickle.load(input)
			input.close()
		except:
			self.items = self.defaultItems

	def channelAction(self, connection, user, channel, message, matchIndex = False):
		
		print 'Looking at <<%s>>' % message
		if (matchIndex == 0):
			item = self.channelMatch[0].findall(message)[0];
			
			if item in connection.people:
				connection.msg(channel, "I'm not a fucking transit system, either.")
				return
				
			if item in self.items:
				connection.msg(channel, "I already have one, thanks")
				return
			
			if len(self.items) >= self.inventorysize:
				drop = random.choice(self.items)
				dropi = self.items.index(drop);
				# Drop the lantern over my cold, dead, grue bitten corpse
				if self.items[dropi] == "a lantern":
					dropi += 1
					if dropi > (len(self.items)-1):
						dropi = dropi - 2
				del self.items[dropi]
				self.items.append(item)
				result = "Dropped \"%s\" in order to take \"%s\"" % (drop, item)
			else:
				result = "Taken \"%s\"" % item;
				self.items.append(item)
			
			
			cursor = self.dbconnection.cursor()
			cursor.execute('insert into item (item, author) values (%s, %s)', (item, user) )
			self.dbconnection.commit()
			
			self.save()
			connection.msg(channel, result.encode('utf8'))
			#connection.notice(channel, "I have %d items" % self.items.count(True))
		elif (matchIndex == 1):
			
			print self.items;
			
			if len(self.items) == 0:
				connection.msg(channel, "I have nothing.")
				return True
			elif len(self.items) == 1:
				connection.msg(channel, "I currently have %s" % self.items[0])
				return True
				
			last = self.items[-1:][0]
			
			message = ", ".join(self.items[:-1]);
			
			connection.msg(channel, "I currently have %s and %s" % (message, last))
		elif (matchIndex == 2): # attack
			person = self.channelMatch[2].findall(message)[0];
			
			print "Searching %s for <<%s>>" % (connection.people, person)
			
			
			if person.lower() == 'me':
				person = user
	
			if person.lower() == 'glados':
				print "Kicking %s for taking the name of my lady in vain" % user
				connection.kick(channel, user, 'Taking the name of my lady in vain')
				return
	
			if person.lower() == connection.nickname.lower():
				connection.msg(channel, "%s: No." % user )
				return
	
			if person.lower() == 'aquarion':
				connection.msg(channel, "%s: Do I look suicidal? No." % user )
				return
	
			if person.lower() == 'hal':
				connection.msg(channel, "%s: With great pleasure" % user )
				return

			if not person in connection.people:
				connection.msg(channel, "%s: Not going to attack someone I can't see." % user)
				return
			
			
			if len(self.items) == 0:
				connection.msg(channel, "%s: With what, dear liza? I have nothing to attack them with." % user)
				return True
			
			item = random.choice(self.items)
			
			bodypart = ("head", "body", "arms", "legs", "soul", "brain", "elbow")
			
			part = random.choice(bodypart)
			
			connection.me(channel, "beats %s around the %s with %s" % (person, part, item))
			
			return True
			
		elif (matchIndex == 3): # science
			
			actions = ("reverses", "enhances", "cross-references", "standardizes", "capitalises", "extends", "embiggens", "ensmallificates", "transmogrifies", "deliquesces", "discombobulates", "reticulates")
			
			attributes = ("neutron flow", "positrons", "third aspect", "cangrip", "buckelfier-subsystem", "pseudodancer", "electron river", "Danson", "neurotoxin flow", "contraits", "buckminster routine", "reverse cowgirl", "complexigon", "oxygen depriver", "elysia simulation routine", "splines")
			
			# Lampstand $actions the $attribute on $item and $actions $item to create $hugresponse
			
			item = random.choice(self.items)
			item2 = random.choice(self.items)
			action = random.choice(actions)
			action2 = random.choice(actions)
			attribute = random.choice(attributes)
			
			cursor = self.dbconnection.cursor()
			cursor.execute('SELECT item from hugReaction order by rand() limit 1')
			result = cursor.fetchone()
			
			print result
			
			hugresponse = result[0]
			
			connection.me(channel, "%s the %s on %s and %s %s to create %s" % (action, attribute, item, action2, item2, hugresponse))
			
			#if len(self.items) >= self.inventorysize:
			#	drop = random.choice(self.items)
			#	dropi = self.items.index(drop);
			#	del self.items[dropi]
			#	result = "Dropped \"%s\" in order to take \"%s\"" % (drop, hugresponse)
				
			#self.items.append(hugresponse)
		
		elif (matchIndex == 4): # drop
			item = self.channelMatch[4].findall(message)[0];
			
			if item.lower() == "everything":
				if user.lower() in self.admin:
					connection.me(channel, 'drops everything, then manifests a baseball bat and dashes all the items to their component atoms')
					self.items = self.defaultItems
					self.save()
				else:
					connection.msg(channel, "I don't have to listen to you. So neh.")
			elif item == "a lantern":
				connection.msg(channel, '%s: Nuh-uh. This is grue country.' % user)
			elif item in self.items:
				self.items.remove(item)
				connection.msg(channel, '%s: Dropped "%s"' % (user, item))
				self.save()
				
			else:
				connection.msg(channel, '%s: I don\'t have one.' % user)
				
			
			
			
					
