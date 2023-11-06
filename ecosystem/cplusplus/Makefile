SOURCES     = $(wildcard *.cpp)
EXECUTABLE  = simulator

CXX         = g++

#Default Flags (we prefer -std=c++17 but Mac/Xcode/Clang doesn't support)
CXXFLAGS = -std=c++17 -Wconversion -Wall -Werror -Wextra -pedantic -pthread


release: CXXFLAGS += -O3 -DNDEBUG
release: $(CXX) $(CXXFLAGS) $(SOURCES) -o $(EXECUTABLE)


debug: CXXFLAGS += -g3 -DDEBUG
debug:
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(EXECUTABLE)_debug

