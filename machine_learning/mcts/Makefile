# Makefile

# Compiler and Tools
CXX = g++
SWIG = swig

# Compiler Flags
CXXFLAGS = -std=c++17 -O3 -Wall -Wextra -Iinclude -fPIC

# SWIG Flags
SWIGFLAGS = -c++ -python -Iinclude

# Linker Flags
LDFLAGS_EXEC = -Llib -lchess_lib -lm
LDFLAGS_SHARED = -Llib -lchess_lib -lm

# Python Configuration
PYTHON_INCLUDE = $(shell python3-config --includes)
PYTHON_LIB = $(shell python3-config --ldflags)

# Directories
SRC_DIR = src
BUILD_DIR = build
INCLUDE_DIR = include
LIB_DIR = lib

# Source Files for Executable
EXEC_SRC = $(SRC_DIR)/testmcts.cpp $(SRC_DIR)/MCTS.cpp $(SRC_DIR)/chess_lib.cpp
EXEC_OBJ = $(EXEC_SRC:$(SRC_DIR)/%.cpp=$(BUILD_DIR)/%.o)
EXEC_TARGET = $(BUILD_DIR)/mcts

# SWIG Interface
SWIG_INTERFACE = mcts.i
SWIG_WRAP = mcts_wrap.cxx
SWIG_PY = mcts.py

# Shared Library
SHARED_LIB = _mcts.so
SHARED_SRC = $(SWIG_WRAP) $(SRC_DIR)/MCTS.cpp
SHARED_OBJ = $(BUILD_DIR)/mcts_wrap.o $(BUILD_DIR)/MCTS.o

# Default Target: Build Executable
all: $(EXEC_TARGET)

# Build Executable
$(EXEC_TARGET): $(EXEC_OBJ) lib/libchess_lib.a
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(EXEC_OBJ) $(CXXFLAGS) $(LDFLAGS_EXEC) -o $(EXEC_TARGET)

# Compile Source Files for Executable
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) -c $(CXXFLAGS) $< -o $@

# SWIG Targets: Generate Wrapper Code
$(SWIG_WRAP) $(SWIG_PY): $(SWIG_INTERFACE) $(INCLUDE_DIR)/MCTS.hpp
	$(SWIG) $(SWIGFLAGS) $(SWIG_INTERFACE)

# Compile SWIG Wrapper
$(BUILD_DIR)/mcts_wrap.o: $(SWIG_WRAP)
	@mkdir -p $(BUILD_DIR)
	$(CXX) -c $(CXXFLAGS) $(PYTHON_INCLUDE) $(SWIG_WRAP) -o $(BUILD_DIR)/mcts_wrap.o

# Compile C++ Sources for Shared Library
$(BUILD_DIR)/MCTS.o: $(SRC_DIR)/MCTS.cpp $(INCLUDE_DIR)/MCTS.hpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) -c $(CXXFLAGS) -I$(INCLUDE_DIR) $(SRC_DIR)/MCTS.cpp -o $(BUILD_DIR)/MCTS.o

# Build the Static Library (Ensure it's built with -fPIC)
lib/libchess_lib.a: build/chess_lib.o
	@mkdir -p lib
	ar rcs lib/libchess_lib.a build/chess_lib.o

# Compile chess_lib.cpp with -fPIC and include all necessary functions
$(BUILD_DIR)/chess_lib.o: $(SRC_DIR)/chess_lib.cpp $(INCLUDE_DIR)/chess_lib.hpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) -c $(CXXFLAGS) -I$(INCLUDE_DIR) $(SRC_DIR)/chess_lib.cpp -o $(BUILD_DIR)/chess_lib.o

# Build Shared Library with SWIG
$(SHARED_LIB): $(SHARED_OBJ) lib/libchess_lib.a
	@mkdir -p $(BUILD_DIR)
	$(CXX) -shared $(SHARED_OBJ) $(CXXFLAGS) $(PYTHON_LIB) $(LDFLAGS_SHARED) -o $(SHARED_LIB)

# Target to Generate and Compile Shared Library
shared: $(SHARED_LIB)

# Clean Build Artifacts
clean:
	rm -f $(EXEC_TARGET) $(BUILD_DIR)/*.o $(SWIG_WRAP) $(SWIG_PY) $(SHARED_LIB) lib/libchess_lib.a

# Phony Targets
.PHONY: all clean shared
