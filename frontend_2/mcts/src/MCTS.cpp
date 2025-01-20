#include "MCTS.hpp"
#include <cmath>
#include <algorithm>

inline size_t MCTS::_get_random_index(std::mt19937 &gen, int min, int max)
{
    std::uniform_int_distribution<> distr(min, max);
    return distr(gen);
}

MCTS::MCTS(const std::string &starting_fen, const std::vector<std::string> &root_moves, size_t branching_factor, size_t max_depth)
    : BRANCHING_FACTOR(std::min(branching_factor, root_moves.size())),
      MAX_DEPTH(max_depth),
      gen(rd())
{
    // Create the root node
    root = new Node(nullptr, "", starting_fen);
    // Add child nodes for each possible move
    size_t child_ctr = 0;
    for (const auto &move : root_moves) // Use const reference
    {
        add_child(root, move, chess_lib::getAppliedMove(starting_fen, move));
        if (++child_ctr >= BRANCHING_FACTOR)
        {
            break;
        }
    }
}

MCTS::~MCTS()
{
    // Delete all nodes in the tree
    std::function<void(Node *)> delete_tree = [&](Node *node)
    {
        for (Node *child : node->children)
        {
            delete_tree(child);
        }
        delete node;
    };

    delete_tree(root);
}

MCTS::Node *MCTS::add_child(Node *parent, const std::string &move, const std::string &fen)
{
    // Create a new node and add it to the parent's children
    Node *child = new Node(parent, move, fen);
    parent->children.emplace_back(child); // Use emplace_back for efficiency
    return child;
}

float MCTS::ucb(const Node *node) const
{
    // UCB1 formula
    if (node->visits == 0)
        return std::numeric_limits<float>::infinity();
    if (node->parent == nullptr)
        return static_cast<float>(node->q()) / node->visits;

    return (static_cast<float>(node->q()) / node->visits) + 1.41f * std::sqrt(std::log(node->parent->visits) / node->visits);
}

MCTS::Node *MCTS::select(Node *node)
{
    // Traverse the tree until a leaf node is reached
    while (!node->is_leaf())
    {
        // Select the child node with the highest UCB value
        node = *std::max_element(node->children.begin(), node->children.end(),
                                 [this](const Node *a, const Node *b) -> bool
                                 { return ucb(a) < ucb(b); });
    }

    return node;
}

MCTS::Node *MCTS::expand(Node *leaf)
{
    // Expand branching factor nodes of untried actions
    if (!leaf->is_leaf())
    {
        std::cerr << "Node is not a leaf" << std::endl;
        return nullptr;
    }
    std::vector<std::string> moves = chess_lib::getAvailableMoves(leaf->fen);
    if (moves.empty())
    {
        return leaf;
    }
    for (const auto &move : moves) // Use const reference
    {
        add_child(leaf, move, chess_lib::getAppliedMove(leaf->fen, move));
    }
    return leaf;
}

void MCTS::rollout(Node *leaf)
{
    if (!leaf->is_leaf())
    {
        std::cerr << "Node is not a leaf" << std::endl;
        return;
    }
    // Simulate a game from the current node
    std::string current_fen = leaf->fen;
    size_t sim_depth = 0;
    while (sim_depth < MAX_DEPTH && !chess_lib::isLostCondition(current_fen))
    {
        // Get available moves
        // Instead sample a branching factor amount of moves, randomly
        // also make the branching factor larger as the game progresses
        const std::vector<std::string> moves = chess_lib::getAvailableMoves(current_fen);
        if (moves.empty())
        {
            // No moves available, game is a draw
            break;
        }
        // the chance of getting checkmate with some random move is very low
        // we can replace this with a heuristic to make the simulation have a bit more sense
        size_t move_index = _get_random_index(gen, 0, static_cast<int>(moves.size() - 1));
        const std::string &random_move = moves.at(move_index);

        // Select a random move
        try
        {
            current_fen = chess_lib::getAppliedMove(current_fen, random_move);
        }
        catch (const std::exception &e)
        {
            std::cout << "Exception on rand move apply: " << e.what() << std::endl;
            std::cout << "Tried to apply move: " << random_move << " in position " << current_fen << std::endl;
        }
        sim_depth++;
    }
    if (chess_lib::isLostCondition(current_fen))
    {
        bool isWin = (leaf->turn() && (sim_depth % 2 != 0)) || (!leaf->turn() && (sim_depth % 2 == 0));

        if (isWin)
        {
            leaf->wins = 1;
        }
        else
        {
            leaf->losses = 1;
        }
    }
}

void MCTS::backpropagate(Node *node)
{
    int wins = node->wins;
    int losses = node->losses;
    while (node != nullptr)
    {
        node->visits++;
        if (!node->is_leaf())
        {
            node->wins += wins;
            node->losses += losses;
        }

        node = node->parent;
    }
}

void MCTS::run(int iterations)
{
    for (int i = 0; i < iterations; ++i)
    {
        Node *selected_node = select(root);
        Node *expanded_node = expand(selected_node);
        for (Node *child : expanded_node->children)
        {
            rollout(child);
            backpropagate(child);
        }
    }
}

std::string MCTS::get_best_move(int iterations)
{
    run(iterations);
    // Select the child node with the highest number of visits
    Node *best_node = *std::max_element(root->children.begin(), root->children.end(),
                                        [this](const Node *a, const Node *b) -> bool
                                        {
                                            // Only consider nodes that were visited at least once
                                            if (a->visits == 0 || b->visits == 0)
                                                return false;
                                            return ucb(a) < ucb(b);
                                        });

    return best_node->move;
}
/*
void MCTS::debug_print_tree() const
{
    // Print the tree structure starting from the root node
    std::function<void(const Node *, int)> print_tree = [&](const Node *node, int depth) -> void
    {
        for (int i = 0; i < depth; ++i)
        {
            std::cout << "  ";
        }
        std::cout << "Move: " << node->move
                  << " Fen: " << node->fen
                  << " Wins: " << node->wins
                  << " Losses: " << node->losses
                  << " Visits: " << node->visits << std::endl;
        for (const Node *child : node->children)
        {
            print_tree(child, depth + 1);
        }
    };

    print_tree(root, 0);
}
*/