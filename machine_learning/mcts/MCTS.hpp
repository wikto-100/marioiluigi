#pragma once
#include <vector>
#include <string>
#include <random>
#include <functional>
#include <iostream>
#include <cmath>
#include <algorithm>
#include "chess_lib.hpp"

class MCTS
{
private:
    // --- Types & Data ---
    struct Node
    {
        Node *parent;
        std::vector<Node *> children; 
        // In a standard partial-expansion scheme, we track which moves remain unexpanded:
        std::vector<std::string> unexpanded_moves;

        int wins;
        int losses;
        int visits;
        int depth;
        std::string move;
        std::string fen;

        // Constructor
        Node(Node *p, const std::string &m, const std::string &f)
            : parent(p), wins(0), losses(0), visits(0), move(m), fen(f)
        {
            // Depth is parent's depth + 1, or 0 if no parent
            depth = parent ? parent->depth + 1 : 0;
        }

        // Helper methods
        inline int q() const { return wins - losses; }
        inline bool is_leaf() const { return children.empty() && unexpanded_moves.empty(); }
        // If depth is even, it's the same side’s turn as the root; if odd, the other side.
        inline bool turn() const { return (depth % 2) == 0; }
    };

    Node *root;

    // Fields from the constructor
    size_t BRANCHING_FACTOR;
    const size_t MAX_DEPTH;

    // RNG
    std::random_device rd;
    std::mt19937 gen;

    // --- MCTS Subroutines ---
    static size_t _get_random_index(std::mt19937 &gen, int min, int max);
    
    float ucb(const Node *node) const;
    Node* select_node(Node *node);
    Node* expand(Node *node);
    void  rollout(Node *node);
    void  backpropagate(Node *node);
    void  run(int iterations);

    // Utility
    Node* add_child(Node *parent, const std::string &move, const std::string &fen);
    bool  is_terminal(const Node *node) const;

public:
    // --- Public Interface ---
    MCTS(const std::string &starting_fen,
         const std::vector<std::string> &root_moves,
         size_t branching_factor,
         size_t max_depth);

    ~MCTS();

    // Run MCTS and return best move
    std::string get_best_move(int iterations);
};
