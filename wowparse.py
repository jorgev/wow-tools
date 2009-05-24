#!/usr/bin/env python
# encoding: utf-8
"""
wowparse.py

Created by Jorge Velazquez on 2009-05-24.
"""

import sys
import os

def main():
	# command line args
	args = sys.argv[1:]
	help = False
	filename = "WoWCombatLog.txt"
	for (index, arg) in enumerate(args):
		if arg == '-h':
			help = True
		elif arg == '-i':
			filename = args[index + 1]
		elif arg == '-s':
			source = args[index + 1]
		elif arg == '-d':
			dest = args[index + 1]
	
	# if user just wants help, print usage and then exit
	if help:
		print "Usage: wowparse.py -i inputfile"
		return 0
	
	# start reading the file
	print "Opening " + filename + "..."
	file = open(filename)
	while True:
		line = file.readline()
		if not line:
			break

if __name__ == '__main__':
	main()

class attack_stats:
	def __init__(self, name):
		self.name = name