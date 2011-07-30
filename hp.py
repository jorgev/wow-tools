#!/usr/bin/env python

import csv
import sys
import getopt

help_message = '''
Usage: hp.py -n name logfile
'''

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def main(argv=None):
	if argv is None:
		argv = sys.argv
		
	try:
		try:
			opts, args = getopt.getopt(argv[1:], 'hn:v', ['help', 'name='])
		except getopt.error, msg:
			raise Usage(msg)

		# option processing
		name = None
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-n", "--name"):
				name = value

		# can read from file or stdin, assume file is the only argument, if any
		if len(args) > 0:
			reader = csv.reader(open(args[0]))
		else:
			reader = csv.reader(sys.stdin)

		# dictionary for storing hit points
		hp = {}
		
		# iterate over the rows in the log file
		for row in reader:
			# we need to further split the first field
			timestamp, event = row[0].split('  ')
		
			# filtering on name
			if name == row[6]:
				# must be a damage field
				if event in ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE', 'RANGE_DAMAGE']:
					if row[5] in hp:
						hp[row[5]] += int(row[12])
					else:
						hp[row[5]] = int(row[12])
				elif event == 'SWING_DAMAGE':
					if row[5] in hp:
						hp[row[5]] += int(row[9])
					else:
						hp[row[5]] = int(row[9])
				elif event == 'UNIT_DIED':
					if row[5] in hp:
						print 'Total HP for %s (%s) is %d' % (name, row[5], hp[row[5]])
				
	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2
		
if __name__ == "__main__":
	sys.exit(main())
