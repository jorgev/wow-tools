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

	if ($6 == "\"" target "\"")
	{
		if (first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE" || first[2] == "RANGE_DAMAGE")
		{
			hp[$5] += $11
		}
		else if (first[2] == "SWING_DAMAGE")
		{
			hp[$5] += $8
		}
		else if (first[2] == "UNIT_DIED")
		{
			dead[$5] = 1
		}
	}
}

END {
	# dump out stats
	print "Summary for target:", target
	for (id in hp)
		if (id in dead)
			print id ":", hp[id]
}

