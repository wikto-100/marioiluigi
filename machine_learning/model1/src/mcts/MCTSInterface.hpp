#ifndef MCTS_INTERFACE_H
#define MCTS_INTERFACE_H

#include <string>
#include <vector>

class MCTSInterface {
public:
    // Constructor
    MCTSInterface();

    // Destructor
    ~MCTSInterface();

    /**
     * Generates legal moves based on the given FEN.
     * 
     * @param fen The FEN string representing the board state.
     * @return A vector of legal moves in UCI format.
     */
    std::vector<std::string> generateLegalMoves(const std::string& fen) const;

    /**
     * Selects the best move from the list of legal moves using MCTS.
     * 
     * @param legalMoves A vector of legal moves in UCI format.
     * @return The selected move in UCI format.
     */
    std::string selectMove(const std::vector<std::string>& legalMoves) const;

    /**
     * Processes a single FEN string and outputs the selected move.
     * 
     * @param fen The FEN string representing the board state.
     * @return The selected move in UCI format.
     */
    std::string processFen(const std::string& fen) const;

private:
    // Internal helper methods can be declared here if needed
};

#endif // MCTS_INTERFACE_H
