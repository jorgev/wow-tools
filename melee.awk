#!/usr/bin/awk -f

BEGIN {
	# comma-delimited fields
	FS = ","
}

{
	# $1 actually contains two fields, which we need to split where the double-space occurs
	split($1, first, "  ")

	if (first[2] == "SWING_MISSED" && ($10 == "BLOCK" || $10 == "PARRY"))
	{
		# bump hit count and add damage total, based on target name
		hit_count[$3]++
	}
}

END {
	# dump out stats
	print "Summary of blocked/parried melee attacks", effect
	for (name in hit_count)
		print name ":", hit_count[name], "time(s)"
}

