// src/testmcts.cpp
#include "MCTS.hpp"
#include "chess_lib.hpp"
#include <iostream>

int main()
{
    std::string fen = "k7/8/1K6/8/8/4R3/8/8 w - - 0 1";
    std::vector<std::string> root_moves = chess_lib::getAvailableMoves(fen);
    MCTS mcts(fen, root_moves, root_moves.size(), 1);
    std::string best_move = mcts.get_best_move(1000);
    std::cout << "Best move: " << best_move << std::endl;
    return 0;
}
