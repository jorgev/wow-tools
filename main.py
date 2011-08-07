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
Usage: main.py [-s source] [-d destination] [--ignore_pets] [--ignore_guardians] logfile
'''

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], 'hs:d:v', ['help', 'source=', 'destination=', 'ignore_pets', 'ignore_guardians'])
		except getopt.error, msg:
			raise Usage(msg)
	
		# option processing
		source = None
		destination = None
		ignore_pets = False
		ignore_guardians = False
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-s", "--source"):
				source = value
			if option in ("-d", "--destination"):
				destination = value
			if option in ("--ignore_pets"):
				ignore_pets = True
			if option in ("--ignore_guardians"):
				ignore_guardians = True

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
					effect = encounter.effects[key]
					print '\t\t%s' % effect.name,
					if effect.total_healing:
						print '- %d healing' % effect.total_healing,
					if effect.healing:
						print '- %d hits (%.1f avg)' % (effect.hits, effect.healing / float(effect.hits)),
					if effect.periodic_healing:
						print '- %d ticks (%.1f avg)' % (effect.ticks, effect.periodic_healing / float(effect.ticks)),
					if effect.overheal:
						print '- %d overhealing (%.1f%%)' % (effect.overheal, effect.overheal * 100.0 / effect.total_healing),
					print
			if encounter.total_damage > 0:
				print '\tTotal damage - %d over %.1f seconds (%.1f DPS)' % (encounter.total_damage, elapsed_time, encounter.total_damage / elapsed_time)
				for key in sorted(encounter.effects.keys()):
					effect = encounter.effects[key]
					print '\t\t%s' % effect.name,
					if effect.total_damage:
						print '- %d damage' % effect.total_damage,
					if effect.damage:
						print '- %d hits (%.1f avg)' % (effect.hits, effect.damage / float(effect.hits)),
					if effect.periodic_damage:
						print '- %d ticks (%.1f avg)' % (effect.ticks, effect.periodic_damage / float(effect.ticks)),
					if effect.immune:
						print '- %d immune' % effect.immune,
					if effect.missed:
						print '- %d missed' % effect.missed,
					if effect.resisted:
						print '- %d resisted' % effect.resisted,
					if effect.dodged:
						print '- %d dodged' % effect.dodged,
					if effect.parried:
						print '- %d parried' % effect.parried,
					if effect.absorbed:
						print '- %d hits absorbed for %d' % (effect.absorbed, effect.absorbed_amount),
					print

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

if __name__ == "__main__":
	sys.exit(main())
