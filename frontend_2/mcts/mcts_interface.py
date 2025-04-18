# mcts_interface.py
import mcts  # This imports mcts.py generated by SWIG
import chess
def get_best_move(starting_fen, iterations, root_moves, branching_factor=10, max_depth=100):
    """
    Interfaces with the MCTS C++ library to get the best move.

    :param starting_fen: The FEN string representing the board state.
    :param iterations: Number of MCTS iterations to perform.
    :param root_moves: List of possible root moves as strings.
    :param branching_factor: Maximum number of child nodes per node.
    :param max_depth: Maximum depth for simulations.
    :return: The best move as a string.
    """
    # Create an MCTS instance

    mcts_instance = mcts.MCTS(starting_fen, root_moves, branching_factor, max_depth)

    # Get the best move by running the specified number of iterations
    best_move = mcts_instance.get_best_move(iterations)

    return chess.Move.from_uci(best_move)
