wowparse: wowparse.o
	g++ wowparse.o -Wall -L/usr/local/lib -lboost_program_options-xgcc40-mt -lboost_date_time-xgcc40-mt -o wowparse -g

wowparse.o: wowparse.cc
	g++  -I/usr/local/include/boost-1_38 -c wowparse.cc -Wall -g
