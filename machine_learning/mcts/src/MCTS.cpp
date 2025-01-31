#include "MCTS.hpp"

// -------------------------------------
//  Utility: _get_random_index
// -------------------------------------
size_t MCTS::_get_random_index(std::mt19937 &gen, int min, int max)
{
    std::uniform_int_distribution<> distr(min, max);
    return distr(gen);
}

// -------------------------------------
//  Constructor / Destructor
// -------------------------------------
MCTS::MCTS(const std::string &starting_fen,
           const std::vector<std::string> &root_moves,
           size_t branching_factor,
           size_t max_depth)
    : BRANCHING_FACTOR(std::min(branching_factor, root_moves.size())),
      MAX_DEPTH(max_depth),
      gen(rd())
{
    // Create the root node
    root = new Node(nullptr, "", starting_fen);

    // For partial expansion, store the candidate moves in root->unexpanded_moves
    // Add up to BRANCHING_FACTOR children immediately if you wish (as in your original code),
    // or simply store them for expansion. Here, we do partial expansion:
    root->unexpanded_moves.assign(root_moves.begin(), root_moves.end());

    // Optionally, you can expand up to BRANCHING_FACTOR right away:
    // (Uncomment if you want the same “initial child creation” as in your original code)
    /*
    size_t child_ctr = 0;
    for (const auto &mv : root_moves)
    {
        if (child_ctr++ >= BRANCHING_FACTOR) break;
        Node *child = add_child(root, mv, chess_lib::getAppliedMove(starting_fen, mv));
        // Remove it from root->unexpanded_moves
        // (But for simplicity, partial expansion is more typical.)
    }
    */
}

MCTS::~MCTS()
{
    std::function<void(Node *)> delete_tree = [&](Node *node)
    {
        for (Node *child : node->children)
            delete_tree(child);
        delete node;
    };
    delete_tree(root);
}

// -------------------------------------
//  is_terminal
// -------------------------------------
bool MCTS::is_terminal(const Node *node) const
{
    // A node is terminal if the game is lost or if there are no moves.
    // Depending on your definition, you might consider a draw also terminal.
    if (chess_lib::isLostCondition(node->fen))
        return true;

    // If no children and no unexpanded moves remain, no moves are possible => terminal
    if (node->children.empty() && node->unexpanded_moves.empty())
        return true;

    return false;
}

// -------------------------------------
//  add_child
// -------------------------------------
MCTS::Node* MCTS::add_child(Node *parent, const std::string &move, const std::string &fen)
{
    Node *child = new Node(parent, move, fen);
    parent->children.push_back(child);
    return child;
}

// -------------------------------------
//  UCB
// -------------------------------------
float MCTS::ucb(const Node *node) const
{
    // If never visited, return +∞ to ensure it gets explored
    if (node->visits == 0)
        return std::numeric_limits<float>::infinity();

    if (node->parent == nullptr) {
        // Root node
        return static_cast<float>(node->q()) / (node->visits + 1e-6f);
    }

    // UCB1
    float exploitation = static_cast<float>(node->q()) / (node->visits + 1e-6f);
    float exploration  = 1.41f * std::sqrt(std::log(node->parent->visits + 1.0f) /
                                           (node->visits + 1e-6f));
    return exploitation + exploration;
}

// -------------------------------------
//  select_node
// -------------------------------------
MCTS::Node* MCTS::select_node(Node *node)
{
    // Traverse down using UCB to find a leaf or a node that still has unexpanded moves
    while (!is_terminal(node))
    {
        // If there are still unexpanded moves, we stop here for expansion
        if (!node->unexpanded_moves.empty())
            return node;

        // Otherwise, pick the best child by UCB
        node = *std::max_element(node->children.begin(), node->children.end(),
            [this](Node *a, Node *b) {
                return ucb(a) < ucb(b);
            }
        );
    }
    return node; // Either terminal or has unexpanded moves
}

// -------------------------------------
//  expand
// -------------------------------------
MCTS::Node* MCTS::expand(Node *node)
{
    // If node is terminal or has no unexpanded moves, return itself
    if (is_terminal(node) || node->unexpanded_moves.empty())
        return node;

    // “Partial expansion”: expand exactly one move from node->unexpanded_moves
    // Here we pick a random move from that vector
    int idx = static_cast<int>(_get_random_index(gen, 0, (int)node->unexpanded_moves.size() - 1));
    std::string move = node->unexpanded_moves[idx];

    // Remove it from unexpanded_moves
    node->unexpanded_moves.erase(node->unexpanded_moves.begin() + idx);

    // Create the new child
    std::string child_fen = chess_lib::getAppliedMove(node->fen, move);
    Node *child = add_child(node, move, child_fen);

    // Prepare child->unexpanded_moves by retrieving moves from chess_lib
    std::vector<std::string> all_moves = chess_lib::getAvailableMoves(child_fen);
    child->unexpanded_moves.assign(all_moves.begin(), all_moves.end());
    
    return child;
}

// -------------------------------------
//  rollout
// -------------------------------------
void MCTS::rollout(Node *node)
{
    // If node is terminal, no simulation needed
    if (is_terminal(node))
        return;

    // Simulate from node->fen up to MAX_DEPTH or until terminal
    std::string current_fen = node->fen;
    size_t sim_depth = 0;

    while (sim_depth < MAX_DEPTH)
    {
        if (chess_lib::isLostCondition(current_fen))
            break; // Terminal

        // Get possible moves
        const std::vector<std::string> moves = chess_lib::getAvailableMoves(current_fen);
        if (moves.empty())
            break; // No legal moves => terminal or draw

        // Randomly pick one
        size_t move_index = _get_random_index(gen, 0, (int)moves.size() - 1);
        const std::string &random_move = moves[move_index];
        
        // Apply it
        try
        {
            current_fen = chess_lib::getAppliedMove(current_fen, random_move);
        }
        catch (const std::exception &e)
        {
            std::cerr << "Rollout move exception: " << e.what() << std::endl;
            break;
        }
        ++sim_depth;
    }

    // If final position is lost from node's perspective, record that
    if (chess_lib::isLostCondition(current_fen))
    {
        // Suppose we define “isWin” as: if the node’s side eventually delivers mate 
        // or the opponent runs out of moves in the next turn, etc.
        // Here we replicate your logic that checks parity of sim_depth:
        bool isWin = (node->turn() && ((sim_depth % 2) != 0)) ||
                     (!node->turn() && ((sim_depth % 2) == 0));

        if (isWin)
            node->wins   = 1;
        else
            node->losses = 1;
    }
}

// -------------------------------------
//  backpropagate
// -------------------------------------
void MCTS::backpropagate(Node *node)
{
    // Take the final outcome from this node
    int w = node->wins;
    int l = node->losses;

    // Walk upwards to root
    while (node != nullptr)
    {
        node->visits++;
        // Update stats in *every* node, including leaf
        node->wins   += w;
        node->losses += l;

        node = node->parent;
    }
}

// -------------------------------------
//  run
// -------------------------------------
void MCTS::run(int iterations)
{
    for (int i = 0; i < iterations; ++i)
    {
        // 1. Selection
        Node *leaf = select_node(root);

        // 2. Expansion (Expand exactly one child if not terminal)
        Node *child = expand(leaf);

        // 3. Rollout
        rollout(child);

        // 4. Backprop
        backpropagate(child);
    }
}

// -------------------------------------
//  get_best_move
// -------------------------------------
std::string MCTS::get_best_move(int iterations)
{
    // Run MCTS
    run(iterations);

    // After run, pick the best child of root. Standard approach: 
    // choose the child with the highest number of visits (or highest average score).
    // We illustrate "max visits" below:
    if (root->children.empty())
    {
        // No moves
        return "";
    }

    Node *best_node = nullptr;
    int best_visits = -1;

    for (Node *child : root->children)
    {
        if (child->visits > best_visits)
        {
            best_visits = child->visits;
            best_node   = child;
        }
    }

    return (best_node ? best_node->move : "");
}
