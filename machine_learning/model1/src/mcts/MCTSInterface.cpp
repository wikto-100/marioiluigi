#include "MCTSInterface.hpp"
#include "chess_lib.hpp"
#include "MCTS.hpp"
#include <iostream>
#include <vector>
#include <stdexcept>
#include <random>

// Constructor
MCTSInterface::MCTSInterface() {
    // Initialization logic, if any
}

// Destructor
MCTSInterface::~MCTSInterface() {
    // Cleanup logic, if any
}

/**
 * Generates legal moves using the chess_lib API based on the given FEN.
 */
std::vector<std::string> MCTSInterface::generateLegalMoves(const std::string& fen) const {
    try {
        return chess_lib::getAvailableMoves(fen);
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error generating legal moves: " << e.what() << std::endl;
        return {};
    }
}

/**
 * Selects the best move from the list of legal moves using MCTS.
 * For now, this implementation selects a random move.
 */
std::string MCTSInterface::selectMove(const std::vector<std::string>& legalMoves) const {
    if (legalMoves.empty()) {
        return "none"; // Return "none" if no legal moves are available
    }
    MCTS mcts(legalMoves);
    std::string best_move = mcts.get_best_move();

    return best_move;
}

/**
 * Processes a single FEN string, generates legal moves, and selects the best move.
 */
std::string MCTSInterface::processFen(const std::string& fen) const {
    try {
        // Generate legal moves
        auto legalMoves = generateLegalMoves(fen);

        // Select the best move using MCTS (random selection for now)
        return selectMove(legalMoves);
    } catch (const std::invalid_argument& e) {
        std::cerr << "Error processing FEN: " << e.what() << std::endl;
        return "none"; // Indicate an error occurred
    }
}

// Main program loop for integration with the executable
int main() {
    MCTSInterface mcts;
    std::string fen;

    while (true) {
        // Read FEN from standard input
        if (!std::getline(std::cin, fen)) {
            break; // Exit loop if input stream is closed
        }

        if (fen.empty()) {
            std::cerr << "Received empty FEN, skipping...\n";
            continue;
        }

        try {
            // Process the FEN and get the move
            std::string move = mcts.processFen(fen);

            // Output the move to standard output
            std::cout << move << std::endl;

            // Flush output to ensure the move is sent immediately
            std::cout.flush();
        } catch (const std::exception& e) {
            std::cerr << "Error processing FEN: " << e.what() << std::endl;
        }
    }

    return 0;
}
