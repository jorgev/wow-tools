wowparse: wowparse.o
	g++ wowparse.o -march=i386 -Wall -lboost_program_options -lboost_date_time -o wowparse -O2

wowparse.o: wowparse.cc
	g++ -c wowparse.cc -march=i386 -Wall -O2
