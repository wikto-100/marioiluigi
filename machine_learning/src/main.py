# main.py

import os
import logging
import chess.engine

from src.chess_agent import ChessAgent
from src.train_utils import test_agent
from src.q_learning import Q_learning
from src.train_utils import read_fen

def main():
    """
    Funkcja main inicjalizuje agenta szachowego, włącza silnik Stockfish, konfiguruje planszę i uruchamia testy.
    """
    # Zainicjuj logger dla pliku main
    logger = logging.getLogger("main")

    try:
        # Zainicjuj ChessAgent
        logger.info("Inicjalizacja agenta szachowego.")
        agent_white = ChessAgent(name="Garry Kasparov")
        agent_black = ChessAgent(name="Magnus Carlsen")
        # Zdefiniuj ścieżkę silnika Stockfish
        stockfish_path = os.path.join(
            os.path.dirname(__file__), "../stockfish/stockfish-ubuntu-x86-64"
        )
        model_save_path = os.path.join(
            os.path.dirname(__file__), "../models/trained_model.pth"
        )
        fen_path = os.path.join(
            os.path.dirname(__file__), "../fen/mate_in_5.fen"
        )
        if not os.path.exists(stockfish_path):
            logger.error(f"Nie znaleziono silnika Stockfish: {stockfish_path}")
            return

        # Zainicjuj silnik Stockfish
        logger.info(f"Włączanie silnika Stockfish ze ścieżki: {stockfish_path}")
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as stockfish:
            # Zdefiniuj konfigurację planszy
            board_fen = read_fen(fen_path)
            board = chess.Board(board_fen)
            logger.info(f"Początkowe ustawienie:\n{board.unicode()}")

            # Uruchom testy
            logger.info("Rozpoczęcie gier testowych")
            test_agent(agent_white=agent_white, agent_black=agent_black, games=10, board_config=board_fen)

            Q_learning(
                agent_white,
                stockfish,
                games_to_play=1000,
                max_game_moves=5,
                board_config=board_fen,
            )
            agent_white.save_model(model_save_path)
            
            test_agent(agent_white=agent_white, agent_black=agent_black, games=10, board_config=board_fen)


    except Exception as e:
        logger.exception(f"Błąd podczas działania testów lub trenowania: {e}")
    finally:
        logger.info("Testy i trenowanie zakończone.")


if __name__ == "__main__":
    # Skonfiguruj logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    main()
