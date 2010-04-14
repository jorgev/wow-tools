#!/usr/bin/awk -F: -f
#
# this script is meant to be used to tail the combat log and points out when
# people do stupid stuff, such as standing in fire bombs or other avoidable
# damage

BEGIN {
	# comma-delimited fields
	FS = ","
}

{
	# $1 actually contains two fields, which we need to split where the double-space occurs
	split($1, first, "  ")

	# we're only interested in spell damage and it must match the effect name
	if ((first[2] == "SPELL_DAMAGE" || first[2] == "SPELL_PERIODIC_DAMAGE") && $9 == quoted_effect)
	{
	}
}

