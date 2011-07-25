#!/usr/bin/awk -f
# this script parses log files and looks up spell damage by effect name and dumps out stats, source and destination are optional
# usage: ./spell.awk -v effect="<effect_name>" [-v source="<source>"] [-v destination="<destination>"] <combat_log_file>
# e.g., ./spell.awk -v effect="Blast Nova" WoWCombatLog.txt

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
	if (source && destination)
	{
		if ((first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE") && $11 == quoted_effect && $3 == "\"" source "\"" && $6 == "\"" destination "\"")
		{
			# bump hit count and add damage total, based on target name
			hit_count[$7]++
			damage[$7] += $13
		}
	}
	else if (source)
	{
		if ((first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE") && $11 == quoted_effect && $3 == "\"" source "\"")
		{
			# bump hit count and add damage total, based on target name
			hit_count[$7]++
			damage[$7] += $13
		}
	}
	else if (destination)
	{
		if ((first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE") && $11 == quoted_effect && $6 == "\"" destination "\"")
		{
			# bump hit count and add damage total, based on target name
			hit_count[$7]++
			damage[$7] += $13
		}
	}
	else
	{
		if ((first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE") && $11 == quoted_effect)
		{
			# bump hit count and add damage total, based on target name
			hit_count[$7]++
			damage[$7] += $13
		}
	}
}

END {
	# dump out stats
	print "Summary for effect:", effect
	for (name in hit_count)
		print name ":", hit_count[name], "time(s),", damage[name], "damage, avg", damage[name] / hit_count[name]
}

