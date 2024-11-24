# chess_utils.py

import numpy as np
import torch
import chess


# Mapowanie typów figur na indeksy
PIECE_TO_INDEX = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 2,
    chess.ROOK: 3,
    chess.QUEEN: 4,
    chess.KING: 5
}

def move_to_index(move):
    """
    Konwertuje obiekt chess.Move na odpowiadający indeks akcji.

    Parametry:
    - move (chess.Move): Ruch do konwersji.

    Zwraca:
    - int: Indeks akcji (0-4095).
    """
    return move.from_square * 64 + move.to_square

def legal_moves_to_indices(board):
    """
    Konwertuje wszystkie legalne ruchy na planszy na odpowiadające indeksy akcji.

    Parametry:
    - board (chess.Board): Aktualna plansza gry.

    Zwraca:
    - lista int: Lista indeksów akcji odpowiadających legalnym ruchom.
    """
    return [move_to_index(move) for move in board.legal_moves]

def get_attacked_squares(board, color):
    """
    Zwraca zestaw pól atakowanych przez dany kolor.

    Parametry:
    - board (chess.Board): Aktualna plansza gry.
    - color (chess.Color): Kolor, dla którego obliczane są ataki (chess.WHITE lub chess.BLACK).

    Zwraca:
    - chess.SquareSet: Zestaw pól atakowanych przez określony kolor.
    """
    attacked = chess.SquareSet()
    for square in board.occupied_co[color]:
        attacked |= board.attacks(square)
    return attacked

def generate_bitboards(board):
    """
    Generuje bitboardy do spakowania w tensor. Każdy bitboard reprezentuje różne typy figur i stany gry.

    Parametry:
    - board (chess.Board): Aktualna plansza gry.

    Zwraca:
    - np.ndarray: Tablica 12x8x8 reprezentująca różne aspekty planszy.
    """
    # 0-5: Typy figur, 6: Kontrolowane pola, 7-10: Prawa do roszady, 11: Bicie w przelocie
    bitboards = np.zeros((12, 8, 8), dtype=np.float32)

    # Bierki
    for piece_type, index in PIECE_TO_INDEX.items():
        # Białe bierki
        white_squares = board.pieces(piece_type, chess.WHITE)
        for square in white_squares:
            row, col = divmod(square, 8)
            bitboards[index, row, col] = 1.0  # Białe jako +1

        # Czarne bierki
        black_squares = board.pieces(piece_type, chess.BLACK)
        for square in black_squares:
            row, col = divmod(square, 8)
            bitboards[index, row, col] = -1.0  # Czarne jako -1

    # Kontrolowane pola
    controlled_squares = np.zeros((8, 8), dtype=np.float32)

    white_attacks = get_attacked_squares(board, chess.WHITE)
    for square in white_attacks:
        row, col = divmod(square, 8)
        controlled_squares[row, col] += 1.0

    black_attacks = get_attacked_squares(board, chess.BLACK)
    for square in black_attacks:
        row, col = divmod(square, 8)
        controlled_squares[row, col] -= 1.0

    bitboards[6] = controlled_squares  # Indeks 6 dla kontrolowanych pól

    # Prawa do roszady
    bitboards[7, :, :] = 1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0
    bitboards[8, :, :] = 1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0
    bitboards[9, :, :] = 1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0
    bitboards[10, :, :] = 1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0

    # Bicie w przelocie
    bitboards[11, :, :] = 0.0
    if board.ep_square is not None:
        row, col = divmod(board.ep_square, 8)
        bitboards[11, row, col] = 1.0  # Ustaw pole docelowe na 1.0

    return bitboards

def board_to_tensor(board):
    """
    Konwertuje obiekt chess.Board na tensor wejściowy dla sieci neuronowej.

    Parametry:
    - board (chess.Board): Aktualna plansza gry.

    Zwraca:
    - torch.Tensor: Tensor o kształcie [12, 8, 8] reprezentujący stan planszy.
    """
    tensor = torch.zeros(12, 8, 8)

    piece_to_channel = {
        'P': 0,  # Biały pion
        'N': 1,  # Biały skoczek
        'B': 2,  # Biały goniec
        'R': 3,  # Biała wieża
        'Q': 4,  # Biała hetman
        'K': 5,  # Biały król
        'p': 6,  # Czarny pion
        'n': 7,  # Czarny skoczek
        'b': 8,  # Czarny goniec
        'r': 9,  # Czarna wieża
        'q': 10, # Czarna hetman
        'k': 11  # Czarny król
    }

    for square, piece in board.piece_map().items():
        row = 7 - (square // 8)
        col = square % 8
        channel = piece_to_channel.get(piece.symbol())
        if channel is not None:
            tensor[channel, row, col] = 1.0

    return tensor

def index_to_move(board, idx):
    """
    Konwertuje indeks akcji na obiekt chess.Move na podstawie indeksu.

    Parametry:
    - board (chess.Board): Aktualna plansza gry.
    - idx (int): Indeks akcji w zakresie (0-4095).

    Zwraca:
    - chess.Move lub None: Odpowiadający ruch, jeśli jest legalny, w przeciwnym razie None.

    Wyjątki:
    - ValueError: Jeśli idx nie znajduje się w zakresie 0-4095.
    - TypeError: Jeśli idx nie jest liczbą całkowitą.
    """
    if not isinstance(idx, int):
        raise TypeError("Indeks akcji musi być liczbą całkowitą")
    if not (0 <= idx < 4096):
        raise ValueError("Indeks akcji poza zakresem (musi być między 0 a 4095)")

    from_square = idx // 64
    to_square = idx % 64
    move = chess.Move(from_square, to_square)

    # Sprawdź legalność ruchu
    if move in board.legal_moves:
        return move
    else:
        return None

def get_action_mask(board):
    """
    Tworzy maskę akcji wskazującą, które ruchy są legalne.

    Parametry:
    - board (chess.Board): Aktualna plansza gry.

    Zwraca:
    - torch.Tensor: Tensor o kształcie [1, 4096], gdzie każdy element odpowiada ruchowi.
                    Wartość 1.0 wskazuje legalny ruch, a 0.0 przeciwnie.
    """
    action_mask = torch.zeros(1, 4096, dtype=torch.float32)

    for move in board.legal_moves:
        action_idx = move_to_index(move)
        action_mask[0, action_idx] = 1.0

    return action_mask
