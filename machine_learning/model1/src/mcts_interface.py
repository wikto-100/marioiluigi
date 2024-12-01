# mcts_interface.py
import subprocess
import shlex
import chess
import logging
import os

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCTSInterface:
    def __init__(self, mcts_binary_path='./mcts_engine', timeout=5.0):
        """
        Inicjalizuje interfejs MCTS.
        
        Parametry:
        - mcts_binary_path (str): Ścieżka do pliku wykonywalnego binarnego MCTS w C++.
        - timeout (float): Maksymalny czas oczekiwania na odpowiedź programu w sekundach.
        """
        self.mcts_binary_path = mcts_binary_path
        self.timeout = timeout
        self.process = None

        if mcts_binary_path and os.path.isfile(mcts_binary_path) and os.access(mcts_binary_path, os.X_OK):
            try:
                self.process = subprocess.Popen(
                    shlex.split(self.mcts_binary_path),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1  # Buforowanie wierszowe
                )
                logger.info("Silnik MCTS uruchomiony pomyślnie.")
            except Exception as e:
                logger.error(f"Nie udało się uruchomić silnika MCTS: {e}")
                self.process = None
        else:
            if mcts_binary_path:
                logger.warning(f"Nie znaleziono pliku binarnego MCTS lub nie jest on wykonywalny: {mcts_binary_path}")
            else:
                logger.info("Nie podano ścieżki do binarnego MCTS.")

    def get_move(self, fen):
        """
        Wysyła FEN do silnika MCTS i pobiera najlepszy ruch.
        
        Parametry:
        - fen (str): FEN reprezentujący aktualny stan planszy.
        
        Zwraca:
        - str lub None: Ruch w formacie UCI, jeśli ok, w przeciwnym razie None.
        """
        if not self.process:
            logger.debug("Proces silnika MCTS nie jest dostępny.")
            return None

        try:
            # Wysyłanie FEN zakończonego nową linią
            self.process.stdin.write(fen + '\n')
            self.process.stdin.flush()
            
            # Odczyt ruchu z stdout
            move = self.process.stdout.readline().strip()
            
            if not move:
                logger.error("Nie otrzymano ruchu od silnika MCTS.")
                return None
            
            # Walidacja ruchu
            board = chess.Board(fen)
            try:
                selected_move = chess.Move.from_uci(move)
                if selected_move in board.legal_moves:
                    logger.info(f"Silnik MCTS wybrał ruch: {move}")
                    return move
                else:
                    logger.error(f"Nielegalny ruch od silnika MCTS: {move}")
                    return None
            except ValueError:
                logger.error(f"Nieprawidłowy ruch UCI od silnika MCTS: {move}")
                return None
        
        except subprocess.TimeoutExpired:
            logger.error("Przekroczono czas oczekiwania na odpowiedź silnika MCTS.")
            return None
        except Exception as e:
            logger.error(f"Błąd w komunikacji z silnikiem MCTS: {e}")
            return None

    def close(self):
        """
        Zamyka proces silnika MCTS.
        """
        if self.process:
            try:
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("Silnik MCTS zakończył działanie poprawnie.")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("Silnik MCTS został zamknięty z powodu przekroczenia limitu czasu.")
            except Exception as e:
                logger.error(f"Błąd podczas zamykania silnika MCTS: {e}")
            finally:
                self.process = None
