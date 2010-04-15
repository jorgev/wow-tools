#!/usr/bin/awk -f
#
# this script is meant to be used to tail the combat log and points out when
# people do stupid stuff, such as standing in fire bombs, getting hit by
# tail sweep, or other avoidable damage
#
# tail -f WoWCombatLog.txt | ./fail.awk

BEGIN {
	# comma-delimited fields
	FS = ","

	# build up our array of effects on which we want to warn
	onyxia_effects = "Breath,Tail Sweep"
	onyxia_effects_count = split(onyxia_effects, onyxia_effects_array, ",")
}

NF == 19 {
	# split the first field, since it has timestamp and effect type
	split($1, type, "  ")

	# trim off double-quotes
	effect = substr($9, 2, length($9) - 2)

	# we're only interested in spell damage and it must match the effect name
	if (type[2] == "SPELL_DAMAGE" || type[2] == "SPELL_PERIODIC_DAMAGE")
	{
		npc = substr($3, 2, length($3) - 2)
		if (npc == "Onyxia")
		{
			for (i = 0; i < onyxia_effects_count; ++i)
			{
				if (onyxia_effects_array[i] == effect)
				{
					damage_array[$2, $5] += $11
					print type[1], $6, $9, damage_array[$2, $5]
					break
				}
			}
		}
	}
}

