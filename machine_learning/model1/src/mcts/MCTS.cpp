#include "MCTS.hpp"
#include "chess_lib.hpp"
MCTS::MCTS(std::vector<std::string> legal_moves)
{
    // need to initialize the root node
    root = MCTS::add_child(nullptr, "", "");
    // for every legal move from the root(use chess library to get legal moves)
    // add a child node to the root
    // do that by calling add_child recursively. problem: apply move to modify fen state (use chess library)
    // okay so 1. get legal moves 2. apply move (modify internal fen state) 3. add child node 4. repeat until depth is reached
    // problem: when is leaf reached? when depth is reached or when no more legal moves?
}
MCTS::Node* MCTS::add_child(Node *parent, std::string move, std::string fen)
{
    Node *child = new Node();
    child->parent = parent;
    child->wins = 0;
    child->visits = 0;
    child->move = move;
    child->fen = fen;
    parent->children.push_back(child);
    return child;
}

MCTS::~MCTS()
{

}