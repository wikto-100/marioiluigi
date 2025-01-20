import chess
import numpy as np
import torch
from typing import Tuple, Dict

def get_move_index(move: chess.Move) -> int:
    """
    Mapuje ruch szachowy na unikalny indeks w zakresie od 0 do 4095.

    Argumenty:
        move (chess.Move): Ruch szachowy do zindeksowania.

    Zwraca:
        int: Unikalny indeks dla ruchu.
    """
    return 64 * move.from_square + move.to_square

def mask_and_valid_moves(
    board: chess.Board,
) -> Tuple[torch.Tensor, Dict[int, chess.Move]]:
    """
    Tworzy maskę prawidłowych ruchów oraz słownik mapujący indeksy ruchów na obiekty ruchów.

    Argumenty:
        board (chess.Board): Aktualna plansza szachowa.

    Zwraca:
        tuple:
            torch.Tensor: Spłaszczona maska prawidłowych ruchów (4096-wymiarowa).
            dict: Mapowanie od indeksu ruchu do obiektu chess.Move.
    """
    mask = np.zeros(4096, dtype=np.double)
    valid_moves_dict = {}

    for move in board.legal_moves:
        index = get_move_index(move)
        mask[index] = 1.0
        valid_moves_dict[index] = move

    return torch.from_numpy(mask), valid_moves_dict

def convert_state(board: chess.Board) -> np.ndarray:
    """
    Konwertuje aktualny stan planszy szachowej na 3-wymiarową tablicę NumPy bitboardów.

    Wynik ma kształt (16, 8, 8), gdzie każda warstwa reprezentuje:
        - 12 dla każdego typu figury i koloru
        - 1 dla pustych pól
        - 1 dla ruchu gracza
        - 1 dla praw do roszady
        - 1 dla en passant

    Argumenty:
        board (chess.Board): Aktualna plansza szachowa.

    Zwraca:
        np.ndarray: 3D tablica reprezentująca stan planszy.
    """
    bitboards = []

    # Mapowanie typów figur na symbole dla spójności
    piece_symbols = {
        (chess.PAWN, True): "P",
        (chess.KNIGHT, True): "N",
        (chess.BISHOP, True): "B",
        (chess.ROOK, True): "R",
        (chess.QUEEN, True): "Q",
        (chess.KING, True): "K",
        (chess.PAWN, False): "p",
        (chess.KNIGHT, False): "n",
        (chess.BISHOP, False): "b",
        (chess.ROOK, False): "r",
        (chess.QUEEN, False): "q",
        (chess.KING, False): "k",
    }

    # Generuj bitboardy dla każdego typu figury i koloru
    for color in chess.COLORS:
        for piece_type in chess.PIECE_TYPES:
            symbol = piece_symbols[(piece_type, color)]
            bitmask = board.pieces(piece_type, color)
            bitboards.append(bitmask)

    # Bitboard pustych pól
    empty_bitmask = ~board.occupied & (2**64 - 1)
    bitboards.append(empty_bitmask)

    # Bitboard ruchu gracza (wszystkie 1 dla białych, wszystkie 0 dla czarnych)
    player_bitmask = (2**64 - 1) if board.turn else 0
    bitboards.append(player_bitmask)

    # Bitmask praw do roszady (jako liczba całkowita)
    castling_bitmask = board.castling_rights
    bitboards.append(castling_bitmask)

    # Bitmaska en passant
    en_passant_bitmask = 0
    if board.ep_square is not None:
        en_passant_bitmask = 1 << board.ep_square
    bitboards.append(en_passant_bitmask)

    # Inicjalizuj 3D tablicę
    bitarray = np.zeros((16, 8, 8), dtype=np.uint8)

    for layer, bitmask in enumerate(bitboards):
        for square in range(64):
            row = square // 8
            col = square % 8
            bitarray[layer, row, col] = (bitmask >> square) & 1

    return bitarray
