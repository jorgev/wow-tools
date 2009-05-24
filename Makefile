wowparse: wowparse.o
	g++ wowparse.o -Wall -L/opt/local/lib -lboost_program_options-mt -lboost_date_time-mt -o wowparse -g

wowparse.o: wowparse.cc
	g++  -I/opt/local/include -c wowparse.cc -Wall -g
