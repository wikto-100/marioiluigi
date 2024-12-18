// mcts.i
%module mcts

%{
#include "MCTS.hpp"
%}

// Include SWIG's standard library interfaces for std::string and std::vector
%include "std_string.i"
%include "std_vector.i"

// Define a SWIG template for std::vector<std::string>
%template(StringVector) std::vector<std::string>;

// Since all methods except get_best_move are private or not exposed,
// and debug_print_tree is commented out, no need to ignore additional methods.

// Include the MCTS class definition
%include "MCTS.hpp"
