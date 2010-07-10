lay_waste_hits = {}

function Bytor_OnLoad(self)
	-- these are the events in which we are interested
	self:RegisterEvent("ADDON_LOADED");
	self:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED");
end

function Bytor_OnEvent(self, event, ...)
	-- if we've loaded this add-on, print a message to let the user know
	if event == "ADDON_LOADED" then
		local addon = select(1, ...);
		if addon == "Bytor" then
			DEFAULT_CHAT_FRAME:AddMessage("Bytor add-on loaded");
		end
	elseif event == "COMBAT_LOG_EVENT_UNFILTERED" then
		-- grab the fields that are the same for all events
		local timestamp, combatEvent, sourceGUID, sourceName, sourceFlags, destGUID, destName, destFlags = ...;
		local eventPrefix, eventSuffix = combatEvent:match("^(.-)_?([^_]*)$");

		-- if this is a damage-type field, do the following
		if eventSuffix == "DAMAGE" then
			local amount, overkill, school, resisted, blocked, absorbed, critical, glancing, crushing = select(select("#", ...)-8, ...);
			local lay_waste = false;
			if eventPrefix == "RANGE" or eventPrefix:match("^SPELL") then
			
				-- now that we know what type of event it is, we can get additional info
				local spellId, spellName, spellSchool = select(9, ...);
				
				-- would probably be cleaner to put this in a lookup table, these are the events we consider to be a fail
				if sourceName == "Blazing Skeletons" and spellId == 69325 then
					lay_waste = true;
					if lay_waste_hits[sourceGUID] == nil then
						lay_waste_hits[sourceGUID] = 1;
					else
						lay_waste_hits[sourceGUID] = lay_waste_hits[sourceGUID] + 1;
					end
				end
			elseif eventPrefix == "SWING" then
			end
			
			-- if blazing skeleton is still up, send a message
			if lay_waste then
				msg = string.format("Bytor sez: Blazing Skeleton still up!!! Lay Waste (%d)", lay_waste_hits[sourceGUID]);
				-- DEFAULT_CHAT_FRAME:AddMessage(msg, 1.0, 0.0, 0.0);
				SendChatMessage(msg, "RAID");
				-- SendChatMessage(msg, "WHISPER", nil, destName);
			end
		elseif eventSuffix == "HEAL" then
		elseif combatEvent == "SPELL_AURA_APPLIED" then
			local spellId, spellName, spellSchool = select(9, ...);

			-- if a player has been hit with mutated infection, set them as the target
			if sourceName == "Rotface" and spellId == 69674 then
			end
		elseif combatEvent == "SPELL_AURA_REMOVED" then
			local spellId, spellName, spellSchool = select(9, ...);

			-- if mutated infection has been removed from the player, we remove the focus
			if sourceName == "Rotface" and spellId == 69674 then
			end
		end
	end
end

