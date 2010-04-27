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
other_fields = ['SPELL_MISSED']
tracked_fields = damage_fields + healing_fields + other_fields

PET_MASK = 0x00001000
GUARDIAN_MASK = 0x00002000

class Effect:
	def __init__(self, name):
		self.name = name
		self.healing = 0
		self.periodic_healing = 0
		self.damage = 0
		self.periodic_damage = 0
		self.hits = 0
		self.ticks = 0
		self.resists = 0
		self.misses = 0
		self.crits = 0
		self.periodic_crits = 0
		self.blocked = 0
		self.parried = 0
		self.absorbed = 0

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

		# depending on how many fields we have, damage/healing amount could be in two places
		num_fields = len(combat_fields)
		if num_fields == 16:
			amount = int(combat_fields[7])
		elif num_fields == 19:
			amount = int(combat_fields[10])
		else:
			amount = 0 # other type of field

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
		if effect_type == 'SWING_DAMAGE':
			effect_name = "Swing"
		else:
			effect_name = combat_fields[8][1:-1]
		if effect_name in destination.effects:
			effect = destination.effects[effect_name]
		else:
			effect = Effect(effect_name)
			destination.effects[effect_name] = effect

		# update effect stats
		if effect_type == 'SPELL_MISSED':
			effect.misses += 1
		elif effect_type in damage_fields:
			if effect_type == 'SPELL_PERIODIC_DAMAGE':
				effect.periodic_damage += amount
				effect.ticks += 1
			else:
				effect.damage += amount
				effect.hits += 1
		elif effect_type in healing_fields:
			if effect_type == 'SPELL_PERIODIC_HEAL':
				effect.periodic_healing += amount
				effect.ticks += 1
			else:
				effect.healing += amount
				effect.hits += 1
					
	# we're done parsing, generate some html and save it to the database
	html = ''
	for source in sources.values():
		html += '<div class="src">%s - ' % source.name
		arr = []
		timediff = source.end_time - source.start_time
		total_seconds = max(timediff.seconds + float(timediff.microseconds) / 1000000, 1.0)
		if source.damage:
			dps = float(source.damage) / total_seconds
			arr.append('%d damage (%0.1f DPS)' % (source.damage, dps))
		if source.healing:
			hps = float(source.healing) / total_seconds
			arr.append('%d healing (%0.1f HPS)' % (source.healing, hps))
		html += ', '.join(arr)
		html += '</div>\n'
		for destination in source.destinations.values():
			html += '<div class="dst">%s - ' % destination.name
			arr = []
			timediff = destination.end_time - destination.start_time
			total_seconds = max(timediff.seconds + float(timediff.microseconds) / 1000000, 1.0)
			if destination.damage:
				arr.append('%d damage' % destination.damage)
			if destination.healing:
				arr.append('%d healing' % destination.healing)
			html += ', '.join(arr)
			html += '</div>\n'
			for effect in destination.effects.keys():
				html += '<div class="effect">%s - ' % effect
				arr = []
				val = destination.effects[effect]
				if val.damage:
					html += '%d damage, %d hits (%0.1f avg)' % (val.damage, val.hits, float(val.damage) / val.hits)
				if val.periodic_damage:
					html += '%d periodic damage, %d ticks (%0.1f avg)' % (val.periodic_damage, val.hits, float(val.periodic_damage) / val.hits)
				if val.healing:
					html += '%d healing' % val.healing
				html += ', '.join(arr)
				html += '</div>\n'

	# create the raid object
	raid = Event(user=user, name=event_name, html=html)
	raid.save()

	return html

