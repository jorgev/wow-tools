wowparse: wowparse.o
	g++ wowparse.o -Wall -O3 -L/usr/local/lib -lboost_program_options-xgcc40-mt -lboost_date_time-xgcc40-mt -o wowparse

wowparse.o: wowparse.cc
	g++  -I/usr/local/include/boost-1_38 -c wowparse.cc -Wall -O3
