#!/usr/bin/env python
# encoding: utf-8
"""
wowparse.py

Created by Jorge Velazquez on 2009-05-24.
"""

import sys
import os
import re
from datetime import datetime
from datetime import date

damage_fields = ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE', 'SWING_DAMAGE', 'RANGE_DAMAGE']
healing_fields = ['SPELL_HEAL', 'SPELL_PERIODIC_HEAL']
other_fields = ['SPELL_MISSED']
tracked_fields = damage_fields + healing_fields + other_fields

class effect_stats:
	def __init__(self, name):
		self.name = name
		self.total_healing = 0
		self.total_damage = 0
		self.hits = 0
		self.ticks = 0
		self.resists = 0
		self.misses = 0

class destination_stats:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.total_damage = 0
		self.total_healing = 0
		self.start_time = datetime.min
		self.end_time = datetime.min
		self.effects = {}

class source_stats:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.total_damage = 0
		self.total_healing = 0
		self.destinations = {}

def main():
	# command line args
	args = sys.argv[1:]
	help = False
	player_only = False
	filename = "WoWCombatLog.txt"
	srcname = dstname = ""
	for (index, arg) in enumerate(args):
		if arg == '-h':
			help = True
		elif arg == '-i':
			filename = args[index + 1]
		elif arg == '-s':
			srcname = args[index + 1]
		elif arg == '-d':
			dstname = args[index + 1]
		elif arg == '-p':
			player_only = True
	
	# if user just wants help, print usage and then exit
	if help:
		print "Usage: wowparse.py -i input_file [-s source] [-d destination]"
		return 0
	
	# start reading the file
	sources = {}
	line_count = 0
	parsed_line_count = 0
	hex_regex = re.compile('^0x[a-fA-F0-9]+$')
	dec_regex = re.compile('^\d+$')
	ts_regex = re.compile(r'^(\d+)/(\d+) (\d+):(\d+):(\d+)\.(\d+)')
	current_year = date.today().year
	file = open(filename, 'r')
	sys.stdout.write("Parsing " + filename)
	sys.stdout.flush()
	while True:
		line = file.readline()
		if not line:
			break
		line_count += 1
		if line_count % 10000 == 0:
			sys.stdout.write('.')
			sys.stdout.flush()
		
		# two spaces are used to split the date/time field from the actual combat data
		major_fields = line.split('  ')
		if len(major_fields) < 2:
			continue
		
		# save off the date/time info, we convert later but only if we need to (i.e., we have a log entry that we are interested in)
		date_time = major_fields[0]
		
		# here we provide our own line parser, since we have fields which may contain separators and are wrapped in quotes
		combat_data = major_fields[1]
		combat_fields = []
		in_quotes = False
		data = ""
		for char in combat_data:
			if char == '"':
				in_quotes = not in_quotes
			elif char == ',' and not in_quotes:
				if hex_regex.match(data):
					combat_fields.append(long(data, 16))
				elif dec_regex.match(data):
					combat_fields.append(int(data))
				else:
					combat_fields.append(data)
				data = ""
			else:
				data += char
		# add last field
		if hex_regex.match(data):
			combat_fields.append(long(data, 16))
		elif dec_regex.match(data):
			combat_fields.append(int(data))
		else:
			combat_fields.append(data)

		# all the stuff we're interested in requires 11 fields or greater
		if len(combat_fields) < 11:
			continue
		
		# must be one of the events that we actually track
		if not combat_fields[0] in tracked_fields:
			continue

		# if source or destination id is zero, we can't do anything with it
		if not combat_fields[1] or not combat_fields[4]:
			continue
			
		# check for source and/or destination match
		if (srcname and srcname != combat_fields[2]) or (dstname and dstname != combat_fields[5]):
			continue
			
		# actual number of lines parsed
		parsed_line_count += 1
		
		# get the timestamp (NOTE: year is not supplied in the combat log, this will cause problems if log file crosses a year boundary)
		m = ts_regex.match(date_time)
		if not m:
			print 'Failed to parse time: %s' % date_time
			continue
		timestamp = datetime(current_year, int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6)) * 1000)
		
		# add or get source
		if sources.has_key(combat_fields[1]):
			source = sources[combat_fields[1]]
		else:
			source = source_stats(combat_fields[1], combat_fields[2])
			sources[combat_fields[1]] = source
		
		# update the stats for the source
		if combat_fields[0] in damage_fields:
			if combat_fields[0] == 'SWING_DAMAGE':
				source.total_damage += combat_fields[7]
			else:
				source.total_damage += combat_fields[10]
		elif combat_fields[0] in healing_fields:
			source.total_healing += combat_fields[10]
		
		# add or get destination
		destinations = source.destinations
		if destinations.has_key(combat_fields[4]):
			destination = destinations[combat_fields[4]]
		else:
			destination = destination_stats(combat_fields[4], combat_fields[5])
			destinations[combat_fields[4]] = destination
			
		# update the stats for the destination
		if combat_fields[0] in damage_fields:
			if combat_fields[0] == 'SWING_DAMAGE':
				destination.total_damage += combat_fields[7]
			else:
				destination.total_damage += combat_fields[10]
		elif combat_fields[0] in healing_fields:
			destination.total_healing += combat_fields[10]
		
		# destination gets the timestamps
		if destination.start_time == datetime.min:
			destination.start_time = timestamp
		destination.end_time = timestamp
		
		# add or get effect
		if combat_fields[0] == 'SWING_DAMAGE':
			effect_name = "Swing"
		else:
			effect_name = combat_fields[8]
		effects = destination.effects
		if effects.has_key(effect_name):
			effect = effects[effect_name]
		else:
			effect = effect_stats(effect_name)
			effects[effect_name] = effect
			
		# update effect stats
		if combat_fields[0] == 'SPELL_MISSED':
			effect.misses += 1
		elif combat_fields[0] in damage_fields:
			if combat_fields[0] == 'SWING_DAMAGE':
				effect.total_damage += combat_fields[7]
			else:
				effect.total_damage += combat_fields[10]
			if combat_fields[0] == 'SPELL_PERIODIC_DAMAGE':
				effect.ticks += 1
			else:
				effect.hits += 1
		elif combat_fields[0] in healing_fields:
			effect.total_healing += combat_fields[10]
			if combat_fields[0] == 'SPELL_PERIODIC_HEAL':
				effect.ticks += 1
			else:
				effect.hits += 1
		
	# tell the user how many lines we actually read
	print "\n%d total lines found, %d lines parsed" % (line_count, parsed_line_count)
	
	# dump the stats out
	for source_id in sources.keys():
		source = sources[source_id]
		if source.total_damage > 0 and source.total_healing > 0:
			print "%s (0x%016X): %d damage, %d healing" % (source.name, source.id, source.total_damage, source.total_healing)
		elif source.total_damage > 0:
			print "%s (0x%016X): %d damage" % (source.name, source.id, source.total_damage)
		elif source.total_healing > 0:
			print "%s (0x%016X): %d healing" % (source.name, source.id, source.total_healing)
		for destination_id in source.destinations.keys():
			destination = source.destinations[destination_id]
			duration = destination.end_time - destination.start_time
			duration = duration.seconds + float(duration.microseconds) / 1000000;
			if destination.total_damage > 0 and destination.total_healing > 0:
				print "\t%s (0x%016X): %d damage received over %.3f sec (%.2f DPS), %d healing received" % (destination.name, destination.id, destination.total_damage, duration, destination.total_damage / duration if duration > 0.0 else destination.total_damage, destination.total_healing)
			elif destination.total_damage > 0:
				print "\t%s (0x%016X): %d damage received over %.3f sec (%.2f DPS)" % (destination.name, destination.id, destination.total_damage, duration, destination.total_damage / duration if duration > 0.0 else destination.total_damage)
			elif destination.total_healing > 0:
				print "\t%s (0x%016X): %d healing received" % (destination.name, destination.id, destination.total_healing)
			for effect_id in destination.effects.keys():
				effect = destination.effects[effect_id]
				if effect.total_damage > 0:
					if effect.hits > 0 and effect.ticks > 0:
						print "\t\t%s: %d damage, %d hits, %d ticks, %d misses" % (effect.name, effect.total_damage, effect.hits, effect.ticks, effect.misses)
					elif effect.hits > 0:
						print "\t\t%s: %d damage, %d hits, %.1f avg, %d misses" % (effect.name, effect.total_damage, effect.hits, effect.total_damage / float(effect.hits), effect.misses)
					elif effect.ticks > 0:
						print "\t\t%s: %d damage, %d ticks, %.1f avg, %d misses" % (effect.name, effect.total_damage, effect.ticks, effect.total_damage / float(effect.ticks), effect.misses)
				if effect.total_healing > 0:
					if effect.hits > 0 and effect.ticks > 0:
						print "\t\t%s: %d healing, %d hits, %d ticks" % (effect.name, effect.total_healing, effect.hits, effect.ticks)
					elif effect.hits > 0:
						print "\t\t%s: %d healing, %d hits, %.1f avg" % (effect.name, effect.total_healing, effect.hits, effect.total_healing / float(effect.hits))
					elif effect.ticks > 0:
						print "\t\t%s: %d healing, %d ticks, %.1f avg" % (effect.name, effect.total_healing, effect.ticks, effect.total_healing / float(effect.ticks))

if __name__ == '__main__':
	main()