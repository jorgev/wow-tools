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
#include <time.h>

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
const unsigned int LINESIZE = 1024;

class attackstats
{
public:
	attackstats(std::string& attackname);

	std::string getname() const { return name; }
	void addspelldamage(unsigned long damage) { spellhits++; spelldamage += damage; totaldamage += damage; }
	void addspellperiodicdamage(unsigned long damage) { ticks++; spellperiodicdamage += damage; totaldamage += damage; }
	void addspellheal(unsigned long heal) { healhits++; spellheal += heal; totalhealing += heal; }
	void addspellperiodicheal(unsigned long heal) { healticks++; spellperiodicheal += heal; totalhealing += heal; }
	void addswingdamage(unsigned long damage) { swinghits++; swingdamage += damage; totaldamage += damage; }
	void addrangedamage(unsigned long damage) { rangehits++; rangedamage += damage; totaldamage += damage; }
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
	unsigned long getswingdamage() const { return swingdamage; }
	unsigned long getrangedamage() const { return rangedamage; }
	unsigned long gettotaldamage() const { return totaldamage; }
	unsigned long gettotalhealing() const { return totalhealing; }

private:
	std::string name;
	unsigned int ticks;
	unsigned int healticks;
	unsigned int swinghits;
	unsigned int rangehits;
	unsigned int spellhits;
	unsigned int healhits;
	unsigned int misses;
	unsigned int blocked;
	unsigned int parried;
	unsigned long totaldamage;
	unsigned long totalhealing;
	unsigned long spelldamage;
	unsigned long spellperiodicdamage;
	unsigned long spellheal;
	unsigned long spellperiodicheal;
	unsigned long swingdamage;
	unsigned long rangedamage;
	unsigned long absorbed;
	unsigned long resisted;
	unsigned long immune;
};

attackstats::attackstats(std::string& attackname)
{
	name = attackname;
	ticks = 0;
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
	swingdamage = 0;
	rangedamage = 0;
	absorbed = 0;
	resisted = 0;
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

private:
	std::string name;
	unsigned long long id;
	unsigned long totaldamage;
	unsigned long totalhealing;
	destinationmap destinations;
};

sourcestats::sourcestats(unsigned long long sourceid, std::string& sourcename)
{
	name = sourcename;
	id = sourceid;
	totaldamage = 0;
	totalhealing = 0;
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

	// define the command line arguments that we accept
	po::options_description desc("Program options");
	desc.add_options()
		("help,h", "print usage")
		("input-file,i", po::value<std::string>(), "input file")
		("source,s", po::value<std::string>(), "source")
		("destination,d", po::value<std::string>(), "destination")
	;
	po::variables_map vm;
	po::store(po::parse_command_line(argc, argv, desc), vm);
	po::notify(vm);	

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

	// let the user know what we're doing, to make sure it's what they want
	std::cout << "Parsing file: " << filename << std::endl;
	if (source.length() > 0)
		std::cout << "Filtering on source: " << source << std::endl;
	if (destination.length() > 0)
		std::cout << "Filtering on destination: " << destination << std::endl;
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
	while (ifs.getline(line, LINESIZE))
	{
		// bump line count
		linecount++;

		// double space separates date and combat info
		char* p = strstr(line, "  ");
		if (p == NULL)
			continue;

		// parse the combat data...comma-separated with occasional double-quotes surrounding some fields
		std::vector<const char*> fields;
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

		// put the fields into some meaningful variable names
		std::string action, srcname, dstname, effect, result, ph, result2;
		unsigned long long srcguid, dstguid;
		unsigned short srcflags, dstflags;
		unsigned int amount;
		action = fields[0];
		std::istringstream is(fields[1]);
		is >> std::hex >> srcguid;
		srcname = fields[2];
		is.clear();
		is.str(fields[3]);
		is >> std::hex >> srcflags;
		is.clear();
		is.str(fields[4]);
		is >> std::hex >> dstguid;
		dstname = fields[5];
		is.clear();
		is.str(fields[6]);
		is >> std::hex >> dstflags;
		result = fields[7];
		effect = fields[8];
		ph = fields[9];
		result2 = fields[10];
		is.clear();
		is.str(fields[10]);
		is >> std::dec >> amount;

		// before going any further, check for valid fields
		if (source.length() > 0 && srcname != source)
			continue;
		if (destination.length() > 0 && dstname != destination)
			continue;
		if (srcname == "nil" || dstname == "nil")
			continue;
		
		// log item must be one of these types (this list may change)
		if (action == SPELL_DAMAGE || action == SPELL_PERIODIC_DAMAGE || action == RANGE_DAMAGE || action == SWING_DAMAGE || action == SPELL_HEAL || action == SPELL_PERIODIC_HEAL)
		{
			// time conversion is probably expensive, so we defer it to here...log doesn't give us years, so we need to fix it
			char* slash =  strchr(line, '/');
			if (slash != NULL)
				*slash = '-';
			dt::ptime t = dt::time_from_string(std::string(year) + line);

			// fixup for swing damage, since format is different
			if (action == SWING_DAMAGE)
			{
				effect = "Swing";
				is.clear();
				is.str(result);
				is >> amount;
			}

			// get or create the current source by id
			sourcestats_ptr cursource = sources[srcguid];
			if (cursource == NULL)
			{
				cursource = sourcestats_ptr(new sourcestats(srcguid, srcname));
				sources[srcguid] = cursource;
			}

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
				if ((dstguid & 0x00f0000000000000LL) == 0)
					curdestination->setisplayer();
				destinations[dstguid] = curdestination;
			}

			// update timestamp for dps calculations
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
				attackstats_ptr tmp = *iter3++;
				if (tmp->getname() == effect)
				{
					curattack = tmp;
					break;
				}
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
		}

		// this is the actual # of lines we processed
		lineparsedcount++;
	}

	// dump the stats out
	unsigned long globaldamage = 0;
	unsigned long globalhealing = 0;
	sourceiter source_end = sources.end();
	for (sourceiter iter = sources.begin(); iter != source_end; ++iter)
	{
		// iterate through each source
		const sourcestats_ptr tmp = iter->second;
		std::cout << tmp->getname() << " (0x" << std::uppercase << std::hex << std::setw(16) << std::setfill('0') << tmp->getid() << "): " << std::dec;
		unsigned long totaldamage = tmp->gettotaldamage();
		globaldamage += totaldamage;
		unsigned long totalhealing = tmp->gettotalhealing();
		globalhealing += totalhealing;
		if (totaldamage > 0)
			std::cout << totaldamage << " dmg dealt";
		if (totaldamage > 0 && totalhealing > 0)
			std::cout << ", ";
		if (totalhealing > 0)
			std::cout << totalhealing << " healing done";
		std::cout << std::endl;

		// for each source, iterate through all the destination targets
		destinationmap& destinations = tmp->getdestinations();
		destinationiter destination_end = destinations.end();
		for (destinationiter iter2 = destinations.begin(); iter2 != destination_end; ++iter2)
		{
			const destinationstats_ptr desttmp = iter2->second;
			std::cout << "\t" << desttmp->getname() << " (0x" << std::hex << std::setw(16) << std::setfill('0') << desttmp->getid() << "): " << std::dec;
			totaldamage = desttmp->gettotaldamage();
			totalhealing = desttmp->gettotalhealing();
			double secs = desttmp->gettotaltime().total_milliseconds() / 1000.0;
			if (totaldamage > 0)
				std::cout << totaldamage << " dmg taken over " << secs << " seconds (" << totaldamage / secs << " DPS) ";
			if (totalhealing > 0)
				std::cout << totalhealing << " healing received";
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
				unsigned long swingdamage = atktmp->getswingdamage();
				unsigned long rangedamage = atktmp->getrangedamage();
				unsigned int ticks = atktmp->getticks();
				unsigned int healticks = atktmp->gethealticks();
				unsigned int swinghits = atktmp->getswinghits();
				unsigned int rangehits = atktmp->getrangehits();
				unsigned int spellhits = atktmp->getspellhits();
				unsigned int healhits = atktmp->gethealhits();
				std::cout << "\t\t" << atktmp->getname() << ": ";
				if (totaldamage > 0)
					std::cout << totaldamage << " total dmg";
				if (totalhealing > 0)
					std::cout << totalhealing << " total healing";
				if (spellhits > 0)
					std::cout << " - " << spelldamage << " spell dmg, " << spellhits << (spellhits > 1 ? " hits, " : " hit, ") << spelldamage / spellhits << " avg";
				if (healhits > 0)
					std::cout << " - " << spellheal << " heal amt, " << healhits << (healhits > 1 ? " hits, " : " hit, ") << spellheal / healhits << " avg";
				if (ticks > 0)
					std::cout << " - " << spellperiodicdamage << " DoT dmg, " << ticks << (ticks > 1 ? " ticks, " : " tick, ") << spellperiodicdamage / ticks << " avg";
				if (healticks > 0)
					std::cout << " - " << spellperiodicheal << " HoT amt, " << healticks << (healticks > 1 ? " ticks, " : " tick, ") << spellperiodicheal / healticks << " avg";
				if (swinghits > 0)
					std::cout << " - " << swingdamage << " swing dmg, " << swinghits << (swinghits > 1 ? " hits, " : " hit, ") << swingdamage / swinghits << " avg";
				if (rangehits > 0)
					std::cout << " - " << rangedamage << " range dmg, " << rangehits << (rangehits > 1 ? " hits, " : " hit, ") << rangedamage / rangehits << " avg";
				std::cout << std::endl;
			}
		}
	}

	// some info
	dt::ptime end = dt::microsec_clock::local_time();
	dt::time_duration elapsed = end - start;
	std::cout << std::endl << linecount << " total lines, " << lineparsedcount << " lines parsed in " << elapsed << std::endl;

	// build arrays for damage and healing data
	std::vector<sourcestats_ptr> damage_vec;
	std::vector<sourcestats_ptr> healing_vec;
	source_end = sources.end();
	for (sourceiter iter = sources.begin(); iter != source_end; ++iter)
	{
		const sourcestats_ptr tmp = iter->second;
		if (tmp->gettotaldamage() > 0)
			damage_vec.push_back(iter->second);
		if (tmp->gettotalhealing() > 0 && (tmp->getid() & 0x00f0000000000000LL) == 0) // only care about player healing
			healing_vec.push_back(iter->second);
	}

	// sort damage so chart is easy to read
	std::sort(damage_vec.begin(), damage_vec.end(), compare_damage());

	// loop through damage sources
	std::vector<sourcestats_ptr>::const_iterator p = damage_vec.begin();
	std::string damagedata, damagelabel;
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

	// if only one source, we'll throw in a chart for damage sources
	std::string dmgsrcdata, dmgsrclabel;
	std::map<std::string, unsigned long> dmgsrcmap;
	if (damage_vec.size() == 1)
	{
		p = damage_vec.begin();
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
		for (std::map<std::string, unsigned long>::const_iterator dmgsrciter = dmgsrcmap.begin(); dmgsrciter != dmgsrcmap.end(); dmgsrciter++)
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
		for (std::string::const_iterator striter = dmgsrclabel.begin(); striter != dmgsrclabel.end(); striter++)
		{
			if (*striter == ' ')
				labelfixup += "%20";
			else
				labelfixup += *striter;
		}
		std::cout << dmgsrcdata << "&chl=" << labelfixup << std::endl;
	}

	// sort healing info
	std::sort(healing_vec.begin(), healing_vec.end(), compare_healing());

	// loop through healing sources
	p = healing_vec.begin();
	std::string healingdata, healinglabel;
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

	// for a visual, we dump out a URI for a google chart
	if (damage_vec.size() > 0)
	{
		std::string damagechart = "http://chart.apis.google.com/chart?";
		if (destination.length() == 0)
			damagechart += "chtt=Total%20Damage";
		else
			damagechart += "chtt=Damage%20-%20" + destination;
		damagechart += "&chts=FF0000&cht=p&chs=680x400&chd=t%3A" + damagedata + "&chl=" + damagelabel;
		std::cout << std::endl << "Use the following URI for an overall damage chart:" << std::endl << damagechart << std::endl;
	}
	if (healing_vec.size() > 0)
	{
		std::string healingchart = "http://chart.apis.google.com/chart?";
		if (destination.length() == 0)
			healingchart += "chtt=Total%20Healing";
		else
			healingchart += "chtt=Healing%20-%20" + destination;
		healingchart += "&chts=0000FF&cht=p&chs=680x400&chd=t%3A" + healingdata + "&chl=" + healinglabel;
		std::cout << std::endl << "Use the following URI for an overall healing chart:" << std::endl << healingchart << std::endl;
	}

	return 0;
}

