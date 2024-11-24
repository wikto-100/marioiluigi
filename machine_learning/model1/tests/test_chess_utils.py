import sys
import os
import pytest
import chess
import torch
import numpy as np

# Add the src directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..', 'src')


sys.path.insert(0, parent_dir)
from chess_utils import (
    get_attacked_squares,
    generate_bitboards,
    board_to_tensor,
    index_to_move,
    get_action_mask
)

@pytest.fixture
def empty_board():
    return chess.Board(None)

@pytest.fixture
def initial_board():
    return chess.Board()

@pytest.fixture
def custom_board():
    board = chess.Board()
    # Set up a custom position
    board.set_fen("8/8/8/8/4P3/5N2/8/8 w - - 0 1")
    return board

def test_get_attacked_squares_empty(empty_board):
    # No pieces on the board; no squares are attacked
    attacked_white = get_attacked_squares(empty_board, chess.WHITE)
    attacked_black = get_attacked_squares(empty_board, chess.BLACK)
    assert len(attacked_white) == 0
    assert len(attacked_black) == 0

def test_get_attacked_squares_initial(initial_board):
    """
    Tests the get_attacked_squares function for the initial chess board setup.
    """
    # Calculate attacked squares for white and black
    attacked_white = get_attacked_squares(initial_board, chess.WHITE)
    attacked_black = get_attacked_squares(initial_board, chess.BLACK)
    
    # Expected attacked squares for white pawns in the initial position
    expected_white_attacks = chess.SquareSet(
        [
            chess.A3, chess.B3, chess.C3, chess.D3, chess.E3, chess.F3, chess.G3, chess.H3, 
            chess.A2, chess.B2, chess.C2, chess.D2, chess.E2, chess.F2, chess.G2, chess.H2,
            chess.B1, chess.C1, chess.D1, chess.E1, chess.F1, chess.G1
        ]
    )
    
    # Expected attacked squares for black pawns in the initial position
    expected_black_attacks = chess.SquareSet(
        [
            chess.A6, chess.B6, chess.C6, chess.D6, chess.E6, chess.F6, chess.G6, chess.H6, 
            chess.A7, chess.B7, chess.C7, chess.D7, chess.E7, chess.F7, chess.G7, chess.H7,
            chess.B8, chess.C8, chess.D8, chess.E8, chess.F8, chess.G8
        ]
    )
    
    # Assert that the actual attacked squares match the expected attacked squares
    assert attacked_white == expected_white_attacks, f"Expected: {expected_white_attacks}, Got: {attacked_white}"
    assert attacked_black == expected_black_attacks, f"Expected: {expected_black_attacks}, Got: {attacked_black}"


def test_generate_bitboards_empty(empty_board):
    bitboards = generate_bitboards(empty_board)
    assert bitboards.shape == (12, 8, 8)
    assert np.all(bitboards == 0.0)

def test_generate_bitboards_initial(initial_board):
    bitboards = generate_bitboards(initial_board)
    assert bitboards.shape == (12, 8, 8)
    
    # Check white pawns
    white_pawns = initial_board.pieces(chess.PAWN, chess.WHITE)
    for square in white_pawns:
        row, col = divmod(square, 8)
        assert bitboards[0, row, col] == 1.0
    
    # Check black pawns
    black_pawns = initial_board.pieces(chess.PAWN, chess.BLACK)
    for square in black_pawns:
        row, col = divmod(square, 8)
        assert bitboards[0, row, col] == -1.0  # Index 0 for pawns
    
    # Check controlled squares
    controlled = bitboards[6]
    expected_controlled = np.zeros((8, 8), dtype=np.float32)
    for square in get_attacked_squares(initial_board, chess.WHITE):
        row, col = divmod(square, 8)
        expected_controlled[row, col] += 1.0
    for square in get_attacked_squares(initial_board, chess.BLACK):
        row, col = divmod(square, 8)
        expected_controlled[row, col] -= 1.0
    assert np.array_equal(controlled, expected_controlled)

def test_board_to_tensor_initial(initial_board):
    tensor = board_to_tensor(initial_board)
    assert tensor.shape == (12, 8, 8)
    
    # Check white pawns
    white_pawns = initial_board.pieces(chess.PAWN, chess.WHITE)
    for square in white_pawns:
        row = 7 - (square // 8)
        col = square % 8
        assert tensor[0, row, col] == 1.0  # Channel 0 for white pawns
    
    # Check black pawns
    black_pawns = initial_board.pieces(chess.PAWN, chess.BLACK)
    for square in black_pawns:
        row = 7 - (square // 8)
        col = square % 8
        assert tensor[6, row, col] == 1.0  # Channel 6 for black pawns

def test_index_to_move_initial(initial_board):
    # Example: e2e4 corresponds to from_square=12 (e2), to_square=28 (e4)
    e2 = chess.E2
    e4 = chess.E4
    idx = e2 * 64 + e4
    move = index_to_move(initial_board, idx)
    assert move == chess.Move.from_uci("e2e4")
    
    # Illegal move: e2e5 (cannot move pawn two squares from e2 to e5 in one move)
    e5 = chess.E5
    idx_illegal = e2 * 64 + e5
    move_illegal = index_to_move(initial_board, idx_illegal)
    assert move_illegal is None

def test_get_action_mask_initial(initial_board):
    action_mask = get_action_mask(initial_board)
    assert action_mask.shape == (10, 4096)
    
    # White pawn moves: each pawn can move one or two squares forward
    for pawn in initial_board.pieces(chess.PAWN, chess.WHITE):
        from_square = pawn
        # One square forward
        to_square = from_square + 8
        action_idx = from_square * 64 + to_square
        channel = 0  # Channel 0 for white pawns
        assert action_mask[channel, action_idx] == 1.0
        
        # Two squares forward (only if on rank 2)
        rank = chess.square_rank(from_square)
        if rank == 1:
            to_square_two = from_square + 16
            action_idx_two = from_square * 64 + to_square_two
            assert action_mask[channel, action_idx_two] == 1.0
    
    # Check that illegal moves are masked
    # For example, moving a knight in the initial position to an illegal square
    knight = next(iter(initial_board.pieces(chess.KNIGHT, chess.WHITE)))
    from_square = knight
    to_square = from_square + 1  # Typically illegal for knights
    action_idx = from_square * 64 + to_square
    channel = 1  # Channel 1 for white knights
    assert action_mask[channel, action_idx] == 0.0

def test_custom_board(custom_board):
    """
    Tests a custom position for specific functionalities.
    Custom Position: "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
    """
    # Test attacked squares for white
    attacked_white = get_attacked_squares(custom_board, chess.WHITE)
    
    # Explicitly define the expected attacked squares
    # Pawn on E4 and knight on F3
    expected_attacks_white = chess.SquareSet(
        [
            chess.D5, chess.F5,  # Pawn on E4 attacks D5, F5
            chess.D2, chess.E1, chess.E5, chess.G5, chess.H4, chess.H2, chess.D4, chess.G1  # Knight on F3
        ]
    )
    
    # Assert attacked squares match the expected values
    assert attacked_white == expected_attacks_white, f"Expected: {expected_attacks_white}, Got: {attacked_white}"


    
    # Test generate_bitboards
    bitboards = generate_bitboards(custom_board)
    assert bitboards.shape == (12, 8, 8)
    
    # Verify a specific piece
    # For example, white knight on f3
    f3 = chess.F3
    row, col = divmod(f3, 8)
    assert bitboards[1, row, col] == 1.0  # Channel 1 for white knights
    
    # Test board_to_tensor
    tensor = board_to_tensor(custom_board)
    assert tensor.shape == (12, 8, 8)
    assert tensor[1, 5, 5] == 1.0  # White knight on f3 (row=5, col=5)
    
    # Test index_to_move
    # Example: e4e5 is a legal move
    e4 = chess.E4
    e5 = chess.E5
    idx = e4 * 64 + e5
    move = index_to_move(custom_board, idx)
    assert move == chess.Move.from_uci("e4e5")
    

    
    # Test get_action_mask
    action_mask = get_action_mask(custom_board)
    assert action_mask.shape == (10, 4096)
    
    # Verify that e4e5 is masked
    channel_pawn = 0  # White pawn channel
    action_idx_e4e5 = e4 * 64 + e5
    assert action_mask[channel_pawn, action_idx_e4e5] == 1.0
    
    

def test_en_passant(generate_en_passant_board):
    board = generate_en_passant_board
    bitboards = generate_bitboards(board)
    
    # En passant target square should be set
    assert board.ep_square is not None
    row, col = divmod(board.ep_square, 8)
    assert bitboards[11, row, col] == 1.0
    
    # Test board_to_tensor for en passant
    
    # Test get_action_mask includes en passant moves
    action_mask = get_action_mask(board)
    for move in board.legal_moves:
        # Check if the move targets the en passant square
        if board.ep_square is not None and move.to_square == board.ep_square:
            from_square = move.from_square
            to_square = move.to_square
            action_idx = from_square * 64 + to_square
            # En passant is treated as a pawn move, so it should be in channel 0
            assert action_mask[0, action_idx] == 1.0, f"En passant move not in action mask: {move}"

@pytest.fixture
def generate_en_passant_board():
    # Set up a position where en passant is possible
    board = chess.Board()
    # e2e4 e7e5
    board.push_san("e4")
    board.push_san("h6")
    # d2d4 e5xd4
    board.push_san("e5")
    board.push_san("d5")
    # Now, white can perform en passant
    return board

def test_castling_rights():
    board = chess.Board()
    # Set up a custom position
    board.set_fen('rnbqkbnr/pppppppp/8/8/8/4PN2/PPPPBPPP/RNBQK2R b KQkq - 0 1')
    # Initial position has all castling rights
    bitboards = generate_bitboards(board)
    print(board)
    # White kingside castling
    assert bitboards[7].all() == 1.0
    # White queenside castling
    assert bitboards[8].all() == 1.0
    # Black kingside castling
    assert bitboards[9].all() == 1.0
    # Black queenside castling
    assert bitboards[10].all() == 1.0
    board.push_san("h6")  # black makes some move
    
    # Now, make a move that removes a castling right
    board.push_san("Kf1")  # White moves king
    bitboards_after = generate_bitboards(board)
    # White kingside castling should now be unavailable
    assert bitboards_after[7].all() == 0.0
    assert bitboards_after[8].all() == 0.0
    # Other castling rights should remain
    
    assert bitboards_after[9].all() == 1.0
    assert bitboards_after[10].all() == 1.0

def test_invalid_index_to_move(initial_board):
    # Test indices out of range
    # Negative index
    with pytest.raises(ValueError):
        index_to_move(initial_board, -1)
    
    # Index greater than 4095
    with pytest.raises(ValueError):
        index_to_move(initial_board, 5000)

def test_invalid_board():
    # Create a board with no pieces
    board = chess.Board(None)
    tensor = board_to_tensor(board)
    assert tensor.shape == (12, 8, 8)
    assert torch.all(tensor == 0.0)
    
    # Action mask should have no legal moves
    action_mask = get_action_mask(board)
    assert torch.all(action_mask == 0.0)

def test_promotion_moves():
    # Set up a promotion scenario
    board = chess.Board()
    # Clear the board
    board.clear()
    # Place a white pawn on the seventh rank
    board.set_piece_at(chess.G7, chess.Piece(chess.PAWN, chess.WHITE))
    # Place black pieces to prevent promotion by capture
    board.set_piece_at(chess.H8, chess.Piece(chess.ROOK, chess.BLACK))
    # Now, white pawn can promote to Q, R, B, or N
    # Push the move g7g8Q
    promotion_moves = [chess.Move.from_uci("g7g8q")]
    for move in promotion_moves:
        board.push(move)
    
    # Now, check generate_bitboards
    bitboards = generate_bitboards(board)
    # The last rank should have promoted pieces
    for move in promotion_moves:
        promoted_square = move.to_square
        row, col = divmod(promoted_square, 8)
        promoted_piece = move.promotion
        # Determine channel based on promotion
        promotion_piece_to_channel = {
            chess.QUEEN: 4,
            chess.ROOK: 3,
            chess.BISHOP: 2,
            chess.KNIGHT: 1
        }
        channel = promotion_piece_to_channel[promoted_piece]
        assert bitboards[channel, row, col] == 1.0


