// wowtail.cc - tails the log file and prints interesting info

#include <string>
#include <iostream>

int main(int argc, char** argv)
{
	std::string line;

	while (1)
	{
		std::getline(std::cin, line);
		std::cout << line << std::endl;
	}

	return 0;
}

