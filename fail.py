#!/usr/bin/env python

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

	for line in (x.strip() for x in open(filename)):
		major_split = line.split('  ')
		timestamp = major_split[0]
		fields = major_split[1].split(',')
		
		# the data we are interested in all has 21 fields in it, so we can verify that up front
		if len(fields) == 21:
			# we're only interested in special effects, which fall into these categories
			if fields[0] in ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE']:
				source = fields[2][1:-1]
				if source in NPC_EFFECTS:
					effect = fields[10][1:-1]
					if effect in NPC_EFFECTS[source]:
						# we're only interested in players
						target_flags = int(fields[7], 16)
						if target_flags & 0x400:
							print fields[6][1:-1], 'hit by', effect, 'for', fields[12]

if __name__ == "__main__":
	sys.exit(main())
