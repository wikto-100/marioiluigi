# reward.py

import chess
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Definicja wartości figur dla nagród za bicie (w centipawnach)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 800,
    chess.KING: 0
}

def calculate_reward(previous_eval, current_eval, agent_color, game_result=None,
                    previous_board=None, current_board=None, last_move=None):
    """
    Oblicza i normalizuje nagrodę na podstawie zmian w ocenie pozycji oraz wydarzeń w grze.

    Parametry:
    - previous_eval (int): Ocena przed ruchem (w centipawnach).
    - current_eval (int): Ocena po ruchu (w centipawnach).
    - agent_color (chess.Color): Kolor agenta (chess.WHITE lub chess.BLACK).
    - game_result (str, opcjonalnie): Wynik gry ('1-0', '0-1', '1/2-1/2') lub None, jeśli gra trwa.
    - previous_board (chess.Board, opcjonalnie): Stan planszy przed ruchem.
    - current_board (chess.Board, opcjonalnie): Stan planszy po ruchu.
    - last_move (chess.Move, opcjonalnie): Ruch, który właśnie został wykonany.

    Zwraca:
    - float: Znormalizowana nagroda uwzględniająca zmiany oceny i wydarzenia w grze.
    """
    # Inicjalizacja składników nagrody
    eval_change_reward = 0.0
    capture_reward = 0.0
    checkmate_reward = 0.0

    # 1. Nagroda za zmianę oceny pozycji
    if previous_eval is not None and current_eval is not None:
        eval_change = current_eval - previous_eval
        # Zmiana znaku na podstawie koloru agenta
        if agent_color == chess.BLACK:
            eval_change = -eval_change
        # Skalowanie nagrody za zmianę oceny (rozszerzenie zakresu)
        eval_change_reward = eval_change / 50.0  # Przykładowa skala: 50 centipawnów = +1.0 nagrody
        logger.debug(f"Zmiana oceny: {eval_change} centipawnów, Nagroda: {eval_change_reward}")

    # 2. Nagroda za bicie figur
    if previous_board and last_move:
        if previous_board.is_capture(last_move):
            captured_piece = previous_board.piece_at(last_move.to_square)
            if captured_piece:
                captured_value = PIECE_VALUES.get(captured_piece.piece_type, 0)
                # Nagroda za bicie figur w zależności od ich wartości
                capture_reward = captured_value / 500.0  # Przykładowa skala: 500 centipawnów = +1.0 nagrody
                logger.debug(f"Zbita figura: {captured_piece.symbol()}, Wartość: {captured_value}, Nagroda: {capture_reward}")

    # 5. Nagroda/Kara za mata
    if game_result is not None:
        if (game_result == '1-0' and agent_color == chess.WHITE) or \
           (game_result == '0-1' and agent_color == chess.BLACK):
            # Agent wygrywa grę
            checkmate_reward = 30.0  # Wyższa nagroda za zwycięstwo
            logger.debug(f"Wynik gry: {game_result}, Nagroda za mata: +30.0")
        elif (game_result == '1-0' and agent_color == chess.BLACK) or \
             (game_result == '0-1' and agent_color == chess.WHITE):
            # Agent przegrywa grę
            checkmate_reward = -30.0  # Wyższa kara za porażkę
            logger.debug(f"Wynik gry: {game_result}, Kara za mata: -30.0")
        # Brak dodatkowej nagrody za remisy

    # 6. Połączenie składników nagrody z wagami
    # Przypisanie różnych wag każdemu składnikowi w celu zrównoważenia ich wpływu
    total_reward = (
        1.0 * eval_change_reward +
        0.2 * capture_reward +
        1.0 * checkmate_reward
    )
    logger.debug(f"Połączona nagroda przed ograniczeniem: {total_reward}")

    # 7. Normalizacja nagrody
    # Dopasowanie zakresu ograniczeń na podstawie zaktualizowanej skali
    total_reward = max(min(total_reward, 40.0), -40.0)  # Dostosowanie zakresu w razie potrzeby
    logger.debug(f"Połączona nagroda po ograniczeniu: {total_reward}")

    return float(total_reward)
