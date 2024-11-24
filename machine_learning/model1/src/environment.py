# environment.py

import chess
import chess.engine

class ChessEnvironment:
    def __init__(self, agent_color=chess.WHITE, stockfish_path=None):
        """
        Inicjalizuje środowisko szachowe.

        Parametry:
        - agent_color (chess.Color): Kolor agenta.
        - stockfish_path (str): Ścieżka do pliku wykonywalnego silnika Stockfish.
        """
        self.board = chess.Board()
        self.agent_color = agent_color
        self.stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path) if stockfish_path else None
        self.previous_eval = None

    def reset(self):
        """
        Resetuje środowisko do początkowego stanu.

        Zwraca:
        - Ocena pozycji (int) lub None.
        """
        self.board.reset()
        self.previous_eval = self.get_stockfish_evaluation()
        return self.previous_eval

    def get_stockfish_evaluation(self):
        """
        Pobiera aktualną ocenę pozycji od silnika Stockfish.

        Zwraca:
        - Ocena pozycji w centipawnach (int) lub None, jeśli silnik nie jest dostępny.
        """
        if self.stockfish is None:
            return None
        try:
            limit = chess.engine.Limit(depth=1)
            info = self.stockfish.analyse(self.board, limit)
            score = info["score"].white().score(mate_score=100000)
            if score is not None:
                return score
            else:
                return None
        except Exception as e:
            print(f"Błąd przy pobieraniu oceny od Stockfisha: {e}")
            return None

    def get_opponent_move(self, board):
        """
        Pobiera ruch przeciwnika za pomocą silnika Stockfish.

        Parametry:
        - board (chess.Board): Aktualna plansza gry.

        Zwraca:
        - chess.Move lub None: Ruch przeciwnika.
        """
        if self.stockfish is None:
            return None
        try:
            limit = chess.engine.Limit(time=0.1)  # Dopasuj czas, jeśli potrzebne
            result = self.stockfish.play(board, limit)
            return result.move if result.move in board.legal_moves else None
        except Exception as e:
            print(f"Błąd przy pobieraniu ruchu przeciwnika: {e}")
            return None

    def update_board(self, board):
        """
        Aktualizuje wewnętrzny stan planszy.

        Parametry:
        - board (chess.Board): Zaktualizowana plansza gry.
        """
        self.board = board.copy()

    def close(self):
        """
        Zamyka silnik Stockfish.
        """
        if self.stockfish:
            self.stockfish.quit()
