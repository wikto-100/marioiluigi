import chess
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Wartości figur w centypionach
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def calculate_in_game_reward(previous_eval, current_eval, agent_color, previous_board, current_board, last_move):
    """
    Oblicz nagrodę w grze na podstawie zmian oceny Stockfisha oraz heurystyk materiałowych/pozycyjnych.

    Parametry:
    - previous_eval (int): Ocena Stockfisha przed ruchem.
    - current_eval (int): Ocena Stockfisha po ruchu.
    - agent_color (chess.Color): Kolor agenta.
    - previous_board (chess.Board): Stan planszy przed ruchem.
    - current_board (chess.Board): Stan planszy po ruchu.
    - last_move (chess.Move): Wykonany ruch.

    Zwraca:
    - float: Natychmiastowa nagroda.
    """
    alpha = 0.01
    beta = 0.1
    gamma = 0.05

    eval_change_reward = 0.0
    material_reward = 0.0
    positional_reward = 0.0

    # Zmiana oceny
    if previous_eval is not None and current_eval is not None:
        eval_change = current_eval - previous_eval
        if agent_color == chess.BLACK:
            eval_change = -eval_change
        eval_change_reward = alpha * eval_change
        logger.debug(f"Zmiana oceny: {eval_change}, Nagroda: {eval_change_reward}")

    # Zmiany równowagi materiałowej
    if previous_board.is_capture(last_move):
        captured_piece = previous_board.piece_at(last_move.to_square)
        if captured_piece and captured_piece.color != agent_color:
            material_reward += beta * PIECE_VALUES.get(captured_piece.piece_type, 0)
            logger.debug(f"Zbicie figury: {captured_piece.symbol()}, Wartość: {PIECE_VALUES[captured_piece.piece_type]}")

    # Nagrody pozycyjne (uprość na mobilność i szachy)
    mobility_difference = len(list(current_board.legal_moves)) - len(list(previous_board.legal_moves))
    positional_reward += gamma * mobility_difference

    if current_board.is_check():
        positional_reward += gamma * 0.5  # Premia za danie przeciwnikowi szacha
        logger.debug("Ruch daje szacha. Nagroda pozycyjna: +0.5")

    # Łączna nagroda
    total_reward = eval_change_reward + material_reward + positional_reward
    logger.debug(f"Łączna nagroda w grze: {total_reward}")
    return total_reward


def calculate_end_game_reward(agent_color, game_result):
    """
    Oblicz nagrody końcowe na podstawie wyniku gry.

    Parametry:
    - agent_color (chess.Color): Kolor agenta.
    - game_result (str): Wynik gry ('1-0', '0-1', '1/2-1/2').

    Zwraca:
    - float: Nagroda końcowa.
    """
    win_reward = 1000.0
    lose_penalty = -1000.0
    draw_reward = 1.0

    if (game_result == '1-0' and agent_color == chess.WHITE) or \
       (game_result == '0-1' and agent_color == chess.BLACK):
        logger.debug(f"Agent wygrywa! Nagroda: +{win_reward}")
        return win_reward
    elif (game_result == '1-0' and agent_color == chess.BLACK) or \
         (game_result == '0-1' and agent_color == chess.WHITE):
        logger.debug(f"Agent przegrywa! Kara: {lose_penalty}")
        return lose_penalty
    else:
        logger.debug(f"Gra kończy się remisem. Nagroda: {draw_reward}")
        return draw_reward
