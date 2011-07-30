#!/usr/bin/env python

import csv
import sys

def main(argv=None):
	if argv is None:
		argv = sys.argv
		
	# can read from file or stdin, assume file is the only argument, if any
	if len(argv) > 1:
		reader = csv.reader(open(argv[1]))
	else:
		reader = csv.reader(sys.stdin)

	# iterate over the rows in the log file
	for row in reader:
		# we need to further split the first field
		timestamp, event = row[0].split('  ')

if __name__ == "__main__":
	sys.exit(main())
