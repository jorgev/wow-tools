#!/usr/bin/awk -f
# this script parses log files and looks up spell damage by effect name and dumps out stats, source and destination are optional
# usage: ./hp.awk -v target="<target>" <combat_log_file>

BEGIN {
	# comma-delimited fields
	FS = ","
}

{
	# $1 actually contains two fields, which we need to split where the double-space occurs
	split($1, first, "  ")

	if ($7 == "\"" target "\"")
	{
		if (first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE" || first[2] == "RANGE_DAMAGE")
		{
			# for all types of damage except swing, the damage amount is field 11
			hp[$6] += $13
		}
		else if (first[2] == "SWING_DAMAGE")
		{
			# for swing damage, the damage amount is in field 8
			hp[$6] += $10
		}
		else if (first[2] == "UNIT_DIED")
		{
			# log whether or not the unit died, we only dump out stats for dead things
			dead[$6] = 1
		}
	}
}

END {
	# set up the vars we'll use to track the hp
	print "HP totals for target:", target
	count = 0
	total = 0
	min = 0
	max = 0

	# iterate through each npc that we tracked
	for (id in hp)
		# only dump stats for npcs that died, otherwise total hp is going to be inaccurate
		if (id in dead)
		{
			print id ":", hp[id]
			count++
			total += hp[id]
			if (min == 0)
				min = hp[id]
			else
			{
				if (hp[id] < min)
					min = hp[id]
			}
			if (hp[id] > max)
				max = hp[id]
		}

	if (count > 0)
		printf("Count/Min/Max/Avg: %d/%d/%d/%.1f\n", count, min, max, total / count)
	else
		print "No data found for", target
}

