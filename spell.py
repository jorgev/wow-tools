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

		# iterate over the rows in the log file
		for row in reader:
			# we need to further split the first field
			timestamp, event = row[0].split('  ')

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2

if __name__ == "__main__":
	sys.exit(main())
