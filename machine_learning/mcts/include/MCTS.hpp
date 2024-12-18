#pragma once
#include <vector>
#include <string>
#include <random>
#include <functional>
#include <iostream>
#include "chess_lib.hpp"

class MCTS
{
private:
    static size_t _get_random_index(std::mt19937 &gen, int min, int max);

    size_t BRANCHING_FACTOR;
    const size_t MAX_DEPTH;
    std::random_device rd;
    std::mt19937 gen;

    struct Node
    {
        Node *parent;
        std::vector<Node *> children;
        int wins;
        int losses;
        int visits;
        int depth;
        std::string move;
        std::string fen;

        inline int q() const { return wins - losses; }
        inline bool is_leaf() const { return children.empty(); }
        inline bool turn() const { return depth % 2 == 0; }

        Node(Node *p = nullptr, const std::string &m = "", const std::string &f = "")
            : parent(p), wins(0), losses(0), visits(0), move(m), fen(f)
        {
            depth = parent ? parent->depth + 1 : 0;
        }
    };

    Node *root;

    // Changed parameters to const references where applicable
    Node *add_child(Node *parent, const std::string &move, const std::string &fen);
    Node *select(Node *node);
    Node *expand(Node *node);
    void rollout(Node *node);
    void backpropagate(Node *node);
    void run(int iterations);
    float ucb(const Node *node) const;

public:
    // Constructor and Destructor
    MCTS(const std::string &starting_fen, const std::vector<std::string> &root_moves, size_t branching_factor, size_t max_depth);
    ~MCTS();

   //void debug_print_tree() const;
    std::string get_best_move(int iterations);
};
