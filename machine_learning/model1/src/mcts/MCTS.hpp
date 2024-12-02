#pragma once
#include <vector>
#include <string>
// problem 1: select node starting from root
// problem 2: simulate playouts from selected node
// problem 3: expand tree from selected node
// problem 4: backpropagate on path from selected node
class MCTS
{
private:
    struct Node
    {
        Node *parent;
        std::vector<Node *> children;
        int wins;
        int visits;
        std::string move;
        std::string fen;
    };
    Node *root;
    Node *add_child(Node *parent, std::string move, std::string fen);
    Node *select(Node *node);
    Node *expand(Node *node);
    Node *simulate(Node *node);
    void backpropagate(Node *node, int result);
public:
    MCTS(std::vector<std::string> legal_moves);
    std::string get_best_move();
    ~MCTS();
};

