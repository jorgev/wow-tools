#!/usr/bin/env python
# encoding: utf-8
"""
wowparse.py

Created by Jorge Velazquez on 2009-05-24.
"""

import csv
import re
import sys
from datetime import datetime

damage_fields = ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE', 'SWING_DAMAGE', 'RANGE_DAMAGE']
healing_fields = ['SPELL_HEAL', 'SPELL_PERIODIC_HEAL']
missed_fields = ['SPELL_MISSED', 'SWING_MISSED', 'RANGE_MISSED']
tracked_fields = damage_fields + healing_fields + missed_fields

class Effect:
	def __init__(self, name):
		self.name = name
		self.total_healing = 0
		self.healing = 0
		self.periodic_healing = 0
		self.overheal = 0
		self.total_damage = 0
		self.damage = 0
		self.periodic_damage = 0
		self.hits = 0
		self.ticks = 0
		self.resisted = 0
		self.missed = 0
		self.immune = 0
		self.dodged = 0
		self.parried = 0
		self.blocked = 0
		self.blocked_amount = 0
		self.absorbed = 0
		self.absorbed_amount = 0
		self.reflected = 0
		self.evaded = 0

class Entity:
	def __init__(self, id, name, flags):
		self.id = id
		self.name = name
		self.flags = flags

class Encounter:
	def __init__(self, source, destination):
		self.src = source
		self.dst = destination
		self.start_time = datetime.min
		self.end_time = datetime.min
		self.total_damage = 0
		self.total_healing = 0
		self.total_overhealing = 0
		self.effects = {}
		
	def elapsed_time(self):
		elapsed = self.end_time - self.start_time
		seconds = elapsed.seconds + elapsed.microseconds / 1000000.0
		return seconds if seconds > 0.0 else 1.0
		
class LogInfo:		
	def Parse(self, filename, source_name = None, destination_name = None, ignore_pets = False, ignore_guardians = False):
		# parsing a new file, reset some of the instance variables
		self.encounters = []
		self.total_line_count = 0
		self.parsed_line_count = 0
		entities = {}
		
		# warn if no source or destination, parsing may take a while
		if not source_name and not destination_name:
			print 'No source or destination specified, parsing may take a while and output may be lengthy'

		reader = csv.reader(open(filename))
		for row in reader:
			# bump line counter
			self.total_line_count += 1
	
			# two spaces are used to split the date/time field from the actual combat data
			timestamp, event = row[0].split('  ')
	
			# must be one of the events that we actually track
			if not event in tracked_fields:
				continue

			# if source or destination id is zero, we can't do anything with it
			srcguid = long(row[1], 16)
			dstguid = long(row[5], 16)
			if srcguid == 0 or dstguid == 0:
				continue
				
			# get the flags
			srcflags = int(row[3], 16)
			dstflags = int(row[7], 16)
			if ignore_pets and (srcflags & 0x1000 != 0 or dstflags & 0x1000 != 0):
				continue
			if ignore_guardians and (srcflags & 0x2000 != 0 or dstflags & 0x2000 != 0):
				continue
			
			# get source and destination names
			srcname = row[2]
			dstname = row[6]
			
			# check for filtering on source or destination
			if source_name and source_name != srcname:
				continue
			if destination_name and destination_name != dstname:
				continue
			
			# actual number of lines parsed
			self.parsed_line_count += 1
		
			# get the timestamp (NOTE: year is not supplied in the combat log, this will cause problems if log file crosses a year boundary)
			timestamp = datetime.strptime(timestamp, '%m/%d %H:%M:%S.%f')
		
			# depending on how many fields we have, damage/healing amount could be in two places
			amount = 0
			overheal = 0
			if event in damage_fields:
				if event == 'SWING_DAMAGE':
					amount = int(row[9])
				else:
					amount = int(row[12])
			elif event in healing_fields:
				amount = int(row[12])
				overheal = int(row[13])
				
			# create or get source
			if srcguid in entities:
				source = entities[srcguid]
			else:
				source = Entity(srcguid, srcname, srcflags)
				entities[srcguid] = source
		
			# create or get destination
			if dstguid in entities:
				destination = entities[dstguid]
			else:
				destination = Entity(dstguid, dstname, dstflags)
				entities[dstguid] = destination

			# see if we have a record of this encounter already
			encounter = None
			for enc in self.encounters:
				if enc.src.id == source.id and enc.dst.id == destination.id:
					encounter = enc
					break
					
			# if not, we create a new one
			if not encounter:
				encounter = Encounter(source, destination)
				self.encounters.append(encounter)
				
			# update the stats for total damage and healing for this encounter
			if event in damage_fields:
				encounter.total_damage += amount
			elif event in healing_fields:
				encounter.total_healing += amount
				encounter.total_overhealing += overheal
				
			# update the timestamps, for dps/hps calculation
			if encounter.start_time == datetime.min:
				encounter.start_time = timestamp
			encounter.end_time = timestamp

			# add or get effect
			if event == 'SWING_DAMAGE' or event == 'SWING_MISSED':
				effect_name = 'Swing'
			else:
				effect_name = row[10]
			effects = encounter.effects
			if effects.has_key(effect_name):
				effect = effects[effect_name]
			else:
				effect = Effect(effect_name)
				effects[effect_name] = effect
		
			# update effect stats
			if event in missed_fields:
				amount = 0 # some miss stats have an amount (block, absorb, etc.)
				if event == 'SWING_MISSED':
					miss_reason = row[9]
					if len(row) > 10:
						amount = int(row[10])
				else:
					miss_reason = row[12]
					if len(row) > 13:
						amount = int(row[13])
				if miss_reason == 'MISS':
					effect.missed += 1
				elif miss_reason == 'IMMUNE':
					effect.immune += 1
				elif miss_reason == 'PARRY':
					effect.parried += 1
				elif miss_reason == 'BLOCK':
					effect.blocked += 1
					effect.blocked_amount += amount
				elif miss_reason == 'ABSORB':
					effect.absorbed += 1
					effect.absorbed_amount += amount
				elif miss_reason == 'EVADE':
					effect.evaded += 1
			elif event in damage_fields:
				effect.total_damage += amount
				if event == 'SPELL_PERIODIC_DAMAGE':
					effect.periodic_damage += amount
					effect.ticks += 1
				else:
					effect.damage += amount
					effect.hits += 1
			elif event in healing_fields:
				effect.total_healing += amount
				effect.overheal += overheal
				if event == 'SPELL_PERIODIC_HEAL':
					effect.periodic_healing += amount
					effect.ticks += 1
				else:
					effect.healing += amount
					effect.hits += 1
		
		return self.encounters
