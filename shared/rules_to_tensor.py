import numpy as np
import torch
import api

piece_to_channel = {
    'P': 0,
    'N': 1,
    'B': 2,
    'R': 3,
    'Q': 4,
    'K': 5,
    'p': 0,
    'n': 1,
    'b': 2,
    'r': 3,
    'q': 4,
    'k': 5
}

channel_to_piece = {
    0:  'P',
    1:  'N',
    2:  'B',
    3:  'R',
    4:  'Q',
    5:  'K',
    6:  'p',
    7:  'n',
    8:  'b',
    9:  'r',
    10: 'q',
    11: 'k'
}

def get_attacked_squares(fen, color):
    """
    zwraca macierz kontrolowanych pol w formacie 8x8 przez dany kolor.
    """

    controlled_squares = np.zeros((8,8), dtype = np.float32)
    moves = api.get_available_moves(fen)
    if moves:
        for move in moves.split('\n'):
            if (color == 'white' and move[0].isupper()) or (color == 'black' and move[0].islower()):
                end_pos = move[2:]
                row, col = 8 - int(end_pos[1]), ord(end_pos[0]) - ord('a')
                controlled_squares[row, col] += 1.0 if color == 'white' else -1.0
    return controlled_squares

def fen_to_tensor(fen) -> torch.Tensor:
    """
    konwertuje stan planszy z FEN na tensor bitboardow.

    Parametry:
    - fen: stan planszy w notacji FEN

    Zwraca:
    - Tensor o ksztalcie [12, 8, 8]
    """

    board_tensor = np.zeros((12, 8, 8), dtype=np.float32)

    #parsowanie FEN na kanaly
    rows = fen.split()[0].split('/')
    for i, row in enumerate(rows):
        col = 0
        for char in row:
            if char.isdigit():
                col += int(char)
            else:
                if char in piece_to_channel:
                    channel = piece_to_channel[char]
                    if char.isupper():
                        board_tensor[channel, i, col] = 1.0
                    else:
                        board_tensor[channel, i, col] = -1.0
                col += 1


    #kontrolowane pola
    controlled_squares = np.zeros((8, 8), dtype=np.float32)
    controlled_squares += get_attacked_squares(fen, 'white')
    controlled_squares -= get_attacked_squares(fen, 'black')

    board_tensor[6] = controlled_squares

    #metadata[0] - prawa roszady
    #metadata[1] - info o biciu w przelocie
    metadata = fen.split()[2:4]

    board_tensor[7, :, :] = 1.0 if 'K' in metadata[0] else 0.0
    board_tensor[8, :, :] = 1.0 if 'Q' in metadata[0] else 0.0
    board_tensor[9, :, :] = 1.0 if 'k' in metadata[0] else 0.0
    board_tensor[10, :, :] = 1.0 if 'q' in metadata[0] else 0.0

    if metadata[1] != '-':
        row, col = divmod(ord(metadata[1][0]) - ord('a'), 8)
        board_tensor[11, row, col] = 1.0

    return torch.tensor(board_tensor, dtype=torch.float32)

def tensor_to_chess_board(tensor):
    """
    nie wiem czy potrzebne. w sensie do oceny pozycji przez stockfisha
    """


def tensor_to_fen(tensor, halfmove_clock=0, fullmove_number=1):
    """
    Konwertuje tensor bitboardow na notacje FEN

    Parametry
    - tensor: Tensor pytorch [12, 8, 8]
    - halfmove_clock: licznik polruchow od ostaniego bicia (zasada 50 ruchow)
    - fullmove_number: licznik ruchow. zaczyna od 1 i jest inkrementowany od ruchu czarnego

    Zwraca
    - stan planszy w notacji FEN
    """


    fen_rows = []

    for row in range(8):
        fen_row = ""
        empty_count = 0

        for col in range(8):
            piece_found = False
            for channel in range(6):
                if tensor[channel, row, col] == 1.0:
                    fen_row += channel_to_piece[channel]
                    piece_found = True
                    break
                elif tensor[channel, row, col] == -1.0:
                    fen_row += channel_to_piece[channel + 6]
                    piece_found = True
                    break

                if not piece_found:
                    empty_count += 1
                else:
                    if empty_count > 0:
                         fen_row += str(empty_count)
                         empty_count = 0
            
        if empty_count > 0:
            fen_row += str(empty_count)

        fen_rows.append(fen_row)

    fen_board = "/".join(fen_rows)

    castling_rights = ""
    if tensor[7, :, :].max() > 0: castling_rights += "K"
    if tensor[8, :, :].max() > 0: castling_rights += "Q"
    if tensor[9, :, :].max() > 0: castling_rights += "k"
    if tensor[10, :, :].max() > 0: castling_rights += "q"
    if castling_rights == "": castling_rights = "-"

    ep_square = "-"
    if tensor[11, :, :].max() > 0:
        ep_position = torch.nonzero(tensor[11, :, :] == 1.0, as_tuple=False)
        if len(ep_position) > 0:
            row, col =  ep_position[0].tolist()
            ep_square = f"{chr(col + ord('a'))}{8 - row}"

    fen = f"{fen_board} w {castling_rights} {ep_square} {halfmove_clock} {fullmove_number}"

    return fen

def index_to_move(idx):
    """
    konwertuje indeks akcji na ruch w formacie FEN na podstawie indeksu

    Parametry:
    - idx: indeks akcji w kanale (0-4095)

    Zwraca:
    - string reprezentujacy ruch w formacie FEN (moze byc nielegalny, API sprawdza)
    """

    from_square = idx // 64
    to_square = idx % 64

    from_pos = f"{chr((from_square % 8) + ord('a'))}{8 - (from_square // 8)}"
    to_pos = f"{chr((to_square % 8) + ord('a'))}{8 - (to_square // 8)}"

    return from_pos + to_pos

def apply_move(board, move):
    """
    aplikuje ruch na planszy

    Parametry:
    - board: aktualny stan planszy w formacie FEN
    - move: ruch do wykonania w formacie FEN

    Zwraca:
    - stan planszy w formacie FEN lub None, jesli ruch nielegalny
    """

    new_board = api.get_applied_move(board, move)
    if new_board == "":
        return None
    return new_board

def get_legal_moves(board):
    """
    zwraca liste legalnych ruchow w formie stringow na podstawie aktualnego stanu planszy

    Parametry:
    - board: plansza w formacie FEN

    Zwraca:
    - lista stringow reprezentujacych legalne ruchy
    """

    available_moves_str = api.get_available_moves(board)

    if not available_moves_str:
        return []

    legal_moves = available_moves_str.strip().split('\n')

    return legal_moves
