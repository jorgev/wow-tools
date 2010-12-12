#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Jorge Velázquez on 2010-12-11.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import sys
import getopt
import parser

help_message = '''
The help message goes here.
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
		filename = args[0]

		if not source and not destination:
			print >> sys.stderr, 'Please provide either a source or destination'
			return 1
			
		log_info = parser.LogInfo()
		log_info.Parse(filename, source_name=source, destination_name=destination)
		for encounter in log_info.encounters:
			print encounter.src.name, '->', encounter.dst.name + ':'
			elapsed_time = encounter.elapsed_time()
			if encounter.total_healing > 0:
				print '\tTotal healing %d over %.1f seconds (%.1f HPS)' % (encounter.total_healing, elapsed_time, encounter.total_healing / elapsed_time)
				for v in encounter.effects.values():
					print '\t\t%s - %d' % (v.name, v.total_healing)
			if encounter.total_damage > 0:
				print '\tTotal damage %d over %.1f seconds (%.1f DPS)' % (encounter.total_damage, elapsed_time, encounter.total_damage / elapsed_time)
				for v in encounter.effects.values():
					print '\t\t%s - %d' % (v.name, v.total_damage)

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

if __name__ == "__main__":
	sys.exit(main())
