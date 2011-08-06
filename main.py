#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Jorge Velázquez on 2010-12-11.

This script is provided mostly for showing how to use the parser.  It can be easily
modified or enhanced to provide additional information from the log files.
"""

import sys
import getopt
import parser

help_message = '''
Usage: main.py [-s source] [-d destination] logfile
'''

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], 'hs:d:v', ['help', 'source=', 'destination='])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		source = None
		destination = None
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-s", "--source"):
				source = value
			if option in ("-d", "--destination"):
				destination = value

		if len(args) == 0:
			print >> sys.stderr, 'Please provide the name of the log file as the last argument on the command line'
			return 1
		filename = args[0]
		
		# parse the log file	
		log_info = parser.LogInfo()
		encounters = log_info.Parse(filename, source_name=source, destination_name=destination)
		
		# dump out the stats
		for encounter in encounters:
			print '%s (0x%016X) => %s (0x%016X):' % (encounter.src.name, encounter.src.id, encounter.dst.name, encounter.dst.id)
			elapsed_time = encounter.elapsed_time()
			if encounter.total_healing > 0:
				print '\tTotal healing - %d over %.1f seconds (%.1f HPS)' % (encounter.total_healing, elapsed_time, encounter.total_healing / elapsed_time),
				if encounter.total_overhealing:
					print '- %d overhealing (%.1f%%)' % (encounter.total_overhealing, encounter.total_overhealing * 100.0 / encounter.total_healing),
				print
				for key in sorted(encounter.effects.keys()):
					value = encounter.effects[key]
					print '\t\t%s' % value.name,
					if value.total_healing:
						print '- %d healing' % value.total_healing,
					if value.healing:
						print '- %d hits (%.1f avg)' % (value.hits, value.healing / float(value.hits)),
					if value.periodic_healing:
						print '- %d ticks (%.1f avg)' % (value.ticks, value.periodic_healing / float(value.ticks)),
					if value.overheal:
						print '- %d overhealing (%.1f%%)' % (value.overheal, value.overheal * 100.0 / value.total_healing),
					print
			if encounter.total_damage > 0:
				print '\tTotal damage - %d over %.1f seconds (%.1f DPS)' % (encounter.total_damage, elapsed_time, encounter.total_damage / elapsed_time)
				for key in sorted(encounter.effects.keys()):
					value = encounter.effects[key]
					print '\t\t%s' % value.name,
					if value.total_damage:
						print '- %d damage' % value.total_damage,
					if value.damage:
						print '- %d hits (%.1f avg)' % (value.hits, value.damage / float(value.hits)),
					if value.periodic_damage:
						print '- %d ticks (%.1f avg)' % (value.ticks, value.periodic_damage / float(value.ticks)),
					if value.immune:
						print '- %d immune' % value.immune,
					if value.missed:
						print '- %d missed' % value.missed,
					if value.resisted:
						print '- %d resisted' % value.resisted,
					if value.dodged:
						print '- %d dodged' % value.dodged,
					if value.parried:
						print '- %d parried' % value.parried,
					if value.absorbed:
						print '- %d hits absorbed for %d' % (value.absorbed, value.absorbed_amount),
					print

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

if __name__ == "__main__":
	sys.exit(main())
