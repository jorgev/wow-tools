#!/usr/bin/env python
# encoding: utf-8
"""
wowparse.py

Created by Jorge Velazquez on 2009-05-24.
"""

import re
from datetime import datetime

damage_fields = ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE', 'SWING_DAMAGE', 'RANGE_DAMAGE']
healing_fields = ['SPELL_HEAL', 'SPELL_PERIODIC_HEAL']
other_fields = ['SPELL_MISSED']
tracked_fields = damage_fields + healing_fields + other_fields

class Effect:
	def __init__(self, name):
		self.name = name
		self.total_healing = 0
		self.total_damage = 0
		self.hits = 0
		self.ticks = 0
		self.resists = 0
		self.misses = 0

class Destination:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.total_damage = 0
		self.total_healing = 0
		self.start_time = datetime.min
		self.end_time = datetime.min
		self.effects = {}

class Source:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.total_damage = 0
		self.total_healing = 0
		self.destinations = {}

class LogInfo:
	def __init__(self):
		self.sources = {}
		self.total_line_count = 0
		self.parsed_line_count = 0
		
	def Parse(self, filename):
		# parsing a new file, reset some of the instance variables
		self.sources = {}
		self.total_line_count = 0
		self.parsed_line_count = 0
		
		# start reading the file
		file = open(filename, 'r')
		while True:
			# read a single line, exit if nothing read
		 	line = file.readline()
			if not line:
				break
				
			# bump line counter
			self.total_line_count += 1
		
			# two spaces are used to split the date/time field from the actual combat data
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
			
			# actual number of lines parsed
			self.parsed_line_count += 1
		
			# strip surrounding double-quots from source and destination names
			srcname = combat_fields[2][1:-1]
			dstname = combat_fields[5][1:-1]
			effect_type = combat_fields[0]
			
			# get the timestamp (NOTE: year is not supplied in the combat log, this will cause problems if log file crosses a year boundary)
			timestamp = datetime.strptime(date_time, '%m/%d %H:%M:%S.%f')
		
			# depending on how many fields we have, damage/healing amount could be in two places
			if len(combat_fields) == 16:
				amount = int(combat_fields[7])
			else:
				amount = int(combat_fields[10])
				
			# add or get source
			if self.sources.has_key(srcguid):
				source = self.sources[srcguid]
			else:
				source = Source(srcguid, srcname)
				self.sources[srcguid] = source
		
			# update the stats for the source
			if effect_type in damage_fields:
				source.total_damage += amount
			elif effect_type in healing_fields:
				source.total_healing += amount
		
			# add or get destination
			destinations = source.destinations
			if destinations.has_key(dstguid):
				destination = destinations[dstguid]
			else:
				destination = Destination(dstguid, dstname)
				destinations[dstguid] = destination
			
			# update the stats for the destination
			if effect_type in damage_fields:
				destination.total_damage += amount
			elif effect_type in healing_fields:
				destination.total_healing += amount
		
			# destination gets the timestamps, for dps/hps calculation
			if destination.start_time == datetime.min:
				destination.start_time = timestamp
			destination.end_time = timestamp
		
			# add or get effect
			if effect_type == 'SWING_DAMAGE':
				effect_name = "Swing"
			else:
				effect_name = combat_fields[8][1:-1]
			effects = destination.effects
			if effects.has_key(effect_name):
				effect = effects[effect_name]
			else:
				effect = Effect(effect_name)
				effects[effect_name] = effect
			
			# update effect stats
			if effect_type == 'SPELL_MISSED':
				effect.misses += 1
			elif effect_type in damage_fields:
				effect.total_damage += amount
				if effect_type == 'SPELL_PERIODIC_DAMAGE':
					effect.ticks += 1
				else:
					effect.hits += 1
			elif effect_type in healing_fields:
				effect.total_healing += amount
				if effect_type == 'SPELL_PERIODIC_HEAL':
					effect.ticks += 1
				else:
					effect.hits += 1
