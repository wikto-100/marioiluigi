import chess
import chess.engine
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ChessEnvironment:
    def __init__(self, agent_color=chess.WHITE, stockfish_path=None, stockfish_depth=5):
        """
        Inicjalizuje środowisko szachowe.

        Parametry:
        - agent_color (chess.Color): Kolor agenta (chess.WHITE lub chess.BLACK).
        - stockfish_path (str): Ścieżka do pliku wykonywalnego silnika Stockfish.
        - stockfish_depth (int): Początkowa głębokość analizy dla Stockfisha.
        """
        self.board = chess.Board()
        self.agent_color = agent_color
        self.stockfish = chess.engine.SimpleEngine.popen_uci(stockfish_path) if stockfish_path else None
        self.stockfish_depth = stockfish_depth  # Dynamiczne zarządzanie głębokością
        if not self.stockfish:
            logger.warning("Silnik Stockfish nie został zainicjalizowany. Przeciwnik i ocena pozycji nie będą działać.")

    def reset(self):
        """
        Resetuje środowisko do początkowego stanu.

        Zwraca:
        - Ocena pozycji (int) lub None, jeśli niedostępna.
        """
        self.board.reset()
        return

    def get_stockfish_evaluation(self):
        """
        Pobiera bieżącą ocenę planszy od Stockfisha.

        Zwraca:
        - Ocena pozycji w centypionach (int) lub None, jeśli silnik jest niedostępny.
        """
        if not self.stockfish:
            logger.warning("Silnik Stockfish nie został zainicjalizowany.")
            return None
        try:
            limit = chess.engine.Limit(depth=self.stockfish_depth)
            info = self.stockfish.analyse(self.board, limit)
            score = info["score"].relative
            if score.is_mate():  # Obsługa ocen mata
                mate_score = 100000 if score.mate() > 0 else -100000
                logger.debug(f"Wykryto mata z oceną: {mate_score}")
                return mate_score
            logger.debug(f"Ocena Stockfisha: {score.score(mate_score=100000)} centypionów")
            return score.score(mate_score=100000)
        except Exception as e:
            logger.error(f"Błąd podczas pobierania oceny od Stockfisha: {e}")
            return None

    def get_opponent_move(self):
        """
        Pobiera ruch przeciwnika generowany przez Stockfisha.

        Zwraca:
        - Ruch przeciwnika (chess.Move) lub None, jeśli wystąpił błąd.
        """
        if not self.stockfish:
            logger.warning("Silnik Stockfish nie został zainicjalizowany.")
            return None
        try:
            limit = chess.engine.Limit(depth=self.stockfish_depth)
            result = self.stockfish.play(self.board, limit)
            if result.move and result.move in self.board.legal_moves:
                logger.debug(f"Ruch przeciwnika Stockfisha: {self.board.san(result.move)}")
                return result.move
            else:
                logger.warning(f"Nieprawidłowy ruch od Stockfisha: {result.move}")
                return None
        except Exception as e:
            logger.error(f"Błąd podczas pobierania ruchu przeciwnika od Stockfisha: {e}")
            return None

    def update_board(self, board):
        """
        Aktualizuje wewnętrzny stan planszy.

        Parametry:
        - board (chess.Board): Zaktualizowana plansza gry.
        """
        self.board = board.copy()
        logger.debug(f"Plansza zaktualizowana: {self.board}")

    def set_depth(self, depth):
        """
        Aktualizuje głębokość analizy Stockfisha.

        Parametry:
        - depth (int): Nowa głębokość analizy dla Stockfisha.
        """
        self.stockfish_depth = depth
        logger.info(f"Głębokość Stockfisha ustawiona na: {self.stockfish_depth}")

    def close(self):
        """
        Zamyka silnik Stockfish.
        """
        if self.stockfish:
            self.stockfish.quit()
            logger.info("Silnik Stockfish zamknięty.")
