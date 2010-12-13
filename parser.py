#!/usr/bin/env python
# encoding: utf-8
"""
wowparse.py

Created by Jorge Velazquez on 2009-05-24.
"""

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
	def __init__(self, id, name):
		self.id = id
		self.name = name

class Encounter:
	def __init__(self, source, destination):
		self.src = source
		self.dst = destination
		self.start_time = datetime.min
		self.end_time = datetime.min
		self.total_damage = 0
		self.total_healing = 0
		self.effects = {}
		
	def elapsed_time(self):
		elapsed = self.end_time - self.start_time
		seconds = elapsed.seconds + elapsed.microseconds / 1000000.0
		return seconds if seconds > 0.0 else 1.0
		
class LogInfo:		
	def Parse(self, filename, source_name = None, destination_name = None):
		# parsing a new file, reset some of the instance variables
		self.entities = {}
		self.encounters = []
		self.total_line_count = 0
		self.parsed_line_count = 0
		
		for line in (x.strip() for x in open(filename)):
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
			
			# strip surrounding double-quots from source and destination names
			srcname = combat_fields[2][1:-1]
			dstname = combat_fields[5][1:-1]
			effect_type = combat_fields[0]
			
			# check for filtering on source or destination
			if source_name and source_name != srcname:
				continue
			if destination_name and destination_name != dstname:
				continue

			# actual number of lines parsed
			self.parsed_line_count += 1
		
			# get the timestamp (NOTE: year is not supplied in the combat log, this will cause problems if log file crosses a year boundary)
			timestamp = datetime.strptime(date_time, '%m/%d %H:%M:%S.%f')
		
			# depending on how many fields we have, damage/healing amount could be in two places
			action = combat_fields[0]
			amount = 0
			if action in damage_fields:
				if action == 'SWING_DAMAGE':
					amount = int(combat_fields[7])
				else:
					amount = int(combat_fields[10])
			elif action in healing_fields:
				amount = int(combat_fields[10])
				
			# add or get source
			if self.entities.has_key(srcguid):
				source = self.entities[srcguid]
			else:
				source = Entity(srcguid, srcname)
				self.entities[srcguid] = source
		
			# add or get destination
			if self.entities.has_key(dstguid):
				destination = self.entities[dstguid]
			else:
				destination = Entity(dstguid, dstname)
				self.entities[dstguid] = destination

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
			if effect_type in damage_fields:
				encounter.total_damage += amount
			elif effect_type in healing_fields:
				encounter.total_healing += amount
				
			# update the timestamps, for dps/hps calculation
			if encounter.start_time == datetime.min:
				encounter.start_time = timestamp
			encounter.end_time = timestamp

			# add or get effect
			if effect_type == 'SWING_DAMAGE' or effect_type == 'SWING_MISSED':
				effect_name = 'Swing'
			else:
				effect_name = combat_fields[8][1:-1]
			effects = encounter.effects
			if effects.has_key(effect_name):
				effect = effects[effect_name]
			else:
				effect = Effect(effect_name)
				effects[effect_name] = effect
		
			# update effect stats
			if effect_type in missed_fields:
				amount = 0 # some miss stats have an amount (block, absorb, etc.)
				if effect_type == 'SWING_MISSED':
					miss_reason = combat_fields[7]
					if len(combat_fields) > 8:
						amount = int(combat_fields[8])
				else:
					miss_reason = combat_fields[10]
					if len(combat_fields) > 11:
						amount = int(combat_fields[11])
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
					effect.evade += 1
			elif effect_type in damage_fields:
				effect.total_damage += amount
				if effect_type == 'SPELL_PERIODIC_DAMAGE':
					effect.periodic_damage += amount
					effect.ticks += 1
				else:
					effect.damage += amount
					effect.hits += 1
			elif effect_type in healing_fields:
				effect.total_healing += amount
				effect.overheal += int(combat_fields[11])
				if effect_type == 'SPELL_PERIODIC_HEAL':
					effect.periodic_healing += amount
					effect.ticks += 1
				else:
					effect.healing += amount
					effect.hits += 1
