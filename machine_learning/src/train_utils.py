import logging
import random
from typing import Optional, Dict, List

import chess
import torch
from chess import Board
from chess.engine import Limit
from src.chess_utils import convert_state, mask_and_valid_moves, get_move_index

# Skonfiguruj logowanie
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

def generate_random_sample(
    agent, stockfish, board: Board, analysis_depth: int = 5
) -> None:
    """
    Generuje losową próbkę wykonując dwa losowe ruchy i oceniając planszę.

    Argumenty:
        agent: Instancja agenta.
        stockfish: Instancja silnika Stockfish.
        board (Board): Aktualna plansza szachowa.
        analysis_depth (int): Głębokość analizy dla Stockfish.
    """
    try:
        priority = 1
        state = convert_state(board)
        valid_moves, _ = mask_and_valid_moves(board)

        # Wybierz i wykonaj pierwszy losowy ruch
        random_move = random.choice(list(board.legal_moves))
        action = get_move_index(random_move)
        logger.debug(f"Wybrano losowy ruch: {random_move}")

        # Analizuj planszę przed pierwszym ruchem
        analysis_before = stockfish.analyse(
            board=board, limit=Limit(depth=analysis_depth)
        )
        board_score_before = analysis_before["score"].relative.score(mate_score=10000)

        board.push(random_move)
        logger.debug(f"Plansza po pierwszym ruchu: {board.fen()}")

        # Wybierz i wykonaj drugi losowy ruch
        if board.is_game_over():
            logger.debug("Gra zakończona po pierwszym ruchu.")
            board_score_after = board_score_before  # Bez zmian, jeśli gra zakończona
        else:
            random_move = random.choice(list(board.legal_moves))
            board.push(random_move)
            logger.debug(f"Plansza po drugim ruchu: {board.fen()}")

            # Analizuj planszę po drugim ruchu
            analysis_after = stockfish.analyse(
                board=board, limit=Limit(depth=analysis_depth)
            )
            board_score_after = analysis_after["score"].relative.score(mate_score=10000)

        # Oblicz nagrodę
        reward = (board_score_after - board_score_before) / 100 - 0.01
        logger.debug(f"Obliczono nagrodę: {reward}")

        next_state = convert_state(board)
        done = board.is_game_over()
        next_valid_moves, _ = mask_and_valid_moves(board)

        # Cofnij dwa ruchy
        board.pop()
        board.pop()
        logger.debug(f"Plansza cofnięta do: {board.fen()}")

        # Zapisz doświadczenie w pamięci agenta
        agent.remember(
            priority,
            state,
            action,
            reward,
            next_state,
            done,
            valid_moves,
            next_valid_moves,
        )
        logger.debug("Próbka zapisana w pamięci agenta.")

    except Exception as e:
        logger.error(f"Błąd w generate_random_sample: {e}")

def choose_move(agent, board: Board) -> chess.Move:
    """
    Wybiera ruch na podstawie polityki agenta lub losowo.

    Argumenty:
        agent: Instancja agenta lub ciąg znaków 'random'.
        board (Board): Aktualna plansza szachowa.

    Zwraca:
        chess.Move: Wybrany ruch.
    """
    try:
        if agent.name == "random":
            chosen_move = random.choice(list(board.legal_moves))
            logger.debug(f"Losowo wybrany ruch: {chosen_move}")
            return chosen_move

        chosen_move_index = -1
        fen = board.fen()
        if fen in agent.openings_dict:
            #najpierw sprawdz czy idziemy openingiem
            logging.info(f"uzycie ruchu otwarcia dla FEN: {fen}")
            opening_moves = agent.openings_dict[fen]
            chosen_move = chess.Move.from_uci(random.choice(opening_moves))
            chosen_move_index = get_move_index(chosen_move)
        else:
            logging.info(f"pozycja: {fen} nie znajduje sie w bazie otwarc")

        # Wybór ruchu na podstawie agenta
        bit_state = convert_state(board)
        valid_moves_tensor, valid_move_dict = mask_and_valid_moves(board)

        if chosen_move_index == -1:
            #jesli ruchu nie bylo w bazie openingow
            with torch.no_grad():
                # **1. Przenieś tensory na urządzenie agenta**
                tensor = (
                    torch.from_numpy(bit_state).float().unsqueeze(0).to(agent.device)
                )  # Obsługa GPU
                valid_moves_tensor = valid_moves_tensor.to(agent.device)  # Obsługa GPU

                policy_values = agent.policy_net(tensor, valid_moves_tensor)

                # **2. Przenieś policy_values z powrotem na CPU (jeśli konieczne) i konwertuj na liczbę całkowitą**
                chosen_move_index = int(policy_values.argmax(dim=1).item())

        chosen_move = valid_move_dict.get(chosen_move_index, None)
        if chosen_move is None:
            chosen_move = random.choice(list(board.legal_moves))
            logger.debug(
                f"Nieprawidłowy indeks ruchu. Wybrano losowy ruch: {chosen_move}"
            )
        else:
            logger.debug(f"Ruch wybrany przez agenta: {chosen_move}")

        return chosen_move

    except Exception as e:
        logger.error(f"Błąd w choose_move: {e}")
        # W razie błędu wybierz losowy ruch
        fallback_move = random.choice(list(board.legal_moves))
        logger.debug(f"Wybrano losowy ruch jako rezerwę: {fallback_move}")
        return fallback_move

def test_agent(
    agent_white,
    agent_black,
    games: int = 1,
    board_config: Optional[str] = None,
) -> None:
    """
    Testuje agenta, rozgrywając określoną liczbę partii przeciwko przeciwnikowi.

    Argumenty:
        agent_white: Instancja agenta grającego białymi.
        agent_black: Instancja agenta grającego czarnymi.
        
        games (int): Liczba partii do rozegrania.
        board_config (Optional[str]): FEN z początkową konfiguracją planszy.
    """
    outcomes: List[str] = []

    for game_number in range(1, games + 1):
        try:
            # Inicjalizuj planszę
            board = chess.Board(board_config) if board_config else chess.Board()
            logger.info(
                f"Rozpoczęcie partii {game_number}/{games} z planszą: {board.fen()}"
            )

            while not board.is_game_over(claim_draw=True):
                # Sprawdź, czyja jest tura
                if board.turn == chess.WHITE:
                    move = choose_move(agent_white, board)
                    logger.debug(f"Białe ({agent_white.name}) grają: {move}")
                else:
                    move = choose_move(agent_black, board)
                    logger.debug(f"Czarne ({agent_black.name}) grają: {move}")

                board.push(move)

            result = board.result(claim_draw=True)
            outcomes.append(result)
            logger.info(f"Partia {game_number} zakończona wynikiem: {result}")

        except Exception as e:
            logger.error(f"Błąd podczas partii {game_number}: {e}")
            outcomes.append("Error")

    # Podsumowanie wyników
    outcome_dict: Dict[str, str] = {
        "1-0": "Białe wygrały",
        "1/2-1/2": "Remis",
        "0-1": "Czarne wygrały",
        "Error": "Błąd w partii",
    }

    summary: Dict[str, int] = {}
    for outcome in outcomes:
        summary[outcome] = summary.get(outcome, 0) + 1

    logger.info("Podsumowanie testu:")
    for outcome, count in summary.items():
        percentage = (count / games) * 100
        description = outcome_dict.get(outcome, "Nieznany wynik")
        logger.info(f"{outcome} ({description}): {percentage:.2f}%")

def read_fen(fen_path: str):
    """
    Wczytuje konfigurację planszy z pliku FEN.

    Argumenty:
        fen_path (str): Ścieżka do pliku FEN.

    Zwraca:
        str: Wczytana konfiguracja FEN.
    """
    with open(fen_path, 'r') as fen_file:
        return fen_file.readline()




"""A"""
def simple_test(agent_white, agent_black, board_config: Optional[str] = None) -> None:
    try:
        # Inicjalizuj planszę
        board = chess.Board(board_config) if board_config else chess.Board()
        logger.info(
            f"Rozpoczęcie partii z planszą: {board.fen()}"
        )

        while not board.is_game_over(claim_draw=True):
            # Sprawdź, czyja jest tura
            if board.turn == chess.WHITE:
                move = choose_move(agent_white, board)
                logger.info(f"Białe ({agent_white.name}) grają: {move}")
            else:
                move = choose_move(agent_black, board)
                logger.info(f"Czarne ({agent_black.name}) grają: {move}")

            board.push(move)

        result = board.result(claim_draw=True)
        logger.info(f"Partia zakończona wynikiem: {result}")

    except Exception as e:
        logger.error(f"Błąd podczas partii: {e}")

"""A"""
