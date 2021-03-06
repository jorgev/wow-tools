#!/usr/bin/env python

import csv
import sys
import getopt

help_message = '''
Usage: spell.py -e effect [-s source] [-d destination] logfile
'''

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	if argv is None:
		argv = sys.argv
	
	try:
		try:
			opts, args = getopt.getopt(argv[1:], 'he:s:d:v', ['help', 'effect=', 'source=', 'destination='])
		except getopt.error, msg:
			raise Usage(msg)

		# option processing
		effect = None
		source = None
		destination = None
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-e", "--effect"):
				effect = value
			if option in ("-s", "--source"):
				source = value
			if option in ("-d", "--destination"):
				destination = value

		# can read from file or stdin, assume file is the only argument, if any
		if len(args) > 0:
			reader = csv.reader(open(args[0]))
		else:
			reader = csv.reader(sys.stdin)

		# initialize our vars
		hit_damage = 0
		tick_damage = 0
		hits = 0
		ticks = 0
		
		# iterate over the rows in the log file
		for row in reader:
			# we need to further split the first field
			timestamp, event = row[0].split('  ')
			
			# has to be a field that contains a spell effect
			if not event in ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE']:
				continue

			# check if we're filtering
			if source and source != row[2]:
				continue
			if destination and destination != row[6]:
				continue
			
			# now match on the effect name
			if effect == row[10]:
				if event == 'SPELL_DAMAGE':
					hits += 1
					hit_damage += int(row[12])
				elif event == 'SPELL_PERIODIC_DAMAGE':
					ticks += 1
					tick_damage += int(row[12])
		
		# dump out the results
		if hits > 0 and ticks > 0:
			print '%s - %d hits for %d damage (%.1f avg), %d ticks for %d damage (%.1f avg)' % (effect, hits, hit_damage, float(hit_damage) / hits, ticks, tick_damage, float(tick_damage) / ticks)
		elif hits > 0:
			print '%s - %d hits for %d damage (%.1f avg)' % (effect, hits, hit_damage, float(hit_damage) / hits)
		elif ticks > 0:
			print '%s - %d ticks for %d damage (%.1f avg)' % (effect, ticks, tick_damage, float(tick_damage) / ticks)
		else:
			print 'No damage recorded for the arguments given'

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

if __name__ == "__main__":
	sys.exit(main())
