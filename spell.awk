#!/usr/bin/awk -F: -f

BEGIN {
	# comma-delimited fields
	FS = ","

	# wrap in quotes since we're doing exact match and that's how it's logged
	quoted_effect = "\"" effect "\""
}

{
	# $1 actually contains two fields, which we need to split where the double-space occurs
	split($1, first, "  ")

	# we're only interested in spell damage and it must match the effect name
	if ((first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE") && $9 == quoted_effect)
	{
		# bump hit count and add damage total, based on target name
		hit_count[$6]++
		damage[$6] += $11
	}
}

END {
	# dump out stats
	print "Summary for effect:", effect
	for (name in hit_count)
		print name ":", hit_count[name], "time(s),", damage[name], "damage, avg", damage[name] / hit_count[name]
}

