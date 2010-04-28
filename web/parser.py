#!/usr/bin/env python
# encoding: utf-8
"""
parser.py

Created by Jorge Velázquez on 2010-04-24.
"""

import datetime
from web.models import Event

damage_fields = ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE', 'SWING_DAMAGE', 'RANGE_DAMAGE']
healing_fields = ['SPELL_HEAL', 'SPELL_PERIODIC_HEAL']
miss_fields = ['SPELL_MISSED', 'SWING_MISSED', 'RANGE_MISSED']
tracked_fields = damage_fields + healing_fields + miss_fields

PET_MASK = 0x00001000
GUARDIAN_MASK = 0x00002000

class Effect:
	def __init__(self, name):
		self.name = name
		self.healing = 0
		self.periodic_healing = 0
		self.overhealing = 0
		self.damage = 0
		self.periodic_damage = 0
		self.hits = 0
		self.crits = 0
		self.ticks = 0
		self.periodic_crits = 0
		self.resisted = 0
		self.resisted_amount = 0
		self.missed = 0
		self.crits = 0
		self.periodic_crits = 0
		self.blocked = 0
		self.blocked_amount = 0
		self.dodged = 0
		self.parried = 0
		self.immune = 0
		self.absorbed = 0
		self.absorbed_amount = 0
		self.reflected = 0

class Destination:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.damage = 0
		self.healing = 0
		self.start_time = None
		self.end_time = None
		self.effects = {}

class Source:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.damage = 0
		self.healing = 0
		self.start_time = None
		self.end_time = None
		self.destinations = {}

def parse_data(user, event_name, ignore_pets, ignore_guardians, file):
	# hashes for calculating stats
	sources = {}

	# start our read loop
	while True:
		line = file.readline()
		if not line:
			break;

		# two spaces are used to split the date/time field from the actual combat data
		line = line.strip()
		major_fields = line.split('  ')
		if len(major_fields) < 2:
			continue

		# save off the date/time info, we convert later but only if we need to (i.e., we have a log entry that we are interested in)
		date_time = major_fields[0]

		# here we provide our own line parser, since we have fields which may contain separators and are wrapped in quotes
		combat_fields = major_fields[1].split(',')

		# must be one of the events that we actually track
		if not combat_fields[0] in tracked_fields:
			continue

		# if source or destination id is zero, we can't do anything with it
		srcguid = int(combat_fields[1], 16)
		dstguid = int(combat_fields[4], 16)
		if srcguid == 0 or dstguid == 0:
			continue

		# get flags and check for user-specified filters
		srcflags = int(combat_fields[3], 16)
		dstflags = int(combat_fields[6], 16)
		if ignore_pets and ((srcflags & PET_MASK) or (dstflags & PET_MASK)):
			continue
		if ignore_guardians and ((srcflags & GUARDIAN_MASK) or (dstflags & GUARDIAN_MASK)):
			continue

		# strip surrounding double-quots from source and destination names
		srcname = combat_fields[2][1:-1]
		dstname = combat_fields[5][1:-1]
		effect_type = combat_fields[0]

		# get the timestamp (NOTE: year is not supplied in the combat log, this will cause problems if log file crosses a year boundary)
		timestamp = datetime.datetime.strptime(date_time, '%m/%d %H:%M:%S.%f')

		# depending on how many fields we have, combat data could be in different places
		num_fields = len(combat_fields)
		crit = False
		overheal = 0
		if num_fields == 16: # this is a swing damage entry
			amount = int(combat_fields[7])
			if combat_fields[13] == '1':
				crit = True
		elif num_fields == 19: # this is spell damage
			amount = int(combat_fields[10])
			if combat_fields[16] == '1':
				crit = True
		elif num_fields == 14: # this is spell healing
			amount = int(combat_fields[10])
			overheal = int(combat_fields[11])
			if combat_fields[13] == '1':
				crit = True
		else:
			amount = 0 # other type of field

		# special case
		if effect_type == 'SWING_DAMAGE' or effect_type == 'SWING_MISSED':
			effect_name = 'Swing'
		else:
			effect_name = combat_fields[8][1:-1]

		# add or get source
		if srcguid in sources:
			source = sources[srcguid]
		else:
			source = Source(srcguid, srcname)
			sources[srcguid] = source

		# update stats for the source
		if effect_type in damage_fields:
			source.damage += amount
		elif effect_type in healing_fields:
			source.healing += amount

		# timestamps, for dps/hps calculation
		if not source.start_time:
			source.start_time = timestamp
		source.end_time = timestamp

		# add or get destination
		if dstguid in source.destinations:
			destination = source.destinations[dstguid]
		else:
			destination = Destination(dstguid, dstname)
			source.destinations[dstguid] = destination

		# update the stats for the destination
		if effect_type in damage_fields:
			destination.damage += amount
		elif effect_type in healing_fields:
			destination.healing += amount

		# timestamps, for dps/hps calculation
		if not destination.start_time:
			destination.start_time = timestamp
		destination.end_time = timestamp

		# add or get effect
		if effect_name in destination.effects:
			effect = destination.effects[effect_name]
		else:
			effect = Effect(effect_name)
			destination.effects[effect_name] = effect

		# update effect stats
		if effect_type in miss_fields:

			# if this is a miss, there are various types of misses and, depending
			# on the miss type, the reason and amount can be in two places
			miss_amount = 0
			if effect_type == 'SWING_MISSED':
				miss_reason = combat_fields[7]
				if num_fields > 8:
					miss_amount = int(combat_fields[8])
			else:
				miss_reason = combat_fields[10]
				if num_fields > 11:
					miss_amount = int(combat_fields[11])

			# now that we know the miss type and amount, add it to the effect stats
			if miss_reason == 'ABSORB':
				effect.absorbed += 1
				effect.absorbed_amount += miss_amount
			elif miss_reason == 'RESIST':
				effect.resisted += 1
				effect.resisted_amount += miss_amount
			elif miss_reason == 'BLOCK':
				effect.blocked += 1
				effect.blocked_amount += miss_amount
			elif miss_reason == 'DODGE':
				effect.dodged += 1
			elif miss_reason == 'PARRY':
				effect.parried += 1
			elif miss_reason == 'IMMUNE':
				effect.immune += 1
			elif miss_reason == 'MISS':
				effect.missed += 1

		# or maybe we're dealing with some type of damage field
		elif effect_type in damage_fields:
			if effect_type == 'SPELL_PERIODIC_DAMAGE':
				effect.periodic_damage += amount
				effect.ticks += 1
				if crit:
					effect.periodic_crits += 1
			else:
				effect.damage += amount
				effect.hits += 1
				if crit:
					effect.crits += 1

		# or could be a healing field
		elif effect_type in healing_fields:
			if effect_type == 'SPELL_PERIODIC_HEAL':
				effect.periodic_healing += amount
				effect.ticks += 1
				if crit:
					effect.periodic_crits += 1
			else:
				effect.healing += amount
				effect.hits += 1
				if crit:
					effect.crits += 1
			effect.overhealing += overheal
					
	# we're done parsing, generate some html and save it to the database
	html = ''
	for source in sources.values():
		html += '<div class="src">%s' % source.name
		timediff = source.end_time - source.start_time
		total_seconds = max(timediff.seconds + float(timediff.microseconds) / 1000000, 1.0)
		if source.damage:
			dps = float(source.damage) / total_seconds
			html += ', %d damage (%0.1f DPS)' % (source.damage, dps)
		if source.healing:
			hps = float(source.healing) / total_seconds
			html += ', %d healing (%0.1f HPS)' % (source.healing, hps)
		html += '</div>\n'
		for destination in source.destinations.values():
			html += '<div class="dst">%s' % destination.name
			timediff = destination.end_time - destination.start_time
			total_seconds = max(timediff.seconds + float(timediff.microseconds) / 1000000, 1.0)
			if destination.damage:
				dps = float(destination.damage) / total_seconds
				html += ', %d damage (%0.1f DPS)' % (destination.damage, dps)
			if destination.healing:
				hps = float(destination.healing) / total_seconds
				html += ', %d healing (%0.1f HPS)' % (destination.healing, hps)
			html += '</div>\n'
			for effect in destination.effects.keys():
				val = destination.effects[effect]
				if val.damage or val.periodic_damage:
					html += '<div class="effect damage">%s' % effect
				elif val.healing or val.periodic_healing:
					html += '<div class="effect healing">%s' % effect
				else:
					html += '<div class="effect">%s' % effect
				if val.damage:
					html += ', %d damage (%d hit(s)' % (val.damage, val.hits)
					if val.crits:
						html += ', %d crit(s)' % val.crits
					html += ' - %0.1f avg)' %  (float(val.damage) / val.hits)
				if val.periodic_damage:
					html += ', %d periodic damage (%d ticks' % (val.periodic_damage, val.ticks)
					if val.periodic_crits:
						html += ', %d crit(s)' % val.periodic_crits
					html += ' - %0.1f avg)' % (float(val.periodic_damage) / val.ticks)
				if val.healing:
					html += ', %d healing (%d hits(s)' % (val.healing, val.hits)
					if val.crits:
						html += ', %d crit(s)' % val.crits
					html += ' - %0.1f avg)' % (float(val.healing) / val.hits)
				if val.periodic_healing:
					html += ', %d periodic healing (%d ticks' % (val.periodic_healing, val.ticks)
					if val.periodic_crits:
						html += ', %d crit(s)' % val.periodic_crits
					html += ' - %0.1f avg)' % (float(val.periodic_healing) / val.ticks)
				if val.overhealing:
					html += ', %d overhealing (%0.1f %%)' % (val.overhealing, val.overhealing * 100.0 / (val.healing + val.periodic_healing))
				if val.absorbed:
					html += ', %d absorbed (%d amount)' % (val.absorbed, val.absorbed_amount)
				if val.blocked:
					html += ', %d blocked (%d amount)' % (val.blocked, val.blocked_amount)
				if val.resisted:
					html += ', %d resisted' % val.resisted
				if val.missed:
					html += ', %d missed' % val.missed
				if val.dodged:
					html += ', %d dodged' % val.dodged
				if val.parried:
					html += ', %d parried' % val.parried
				if val.immune:
					html += ', %d immune' % val.immune
				if val.reflected:
					html += ', %d reflected' % val.reflected
				html += '</div>\n'

	# create the raid object
	raid = Event(user=user, name=event_name, html=html)
	raid.save()

	return raid.id

