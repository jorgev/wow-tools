fails = {}

function Phail_OnLoad(self)
	-- these are the events in which we are interested
	self:RegisterEvent("ADDON_LOADED");
	self:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED");
end

function Phail_OnEvent(self, event, ...)
	-- if we've loaded this add-on, print a message to let the user know
	if event == "ADDON_LOADED" then
		local addon = select(1, ...);
		if addon == "Phail" then
			DEFAULT_CHAT_FRAME:AddMessage("Phail add-on loaded");
		end
	elseif event == "COMBAT_LOG_EVENT_UNFILTERED" then
		-- grab the fields that are the same for all events
		local timestamp, combatEvent, sourceGUID, sourceName, sourceFlags, destGUID, destName, destFlags = ...;
		local eventPrefix, eventSuffix = combatEvent:match("^(.-)_?([^_]*)$");

		-- if this is a damage-type field, do the following
		if eventSuffix == "DAMAGE" then
			local amount, overkill, school, resisted, blocked, absorbed, critical, glancing, crushing = select(select("#", ...)-8, ...);
			local is_fail = false;
			if eventPrefix == "RANGE" or eventPrefix:match("^SPELL") then
			
				-- now that we know what type of event it is, we can get additional info
				local spellId, spellName, spellSchool = select(9, ...);
				
				-- would probably be cleaner to put this in a lookup table, these are the events we consider to be a fail
				if sourceName == "Lady Deathwhisper" then
					if spellName == "Death and Decay" then
						is_fail = true;
					end
				elseif sourceName == "Onyxia" then
					if spellName == "Tail Sweep" or spellName == "Breath"
						is_fail = true;
					end
				elseif sourceName == "Onyxian Lair Guard" then
					if spellName == "Blast Nova" then
						is_fail = true;
					end
				elseif sourceName == "Skybreaker Mortar Soldier" then
					if spellName == "Explosion" then
						is_fail = true;
					end
				end
			elseif eventPrefix == "SWING" then
			end
			
			-- if we got a phail, send a message
			if is_fail then
				fail_count = AddFail(destName);
				msg = string.format("%s was hit by %s, fail #%d", destName, spellName, fail_count);
				DEFAULT_CHAT_FRAME:AddMessage(msg, 1.0, 0.0, 0.0);
				-- other possible options to add
				-- SendChatMessage(msg, "RAID");
				-- SendChatMessage(msg, "WHISPER", nil, destName);
			end
		elseif eventSuffix == "HEAL" then
		end
	end
end

function AddFail(name)
	if fails[name] == nil then
		fails[name] = 1;
	else
		fails[name] = fails[name] + 1;
	end
	return fails[name];
end
