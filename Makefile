CC=g++
INC=

CFLAGS=-c -Wall -std=c++0x -O2
LDFLAGS=

SOURCES := $(wildcard src/*.cpp)
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=faultsim

all: $(EXECUTABLE) doc

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(OBJECTS) $(LDFLAGS) -lboost_program_options -o $@

.cpp.o:
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -rf faultsim
	rm -rf src/*.o

doc:
	cd doc && make || true

