#!/usr/bin/env python

import csv
import sys

NPC_EFFECTS = { 'Temple Guardian Anhuur': [],
	'Searing Light': ['Burning Light'],
	'Invoked Flaming Spirit': ['Supernova'],
	'Corborus': ['Crystal Barrage'],
	'Slabhide': ['Sand Blast'],
	}

def main(argv=None):
	if argv is None:
		argv = sys.argv
	filename = argv[1]

	reader = csv.reader(open(filename))
	for row in reader:
		timestamp, event = row[0].split('  ')
		
		# the data we are interested in all has 21 fields in it, so we can verify that up front
		if len(row) == 21:
			# we're only interested in special effects, which fall into these categories
			if event in ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE']:
				source = row[2]
				# see if we have this npc in our dictionary
				if source in NPC_EFFECTS:
					effect = row[10]
					# see if we are interested in this effect from this specific nps
					if effect in NPC_EFFECTS[source]:
						# we're only interested in players (i.e., not pets, guardians, etc.)
						target_flags = int(row[7], 16)
						if target_flags & 0x400:
							# dump out the result and (hopefully) embarass the player
							print row[6], 'hit by', effect, 'for', row[12]

if __name__ == "__main__":
	sys.exit(main())
