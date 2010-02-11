// wowtail.cc - tails the log file and prints interesting info

#include <string>
#include <iostream>
#include <sstream>
#include <vector>

int main(int argc, char** argv)
{
	char line[1024];

	while (std::cin.getline(line, 1024))
	{
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
		unsigned int srcflags, dstflags, amount;
		action = fields[0];
		std::istringstream is(fields[1]);
		is >> srcguid;
		srcname = fields[2];
		is.str(fields[3]);
		is >> srcflags;
		is.str(fields[4]);
		is >> dstguid;
		dstname = fields[5];
		is.str(fields[6]);
		is >> dstflags;
		result = fields[7];
		effect = fields[8];
		ph = fields[9];
		is.str(fields[10]);
		is >> amount;
	}

	return 0;
}

