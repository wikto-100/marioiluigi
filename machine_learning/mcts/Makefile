# Makefile

# ------------------------------------------------------------------------------
# Tools and Flags
CXX        = g++
SWIG       = swig

BUILD_DIR  = build

# Include local . so we can #include "MCTS.hpp" without a path,
# plus engine/chess_lib/cpp_headers/ so we can #include "chess_lib.hpp".
CXXFLAGS   = -std=c++17 -O3 -Wall -Wextra -I. -I../../engine/chess_lib/cpp_headers -fPIC

# SWIG: point to current dir and engine headers
SWIGFLAGS  = -c++ -python -I. -I../../engine/chess_lib/cpp_headers

# Python dev flags (Arch has Python.h in /usr/include/python3.X)
PYTHON_INCLUDE = $(shell python3-config --includes)
PYTHON_LIB     = $(shell python3-config --ldflags)

# Rust build output directory
LIB_DIR    = ../../engine/chess_lib/target/release

# Linker flags: link directly with Rust's static library
LDFLAGS_EXEC   = -L$(LIB_DIR) -lchess_lib -lm
LDFLAGS_SHARED = -L$(LIB_DIR) -lchess_lib -lm

# ------------------------------------------------------------------------------
# Source Files
SRC_DIR     = src

# Local MCTS sources for the executable
MCTS_SOURCES  = $(SRC_DIR)/testmcts.cpp \
                $(SRC_DIR)/MCTS.cpp
MCTS_OBJECTS  = $(MCTS_SOURCES:%.cpp=$(BUILD_DIR)/%.o)

# Engine's external chess_lib wrapper
ENGINE_CHESS_LIB_CPP = ../../engine/chess_lib/cpp_headers/chess_lib.cpp
ENGINE_CHESS_LIB_OBJ = $(BUILD_DIR)/chess_lib.o

# ------------------------------------------------------------------------------
# Final Executable
EXEC_OBJ    = $(MCTS_OBJECTS) $(ENGINE_CHESS_LIB_OBJ)
EXEC_TARGET = $(BUILD_DIR)/mcts

# ------------------------------------------------------------------------------
# SWIG: interface + generated wrappers
SWIG_INTERFACE = mcts.i
SWIG_WRAP      = mcts_wrap.cxx
SWIG_PY        = mcts.py

# Compile SWIG wrapper into an object file with Python includes
WRAP_OBJ       = $(BUILD_DIR)/mcts_wrap.o

# ------------------------------------------------------------------------------
# Build the shared library (Python module):
# We'll link these object files:
# 1) mcts_wrap.o  (SWIG wrapper, compiled with Python includes)
# 2) MCTS.o       (from src/MCTS.cpp)
# 3) chess_lib.o  (from engine's chess_lib.cpp)
SHARED_OBJ = $(WRAP_OBJ) \
             $(BUILD_DIR)/src/MCTS.o \
             $(ENGINE_CHESS_LIB_OBJ)

SHARED_LIB = _mcts.so

# ------------------------------------------------------------------------------
# Default target: build the executable
all: $(EXEC_TARGET)

# 1) Ensure the Rust library is built first
rustlib:
	@echo "[Makefile] Building Rust library via just..."
	cd ../../engine/chess_lib && just build_cpp_api_release

# 2) Build the executable (depends on Rust library + object files)
$(EXEC_TARGET): rustlib $(EXEC_OBJ)
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(EXEC_OBJ) $(CXXFLAGS) $(LDFLAGS_EXEC) -o $(EXEC_TARGET)

# ------------------------------------------------------------------------------
# Pattern rule for local MCTS .cpp -> .o
$(BUILD_DIR)/%.o: %.cpp
	@mkdir -p $(dir $@)
	$(CXX) -c $(CXXFLAGS) $(PYTHON_INCLUDE) $< -o $@

# ------------------------------------------------------------------------------
# Explicit rule for building engine/chess_lib.cpp -> chess_lib.o
$(ENGINE_CHESS_LIB_OBJ): $(ENGINE_CHESS_LIB_CPP)
	@mkdir -p $(dir $@)
	$(CXX) -c $(CXXFLAGS) $(PYTHON_INCLUDE) $< -o $@

# ------------------------------------------------------------------------------
# SWIG steps
$(SWIG_WRAP) $(SWIG_PY): $(SWIG_INTERFACE) MCTS.hpp
	$(SWIG) $(SWIGFLAGS) $(SWIG_INTERFACE)

# Compile the SWIG wrapper into an object file with the correct Python includes
$(WRAP_OBJ): $(SWIG_WRAP)
	@mkdir -p $(dir $@)
	$(CXX) -c $(CXXFLAGS) $(PYTHON_INCLUDE) $(SWIG_WRAP) -o $@

# ------------------------------------------------------------------------------
# Build the shared library (Python module)
$(SHARED_LIB): rustlib $(SHARED_OBJ)
	@mkdir -p $(BUILD_DIR)
	$(CXX) -shared $(SHARED_OBJ) $(CXXFLAGS) $(PYTHON_LIB) $(LDFLAGS_SHARED) -o $(SHARED_LIB)

# Provide a "shared" target to build _mcts.so
shared: $(SHARED_LIB)

# ------------------------------------------------------------------------------
# Cleanup
clean:
	rm -f \
		$(EXEC_TARGET) \
		$(BUILD_DIR)/*.o \
		$(BUILD_DIR)/*/*.o \
		$(SWIG_WRAP) \
		$(SWIG_PY) \
		$(SHARED_LIB)

.PHONY: all clean shared rustlib
