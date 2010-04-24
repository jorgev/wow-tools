// wowparse.cc - combat log parser

#include <fstream>
#include <iostream>
#include <string>
#include <iomanip>
#include <vector>
#include <map>
#include <algorithm>
#include <boost/date_time.hpp>
#include <boost/program_options.hpp>
#include <boost/shared_ptr.hpp>

namespace po = boost::program_options;
namespace dt = boost::posix_time;

const char* SPELL_DAMAGE = "SPELL_DAMAGE";
const char* SPELL_PERIODIC_DAMAGE = "SPELL_PERIODIC_DAMAGE";
const char* SPELL_HEAL = "SPELL_HEAL";
const char* SPELL_PERIODIC_HEAL = "SPELL_PERIODIC_HEAL";
const char* SWING_DAMAGE = "SWING_DAMAGE";
const char* RANGE_DAMAGE = "RANGE_DAMAGE";
const char* SPELL_CAST_SUCCESS = "SPELL_CAST_SUCCESS";
const char* UNIT_DIED = "UNIT_DIED";
const char* SPELL_AURA_APPLIED = "SPELL_AURA_APPLIED";
const char* SPELL_AURA_REMOVED = "SPELL_AURA_REMOVED";
const char* SPELL_MISSED = "SPELL_MISSED";
const char* SWING_MISSED = "SWING_MISSED";
const char* RANGE_MISSED = "RANGE_MISSED";
const unsigned int LINESIZE = 1024;
const unsigned int PLAYER_MASK = 0x00000400;
const unsigned int NPC_MASK = 0x00000800;
const unsigned int PET_MASK = 0x00001000;
const unsigned int GUARDIAN_MASK = 0x00002000;
const unsigned int NEUTRAL_MASK = 0x00000020;

class attackstats
{
public:
	attackstats(std::string& attackname);

	std::string getname() const { return name; }
	void addspelldamage(unsigned long damage) { spellhits++; spelldamage += damage; totaldamage += damage; }
	void addspellperiodicdamage(unsigned long damage) { ticks++; spellperiodicdamage += damage; totaldamage += damage; }
	void addspellheal(unsigned long heal) { healhits++; spellheal += heal; totalhealing += heal; }
	void addspellperiodicheal(unsigned long heal) { healticks++; spellperiodicheal += heal; totalhealing += heal; }
	void addspelloverheal(unsigned long overheal) { spelloverheal += overheal; }
	void addswingdamage(unsigned long damage) { swinghits++; swingdamage += damage; totaldamage += damage; }
	void addrangedamage(unsigned long damage) { rangehits++; rangedamage += damage; totaldamage += damage; }
	void addcrit() { crits++; }
	void addperiodiccrit() { periodiccrits++; }
	void addmiss() { missed++; }
	void adddodge() { dodged++; }
	void addblock() { blocked++; }
	void addparry() { parried++; }
	void addabsorb() { absorbed++; }
	void addimmune() { immune++; }
	void addresist() { resisted++; }
	void addreflect() { reflected++; }
	void addevade() { evaded++; }
	unsigned int getcrits() const { return crits; }
	unsigned int getperiodiccrits() const { return periodiccrits; }
	unsigned int getticks() const { return ticks; } 
	unsigned int gethealticks() const { return healticks; }
	unsigned int getswinghits() const { return swinghits; }
	unsigned int getrangehits() const { return rangehits; }
	unsigned int getspellhits() const { return spellhits; }
	unsigned int gethealhits() const { return healhits; }
	unsigned long getspelldamage() const { return spelldamage; }
	unsigned long getspellperiodicdamage() const { return spellperiodicdamage; }
	unsigned long getspellheal() const { return spellheal; }
	unsigned long getspellperiodicheal() const { return spellperiodicheal; }
	unsigned long getspelloverheal() const { return spelloverheal; }
	unsigned long getswingdamage() const { return swingdamage; }
	unsigned long getrangedamage() const { return rangedamage; }
	unsigned long gettotaldamage() const { return totaldamage; }
	unsigned long gettotalhealing() const { return totalhealing; }
	unsigned int getmissed() { return missed; }
	unsigned int getdodged() { return dodged; }
	unsigned int getblocked() { return blocked; }
	unsigned int getparried() { return parried; }
	unsigned int getabsorbed() { return absorbed; }
	unsigned int getimmune() { return immune; }
	unsigned int getresisted() { return resisted; }
	unsigned int getreflected() { return reflected; }
	unsigned int getevaded() { return evaded; }

private:
	std::string name;
	unsigned int ticks;
	unsigned int crits;
	unsigned int periodiccrits;
	unsigned int healticks;
	unsigned int swinghits;
	unsigned int rangehits;
	unsigned int spellhits;
	unsigned int healhits;
	unsigned int missed;
	unsigned int dodged;
	unsigned int blocked;
	unsigned int parried;
	unsigned int absorbed;
	unsigned int resisted;
	unsigned int immune;
	unsigned int reflected;
	unsigned int evaded;
	unsigned long totaldamage;
	unsigned long totalhealing;
	unsigned long spelldamage;
	unsigned long spellperiodicdamage;
	unsigned long spellheal;
	unsigned long spellperiodicheal;
	unsigned long spelloverheal;
	unsigned long swingdamage;
	unsigned long rangedamage;
};

attackstats::attackstats(std::string& attackname)
{
	name = attackname;
	ticks = 0;
	crits = 0;
	periodiccrits = 0;
	healticks = 0;
	swinghits = 0;
	rangehits = 0;
	spellhits = 0;
	healhits = 0;
	totaldamage = 0;
	totalhealing = 0;
	spelldamage = 0;
	spellperiodicdamage = 0;
	spellheal = 0;
	spellperiodicheal = 0;
	spelloverheal = 0;
	swingdamage = 0;
	rangedamage = 0;
	missed = 0;
	dodged = 0;
	blocked = 0;
	parried = 0;
	absorbed = 0;
	resisted = 0;
	immune = 0;
	reflected = 0;
	evaded = 0;
}

typedef boost::shared_ptr<attackstats> attackstats_ptr;
typedef std::vector<attackstats_ptr> attackvector;
typedef attackvector::const_iterator attackiter;

class destinationstats
{
public:
	destinationstats(unsigned long long destinationid, std::string& destinationname);

	unsigned long long getid() const { return id; }
	std::string getname() const { return name; }
	void addtodamage(unsigned long damage) { totaldamage += damage; }
	void addtohealing(unsigned long healing) { totalhealing += healing; }
	void setisplayer() { isplayer = true; }
	unsigned long gettotaldamage() const { return totaldamage; }
	unsigned long gettotalhealing() const { return totalhealing; }
	dt::time_duration gettotaltime() const { return std::max((end - start), dt::time_duration(0, 0, 1)); }
	bool getisplayer() const { return isplayer; }
	attackvector& getattacks() { return attacks; }
	void addattack(attackstats_ptr attack) { attacks.push_back(attack); }
	void addtimestamp(dt::ptime timestamp);

private:
	unsigned long long id;
	std::string name;
	unsigned long totaldamage;
	unsigned long totalhealing;
	bool isplayer;
	attackvector attacks;
	dt::ptime start, end;
};

destinationstats::destinationstats(unsigned long long destinationid, std::string& destinationname)
{
	id = destinationid;
	name = destinationname;
	totaldamage = 0;
	totalhealing = 0;
	isplayer = false;
}

void destinationstats::addtimestamp(dt::ptime timestamp)
{
	if (start == dt::not_a_date_time)
		start = timestamp;
	end = timestamp;
}

typedef boost::shared_ptr<destinationstats> destinationstats_ptr;
typedef std::map<unsigned long long, destinationstats_ptr> destinationmap;
typedef destinationmap::const_iterator destinationiter;

class sourcestats
{
public:
	sourcestats(unsigned long long sourceid, std::string& sourcename);

	std::string getname() const { return name; }
	unsigned long long getid() const { return id; }
	void addtodamage(unsigned long damage) { totaldamage += damage; }
	void addtohealing(unsigned long healing) { totalhealing += healing; }
	unsigned long gettotaldamage() const { return totaldamage; }
	unsigned long gettotalhealing() const { return totalhealing; }
	destinationmap& getdestinations() { return destinations; }
	dt::time_duration gettotaltime() const { return std::max((end - start), dt::time_duration(0, 0, 1)); }
	void addtimestamp(dt::ptime timestamp);

private:
	std::string name;
	unsigned long long id;
	unsigned long totaldamage;
	unsigned long totalhealing;
	destinationmap destinations;
	dt::ptime start, end;
};

sourcestats::sourcestats(unsigned long long sourceid, std::string& sourcename)
{
	name = sourcename;
	id = sourceid;
	totaldamage = 0;
	totalhealing = 0;
}

void sourcestats::addtimestamp(dt::ptime timestamp)
{
	if (start == dt::not_a_date_time)
		start = timestamp;
	end = timestamp;
}

typedef boost::shared_ptr<sourcestats> sourcestats_ptr;
typedef std::map<unsigned long long, sourcestats_ptr> sourcemap;
typedef sourcemap::const_iterator sourceiter;

// for sorting
class compare_damage
{
public:
	bool operator()(const sourcestats_ptr& p1, const sourcestats_ptr& p2) const
		{ return p1->gettotaldamage() > p2->gettotaldamage(); }
};

class compare_healing
{
public:
	bool operator()(const sourcestats_ptr& p1, const sourcestats_ptr& p2) const
		{ return p1->gettotalhealing() > p2->gettotalhealing(); }
};

int main(int argc, char* argv[])
{
	// first arg should be file name
	std::string filename = "WoWCombatLog.txt";
	std::string source;
	std::string destination;
	bool ignore_pets = false;
	bool ignore_guardians = false;

	// define the command line arguments that we accept
	po::options_description desc("Program options");
	desc.add_options()
		("help,h", "print usage")
		("input-file,i", po::value<std::string>(), "input file")
		("source,s", po::value<std::string>(), "source")
		("destination,d", po::value<std::string>(), "destination")
		("ignore-pets", "don't process stats for pets")
		("ignore-guardians", "don't process stats for guardians (army of the dead, bloodworms, etc.)")
	;
	po::variables_map vm;
	try
	{
		po::store(po::parse_command_line(argc, argv, desc), vm);
		po::notify(vm);	
	}
	catch (std::exception& ex)
	{
		std::cerr << ex.what() << std::endl << desc << std::endl;
		return 1;
	}

	// see if the user just wants usage printed
	if (vm.count("help"))
	{
		std::cout << desc << std::endl;
		return 0;
	}

	// grab any command line args
	if (vm.count("input-file"))
		filename = vm["input-file"].as<std::string>();
	if (vm.count("source"))
		source = vm["source"].as<std::string>();
	if (vm.count("destination"))
		destination = vm["destination"].as<std::string>();
	if (vm.count("ignore-pets"))
		ignore_pets = true;
	if (vm.count("ignore-guardians"))
		ignore_guardians = true;

	// let the user know what we're doing, to make sure it's what they want
	std::cout << "Parsing file: " << filename << std::endl;
	if (source.length() > 0)
		std::cout << "Filtering on source: " << source << std::endl;
	if (destination.length() > 0)
		std::cout << "Filtering on destination: " << destination << std::endl;
	if (ignore_pets)
		std::cout << "Ignoring pets" << std::endl;
	if (ignore_guardians)
		std::cout << "Ignoring guardians" << std::endl;
	std::cout << std::endl;

	// open the log file
	std::fstream ifs(filename.c_str(), std::ifstream::in);
	if (!ifs)
	{
		std::cerr << "Failed to open file " << filename << std::endl;
		return 1;
	}
	
	// initialize our counters and other objects and start reading lines
	long linecount = 0;
	long lineparsedcount = 0;
	char line[LINESIZE];
	sourcemap sources;
	time_t rawtime;
	struct tm* timeinfo;
	time(&rawtime);
	timeinfo = localtime(&rawtime);
	char year[8];
	strftime(year, 8, "%Y-", timeinfo);
	dt::ptime start = dt::microsec_clock::local_time();
	std::vector<const char*> fields;
	std::string action, srcname, dstname, effect, result, ph, result2;
	unsigned long long srcguid, dstguid;
	unsigned int srcflags, dstflags;
	unsigned int amount, overheal;
	std::istringstream is;
	while (ifs.getline(line, LINESIZE))
	{
		// bump line count
		linecount++;

		// remove trailing carriage return, if there is one
		char* p = strstr(line, "\r");
		if (p != NULL)
			*p = 0;

		// double space separates date and combat info
		p = strstr(line, "  ");
		if (p == NULL)
			continue;

		// parse the combat data...comma-separated with occasional double-quotes surrounding some fields
		fields.clear();
		*p = 0; // null terminate so we can read time later
		p += 2;
		char* temp = p;
		while (*temp)
		{
			bool inquotes = false;
			if (*temp == '"')
			{
				inquotes = true;
				p = ++temp;
			}
			while (*temp && (*temp != ',' || inquotes))
			{
				if (*temp == '"')
				{
					inquotes = false;
					*temp = 0;
				}
				temp++;
			}
			if (*temp)
				*temp++ = 0;
			fields.push_back(p);
			p = temp;
		}

		// make sure we have enough fields on this line, otherwise we ignore it
		if (fields.size() < 11)
			continue;

		// assign the first fields we are filting on
		action = fields[0];
		srcname = fields[2];
		dstname = fields[5];

		// before going any further, check for valid fields
		if (source.length() > 0 && srcname != source)
			continue;
		if (destination.length() > 0 && dstname != destination)
			continue;
		if (srcname == "nil" || dstname == "nil")
			continue;
		
		// log item must be one of these types (this list may change)
		if (action == SPELL_DAMAGE || action == SPELL_PERIODIC_DAMAGE || action == RANGE_DAMAGE || action == SWING_DAMAGE || action == SPELL_HEAL || action == SPELL_PERIODIC_HEAL ||
			action == SPELL_MISSED || action == SWING_MISSED || action == RANGE_MISSED)
		{
			// parse the remainder of the fields
			is.str(fields[3]);
			is >> std::hex >> srcflags;
			is.clear();
			is.str(fields[6]);
			is >> std::hex >> dstflags;
			is.clear();

			// see if we're ignoring pet data
			if (ignore_pets && ((srcflags & PET_MASK) || (dstflags & PET_MASK)))
				continue;

			// see if we're ignoring guardians
			if (ignore_guardians && ((srcflags & GUARDIAN_MASK) || (dstflags & GUARDIAN_MASK)))
				continue;

			// parse the rest of the fields
			is.str(fields[1]);
			is >> std::hex >> srcguid;
			is.clear();
			is.str(fields[4]);
			is >> std::hex >> dstguid;
			is.clear();
			result = fields[7];
			effect = fields[8];
			ph = fields[9];
			result2 = fields[10];
			is.str(fields[10]);
			is >> std::dec >> amount;
			is.clear();

			// time conversion is probably expensive, so we defer it to here...log doesn't give us years, so we need to fix it
			char* slash =  strchr(line, '/');
			if (slash != NULL)
				*slash = '-';
			dt::ptime t = dt::time_from_string(std::string(year) + line);

			// fixup for swing damage, since format is different
			if (action == SWING_DAMAGE)
			{
				effect = "Swing";
				is.str(result);
				is >> std::dec >> amount;
				is.clear();
			}

			// get or create the current source by id
			sourcestats_ptr cursource = sources[srcguid];
			if (cursource == NULL)
			{
				cursource = sourcestats_ptr(new sourcestats(srcguid, srcname));
				sources[srcguid] = cursource;
			}

			// update timestamp for dps/hps calculations
			cursource->addtimestamp(t);

			// add to overall damage or healing stats at the source level
			if (action == SPELL_DAMAGE || action == SPELL_PERIODIC_DAMAGE || action == RANGE_DAMAGE || action == SWING_DAMAGE)
				cursource->addtodamage(amount);
			else if (action == SPELL_HEAL || action == SPELL_PERIODIC_HEAL)
				cursource->addtohealing(amount);

			// get or create the current destination by id
			destinationmap& destinations = cursource->getdestinations();
			destinationstats_ptr curdestination = destinations[dstguid];
			if (curdestination == NULL)
			{
				// if this is a player character, we set the flag
				curdestination = destinationstats_ptr(new destinationstats(dstguid, dstname));
				if (dstflags & PLAYER_MASK)
					curdestination->setisplayer();
				destinations[dstguid] = curdestination;
			}

			// update timestamp for dps/hps calculations
			curdestination->addtimestamp(t);

			// add to overall damage or healing stats at the destination level
			if (action == SPELL_DAMAGE || action == SPELL_PERIODIC_DAMAGE || action == RANGE_DAMAGE || action == SWING_DAMAGE)
				curdestination->addtodamage(amount);
			else if (action == SPELL_HEAL || action == SPELL_PERIODIC_HEAL)
				curdestination->addtohealing(amount);

			// get the current attack type
			attackstats_ptr curattack;
			attackvector& attacks = curdestination->getattacks();
			attackiter iter3 = attacks.begin();
			attackiter end = attacks.end();
			while (iter3 != end)
			{
				attackstats_ptr tmp = *iter3;
				if (tmp->getname() == effect)
				{
					curattack = tmp;
					break;
				}
				++iter3;
			}

			// this attack type doesn't exist yet for the destination target, create it
			if (!curattack)
			{
				curattack = attackstats_ptr(new attackstats(effect));
				curdestination->addattack(curattack);
			}

			// update the individual healing or damage stat
			if (action == SPELL_DAMAGE)
				curattack->addspelldamage(amount);
			else if (action == SPELL_PERIODIC_DAMAGE)
				curattack->addspellperiodicdamage(amount);
			else if (action == SPELL_HEAL)
				curattack->addspellheal(amount);
			else if (action == SPELL_PERIODIC_HEAL)
				curattack->addspellperiodicheal(amount);
			else if (action == RANGE_DAMAGE)
				curattack->addrangedamage(amount);
			else if (action == SWING_DAMAGE)
				curattack->addswingdamage(amount);
			
			// was it a crit?
			if (fields.size() == 19 && std::string(fields[16]) == "1")
			{
				if (action == SPELL_PERIODIC_DAMAGE)
					curattack->addperiodiccrit();
				else
					curattack->addcrit();
			}
			else if (fields.size() == 16 && std::string(fields[13]) == "1")
			{
				// this will be the case for swing damage crits
				curattack->addcrit();
			}
			else if (fields.size() == 14 && std::string(fields[13]) == "1")
			{
				if (action == SPELL_PERIODIC_HEAL)
					curattack->addperiodiccrit();
				else
					curattack->addcrit();
			}

			// overheal
			if ((action == SPELL_PERIODIC_HEAL || action == SPELL_HEAL) && std::string(fields[11]) != "0")
			{
				is.str(fields[11]);
				is >> std::dec >> overheal;
				is.clear();
				curattack->addspelloverheal(overheal);
			}

			// various miss types
			std::string miss_detail;
			if (action == SPELL_MISSED || action == RANGE_MISSED)
				miss_detail = result2;
			else if (action == SWING_MISSED)
				miss_detail = result;
			if (miss_detail == "ABSORB")
				curattack->addabsorb();
			else if (miss_detail == "BLOCK")
				curattack->addblock();
			else if (miss_detail == "PARRY")
				curattack->addparry();
			else if (miss_detail == "IMMUNE")
				curattack->addimmune();
			else if (miss_detail == "DODGE")
				curattack->adddodge();
			else if (miss_detail == "MISS")
				curattack->addmiss();
			else if (miss_detail == "RESIST")
				curattack->addresist();
			else if (miss_detail == "REFLECT")
				curattack->addreflect();
			else if (miss_detail == "EVADE")
				curattack->addevade();
		}

		// this is the actual # of lines we processed
		lineparsedcount++;
	}

	// parse timing info
	dt::ptime end = dt::microsec_clock::local_time();
	dt::time_duration elapsed = end - start;

	// dump the stats out
	unsigned long globaldamage = 0;
	unsigned long globalhealing = 0;
	sourceiter source_end = sources.end();
	std::cout << std::fixed << std::setprecision(1);
	for (sourceiter iter = sources.begin(); iter != source_end; ++iter)
	{
		// iterate through each source
		const sourcestats_ptr tmp = iter->second;
		unsigned char type_mask = (tmp->getid() & 0x0070000000000000) >> 52;
		std::string type = "Unknown";
		if (type_mask == 0)
			type = "Player";
		else if (type_mask == 1)
			type = "World";
		else if (type_mask == 3)
			type = "NPC";
		else if (type_mask == 4)
			type = "Pet";
		else if (type_mask == 5)
			type = "Vehicle";
		std::cout << tmp->getname() << " (" << type << "): ";
		unsigned long totaldamage = tmp->gettotaldamage();
		globaldamage += totaldamage;
		unsigned long totalhealing = tmp->gettotalhealing();
		globalhealing += totalhealing;
		double secs = tmp->gettotaltime().total_milliseconds() / 1000.0;
		if (totaldamage > 0)
			std::cout << totaldamage << " dmg dealt over " << secs << " seconds (" << totaldamage / secs << " DPS) ";
		if (totaldamage > 0 && totalhealing > 0)
			std::cout << ", ";
		if (totalhealing > 0)
			std::cout << totalhealing << " healing done (" << totalhealing / secs << " HPS) ";
		std::cout << std::endl;

		// for each source, iterate through all the destination targets
		destinationmap& destinations = tmp->getdestinations();
		destinationiter destination_end = destinations.end();
		for (destinationiter iter2 = destinations.begin(); iter2 != destination_end; ++iter2)
		{
			const destinationstats_ptr desttmp = iter2->second;
			type_mask = (desttmp->getid() & 0x0070000000000000) >> 52;
			type = "Unknown";
			if (type_mask == 0)
				type = "Player";
			else if (type_mask == 1)
				type = "World";
			else if (type_mask == 3)
				type = "NPC";
			else if (type_mask == 4)
				type = "Pet";
			else if (type_mask == 5)
				type = "Vehicle";
			std::cout << "\t" << desttmp->getname() << " (" <<  type << "): ";
			totaldamage = desttmp->gettotaldamage();
			totalhealing = desttmp->gettotalhealing();
			secs = desttmp->gettotaltime().total_milliseconds() / 1000.0;
			if (totaldamage > 0)
				std::cout << totaldamage << " dmg taken over " << secs << " seconds (" << totaldamage / secs << " DPS) ";
			if (totalhealing > 0)
				std::cout << totalhealing << " healing received (" << totalhealing / secs << " HPS) ";
			std::cout << std::endl;

			// now we iterate through all the attack/healing types from source -> destination
			attackvector& attacks = desttmp->getattacks();
			attackiter iter3 = attacks.begin();
			attackiter attack_end = attacks.end();
			while (iter3 != attack_end)
			{
				const attackstats_ptr atktmp = *iter3++;
				totaldamage = atktmp->gettotaldamage();
				totalhealing = atktmp->gettotalhealing();
				unsigned long spelldamage = atktmp->getspelldamage();
				unsigned long spellperiodicdamage = atktmp->getspellperiodicdamage();
				unsigned long spellheal = atktmp->getspellheal();
				unsigned long spellperiodicheal = atktmp->getspellperiodicheal();
				unsigned long spelloverheal = atktmp->getspelloverheal();
				unsigned long swingdamage = atktmp->getswingdamage();
				unsigned long rangedamage = atktmp->getrangedamage();
				unsigned int ticks = atktmp->getticks();
				unsigned int crits = atktmp->getcrits();
				unsigned int periodiccrits = atktmp->getperiodiccrits();
				unsigned int healticks = atktmp->gethealticks();
				unsigned int swinghits = atktmp->getswinghits();
				unsigned int rangehits = atktmp->getrangehits();
				unsigned int spellhits = atktmp->getspellhits();
				unsigned int healhits = atktmp->gethealhits();
				unsigned int missed = atktmp->getmissed();
				unsigned int dodged = atktmp->getdodged();
				unsigned int blocked = atktmp->getblocked();
				unsigned int parried = atktmp->getparried();
				unsigned int absorbed = atktmp->getabsorbed();
				unsigned int immune = atktmp->getimmune();
				unsigned int resisted = atktmp->getresisted();
				unsigned int reflected = atktmp->getreflected();
				unsigned int evaded = atktmp->getevaded();
				std::cout << "\t\t" << atktmp->getname() << ": ";
				if (totaldamage)
					std::cout << totaldamage << " total dmg";
				if (totalhealing)
					std::cout << totalhealing << " total healing";
				if (spellhits)
				{
					std::cout << " - " << spelldamage << " spell dmg, " << spellhits << " hit(s), ";
					if (crits)
						std::cout << crits << " crit(s) (" << crits * 100.0 / spellhits << "%), ";
					std::cout << spelldamage / spellhits << " avg";
				}
				if (healhits)
				{
					std::cout << " - " << spellheal << " heal amt, " << healhits << " hit(s), ";
					if (crits)
						std::cout << crits << " crits(s) (" << crits * 100.0 / healhits << "%), ";
					std::cout << spellheal / healhits << " avg";
				}
				if (ticks)
				{
					std::cout << " - " << spellperiodicdamage << " DoT dmg, " << ticks << " tick(s), ";
					if (periodiccrits)
						std::cout << periodiccrits << " crits(s) (" << periodiccrits * 100.0 / ticks << "%), ";
					std::cout << spellperiodicdamage / ticks << " avg";
				}
				if (healticks)
				{
					// note: HoTs cannot crit, so no need to check
					std::cout << " - " << spellperiodicheal << " HoT amt, " << healticks << " tick(s), " << spellperiodicheal / healticks << " avg";
				}
				if (spelloverheal)
					std::cout << ", " << spelloverheal << " overhealing (" << spelloverheal * 100.0 / totalhealing << "%)";
				if (swinghits)
				{
					std::cout << " - " << swingdamage << " swing dmg, " << swinghits << " hit(s), ";
					if (crits)
						std::cout << crits << " crits(s), ";
					std::cout << swingdamage / swinghits << " avg";
				}
				if (rangehits)
				{
					std::cout << " - " << rangedamage << " range dmg, " << rangehits << " hit(s), ";
					if (crits)
						std::cout << crits << " crits(s), ";
					std::cout << rangedamage / rangehits << " avg";
				}
				if (missed)
					std::cout << " - " << missed << " missed";
				if (dodged)
					std::cout << " - " << dodged << " dodged";
				if (blocked)
					std::cout << " - " << blocked << " blocked";
				if (parried)
					std::cout << " - " << parried << " parried";
				if (absorbed)
					std::cout << " - " << absorbed << " absorbed";
				if (immune)
					std::cout << " - " << immune << " immune";
				if (resisted > 0)
					std::cout << " - " << resisted << " resisted";
				if (reflected > 0)
					std::cout << " - " << reflected << " reflected";
				if (evaded > 0)
					std::cout << " - " << evaded << " evaded";
				std::cout << std::endl;
			}
		}
	}

	// build arrays for damage and healing data
	std::vector<sourcestats_ptr> damage_vec;
	std::vector<sourcestats_ptr> healing_vec;
	source_end = sources.end();
	for (sourceiter iter = sources.begin(); iter != source_end; ++iter)
	{
		const sourcestats_ptr tmp = iter->second;
		if (tmp->gettotaldamage() > 0 && (tmp->getid() & 0x0070000000000000) == 0) // only care about player damage)
			damage_vec.push_back(iter->second);
		if (tmp->gettotalhealing() > 0 && (tmp->getid() & 0x0070000000000000) == 0) // only care about player healing
			healing_vec.push_back(iter->second);
	}

	// if we have multiple sources, dump out an overall raid chart
	std::string damagedata, damagelabel;
	if (damage_vec.size() > 1)
	{
		// sort damage so chart is easy to read
		std::sort(damage_vec.begin(), damage_vec.end(), compare_damage());

		// loop through damage sources
		std::vector<sourcestats_ptr>::const_iterator p = damage_vec.begin();
		while (p != damage_vec.end())
		{
			// build damage chart info
			const sourcestats_ptr tmp = *p;
			char buf[256], buf2[256];
			if (damagedata.size() == 0)
				sprintf(buf, "%0.2f", tmp->gettotaldamage() * 100 / (double) globaldamage);
			else
				sprintf(buf, ",%0.2f", tmp->gettotaldamage() * 100 / (double) globaldamage);
			damagedata += buf;
			sprintf(buf, "%0.2f", tmp->gettotaldamage() * 100 / (double) globaldamage);
			if (damagelabel.size() == 0)
				sprintf(buf2, "%s%%20(%s%%)", tmp->getname().c_str(), buf);
			else
				sprintf(buf2, "|%s%%20(%s%%)", tmp->getname().c_str(), buf);
			damagelabel += buf2;
			p++;
		}
	}

	// if only one source, we'll throw in a chart for damage sources
	std::string dmgsrcdata, dmgsrclabel;
	std::map<std::string, unsigned long> dmgsrcmap;
	if (damage_vec.size() == 1)
	{
		std::vector<sourcestats_ptr>::const_iterator p = damage_vec.begin();
		const sourcestats_ptr tmp = *p;
		destinationmap& destinations = tmp->getdestinations();
		unsigned long totaldamage = 0;
		for (destinationiter iter = destinations.begin(); iter != destinations.end(); iter++)
		{
			const destinationstats_ptr desttmp = iter->second;
			attackvector& attacks = desttmp->getattacks();
			attackiter iter2 = attacks.begin();
			while (iter2 != attacks.end())
			{
				const attackstats_ptr atktmp = *iter2++;
				unsigned long damage = atktmp->gettotaldamage();
				if (damage > 0)
				{
					dmgsrcmap[atktmp->getname()] += damage;
					totaldamage += damage;
				}
			}
		}
		for (std::map<std::string, unsigned long>::const_iterator dmgsrciter = dmgsrcmap.begin(); dmgsrciter != dmgsrcmap.end(); ++dmgsrciter)
		{
			char buf[256], buf2[256];
			if (dmgsrcdata.size() == 0)
				sprintf(buf, "%0.2f", dmgsrciter->second * 100 / (double) totaldamage);
			else
				sprintf(buf, ",%0.2f", dmgsrciter->second * 100 / (double) totaldamage);
			dmgsrcdata += buf;
			sprintf(buf, "%0.2f", dmgsrciter->second * 100 / (double) totaldamage);
			if (dmgsrclabel.size() == 0)
				sprintf(buf2, "%s%%20(%s%%)", dmgsrciter->first.c_str(), buf);
			else
				sprintf(buf2, "|%s%%20(%s%%)", dmgsrciter->first.c_str(), buf);
			dmgsrclabel += buf2;
		}
		std::cout << std::endl << "Use the following URI for a damage breakdown by effect:" << std::endl;
		std::cout << "http://chart.apis.google.com/chart?chtt=Damage%20-%20" << tmp->getname() << "&chts=FF0000&cht=p&chs=680x400&chd=t%3A";
		std::string labelfixup;
		for (std::string::const_iterator striter = dmgsrclabel.begin(); striter != dmgsrclabel.end(); ++striter)
		{
			if (*striter == ' ')
				labelfixup += "%20";
			else
				labelfixup += *striter;
		}
		std::cout << dmgsrcdata << "&chl=" << labelfixup << std::endl;
	}

	// if only one source, we'll throw in a chart for healing
	std::string healsrcdata, healsrclabel;
	std::map<std::string, unsigned long> healsrcmap;
	if (healing_vec.size() == 1)
	{
		std::vector<sourcestats_ptr>::const_iterator p = healing_vec.begin();
		const sourcestats_ptr tmp = *p;
		destinationmap& destinations = tmp->getdestinations();
		unsigned long totalhealing = 0;
		for (destinationiter iter = destinations.begin(); iter != destinations.end(); iter++)
		{
			const destinationstats_ptr desttmp = iter->second;
			attackvector& attacks = desttmp->getattacks();
			attackiter iter2 = attacks.begin();
			while (iter2 != attacks.end())
			{
				const attackstats_ptr atktmp = *iter2++;
				unsigned long healing = atktmp->gettotalhealing();
				if (healing > 0)
				{
					healsrcmap[atktmp->getname()] += healing;
					totalhealing += healing;
				}
			}
		}
		for (std::map<std::string, unsigned long>::const_iterator healsrciter = healsrcmap.begin(); healsrciter != healsrcmap.end(); ++healsrciter)
		{
			char buf[256], buf2[256];
			if (healsrcdata.size() == 0)
				sprintf(buf, "%0.2f", healsrciter->second * 100 / (double) totalhealing);
			else
				sprintf(buf, ",%0.2f", healsrciter->second * 100 / (double) totalhealing);
			healsrcdata += buf;
			sprintf(buf, "%0.2f", healsrciter->second * 100 / (double) totalhealing);
			if (healsrclabel.size() == 0)
				sprintf(buf2, "%s%%20(%s%%)", healsrciter->first.c_str(), buf);
			else
				sprintf(buf2, "|%s%%20(%s%%)", healsrciter->first.c_str(), buf);
			healsrclabel += buf2;
		}
		std::cout << std::endl << "Use the following URI for a healing breakdown by effect:" << std::endl;
		std::cout << "http://chart.apis.google.com/chart?chtt=Healing%20-%20" << tmp->getname() << "&chts=0000FF&cht=p&chs=680x400&chd=t%3A";
		std::string labelfixup;
		for (std::string::const_iterator striter = healsrclabel.begin(); striter != healsrclabel.end(); ++striter)
		{
			if (*striter == ' ')
				labelfixup += "%20";
			else
				labelfixup += *striter;
		}
		std::cout << healsrcdata << "&chl=" << labelfixup << std::endl;
	}

	std::string healingdata, healinglabel;
	if (healing_vec.size() > 1)
	{
		// sort healing info
		std::sort(healing_vec.begin(), healing_vec.end(), compare_healing());

		// loop through healing sources
		std::vector<sourcestats_ptr>::const_iterator p = healing_vec.begin();
		while (p != healing_vec.end())
		{
			// build healing chart info
			const sourcestats_ptr tmp = *p;
			char buf[256], buf2[256];
			if (healingdata.size() == 0)
				sprintf(buf, "%0.2f", tmp->gettotalhealing() * 100 / (double) globalhealing);
			else
				sprintf(buf, ",%0.2f", tmp->gettotalhealing() * 100 / (double) globalhealing);
			healingdata += buf;
			sprintf(buf, "%0.2f", tmp->gettotalhealing() * 100 / (double) globalhealing);
			if (healinglabel.size() == 0)
				sprintf(buf2, "%s%%20(%s%%)", tmp->getname().c_str(), buf);
			else
				sprintf(buf2, "|%s%%20(%s%%)", tmp->getname().c_str(), buf);
			healinglabel += buf2;
			p++;
		}
	}

	// for a visual, we dump out a URI for a google chart
	if (damage_vec.size() > 1)
	{
		std::string damagechart = "http://chart.apis.google.com/chart?";
		if (destination.length() == 0)
			damagechart += "chtt=Total%20Damage";
		else
			damagechart += "chtt=Damage%20-%20" + destination;
		damagechart += "&chts=FF0000&cht=p&chs=680x400&chd=t%3A" + damagedata + "&chl=" + damagelabel;
		std::cout << std::endl << "Use the following URI for an overall damage chart:" << std::endl << damagechart << std::endl;
	}
	if (healing_vec.size() > 1)
	{
		std::string healingchart = "http://chart.apis.google.com/chart?";
		if (destination.length() == 0)
			healingchart += "chtt=Total%20Healing";
		else
			healingchart += "chtt=Healing%20-%20" + destination;
		healingchart += "&chts=0000FF&cht=p&chs=680x400&chd=t%3A" + healingdata + "&chl=" + healinglabel;
		std::cout << std::endl << "Use the following URI for an overall healing chart:" << std::endl << healingchart << std::endl;
	}

	// parser timing
	std::cout << std::endl << linecount << " total lines, " << lineparsedcount << " lines parsed in " << elapsed.total_milliseconds() << "ms" << std::endl;

	return 0;
}

