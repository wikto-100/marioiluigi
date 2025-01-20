import time
import logging
from typing import Optional, List
import pandas as pd
import chess
import matplotlib.pyplot as plt
import random
from chess.engine import Limit
from src.chess_utils import convert_state, mask_and_valid_moves

# Skonfiguruj logowanie
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Ustaw na DEBUG, aby uzyskać bardziej szczegółowe logi

# Utwórz handler konsoli i ustaw poziom na debug
ch_handler = logging.StreamHandler()
ch_handler.setLevel(logging.DEBUG)

# Utwórz formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Dodaj formatter do handlera
ch_handler.setFormatter(formatter)

# Dodaj handler do loggera
if not logger.hasHandlers():
    logger.addHandler(ch_handler)


def calculate_reward(
    final_result: str, board_score_after: Optional[float] = None
) -> float:
    """
    Oblicza nagrodę na podstawie końcowego wyniku gry.

    Argumenty:
        final_result (str): Wynik gry ('1-0', '0-1', '1/2-1/2' lub '*').
        board_score_after (Optional[float]): Wynik planszy po ruchu przeciwnika, jeśli dotyczy.

    Zwraca:
        float: Obliczona nagroda.
    """
    if final_result in ["*", "1/2-1/2"]:
        return -10.0
    elif final_result == "1-0":
        return 1000.0
    elif final_result == "0-1":
        return -1000.0
    elif board_score_after is not None:
        return board_score_after - 0.01
    else:
        logger.warning(
            f"Nierozpoznany wynik gry: {final_result}. Przypisano domyślną ujemną nagrodę."
        )
        return -10.0  # Domyślna ujemna nagroda dla nierozpoznanych wyników


def plot_training_results(
    final_scores: List[float], losses: List[float], games: int, steps: int
) -> None:
    """
    Generuje wykresy wyników treningu, w tym końcowych wyników i strat w czasie.

    Argumenty:
        final_scores (List[float]): Lista końcowych wyników dla każdej gry.
        losses (List[float]): Lista wartości strat z kroków treningowych.
        games (int): Łączna liczba rozegranych gier.
        steps (int): Łączna liczba kroków treningowych.
    """
    try:
        logger.info("Generowanie wykresów treningu...")
        # Przygotuj DataFrames do wykresów
        score_df = pd.DataFrame(final_scores, columns=["score"])
        # Użyj stałego rozmiaru okna dla średniej kroczącej, np. 10
        score_window = 10
        score_df["ma"] = (
            score_df["score"].rolling(window=score_window, min_periods=1).mean()
        )

        loss_df = pd.DataFrame(losses, columns=["loss"])
        # Użyj stałego rozmiaru okna dla średniej kroczącej, np. 100
        loss_window = 100
        loss_df["ma"] = (
            loss_df["loss"].rolling(window=loss_window, min_periods=1).mean()
        )

        # Utwórz wykres z dwoma podwykresami
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Wykres wyników w pierwszym podwykresie
        ax1.plot(score_df.index, score_df["score"], linewidth=0.5, label="Wynik")
        ax1.plot(
            score_df.index, score_df["ma"], linewidth=2, label="Średnia krocząca (10)"
        )
        ax1.set_title("Końcowy wynik według gry")
        ax1.set_xlabel("Numer gry")
        ax1.set_ylabel("Wynik")
        ax1.legend()

        # Wykres strat w drugim podwykresie
        ax2.plot(loss_df.index, loss_df["loss"], linewidth=0.5, label="Strata")
        ax2.plot(
            loss_df.index, loss_df["ma"], linewidth=2, label="Średnia krocząca (100)"
        )
        ax2.set_title("Strata według kroku treningowego")
        ax2.set_xlabel("Krok treningowy")
        ax2.set_ylabel("Strata")
        ax2.legend()

        # Dopasuj układ i wyświetl wykres
        plt.tight_layout()
        plt.show()
        logger.info("Wykresy treningowe wygenerowane pomyślnie.")
    except Exception as e:
        logger.error(f"Błąd podczas generowania wykresów treningu: {e}")


def Q_learning(
    agent,
    stockfish,
    games_to_play: int,
    max_game_moves: int,
    board_config: Optional[str] = None,
) -> None:
    """
    Wykonuje Q-learning, pozwalając agentowi rozegrać gry przeciwko losowemu przeciwnikowi.

    Argumenty:
        agent: Instancja agenta implementującego Q-learning.
        stockfish: Instancja silnika Stockfish do analizy ruchów.
        games_to_play (int): Liczba gier do symulacji.
        max_game_moves (int): Maksymalna liczba ruchów na grę przed zakończeniem.
        board_config (Optional[str]): FEN jako początkowa konfiguracja planszy. Domyślnie standardowa pozycja początkowa.
    """
    loss = []
    final_score = []
    games = 0
    steps = 0
    start_time = time.time()

    logger.info(
        f"Rozpoczęcie Q-learning: {games_to_play} gier, maks. {max_game_moves} ruchów na grę."
    )

    # Rozegraj n gier
    while games < games_to_play:
        games += 1
        logger.debug(f"Rozpoczęcie gry {games}/{games_to_play}")

        # Utwórz nową standardową planszę lub planszę z określoną konfiguracją
        if board_config is None:
            board = chess.Board()
        else:
            try:
                board = chess.Board(board_config)
            except ValueError as e:
                logger.error(f"Nieprawidłowa konfiguracja planszy dla gry {games}: {e}")
                final_score.append(-10.0)
                continue

        done = False
        game_moves = 0

        # Kontynuuj, dopóki gra nie zostanie zakończona
        while not done:
            game_moves += 1
            steps += 1
            # Analizuj planszę za pomocą Stockfish
            try:
                analysis = stockfish.analyse(board=board, limit=Limit(depth=5))
            except Exception as e:
                logger.error(f"Analiza Stockfish nie powiodła się w grze {games}: {e}")
                final_score.append(-10.0)
                continue
            # Wybierz akcję: agent decyduje, czy eksplorować, czy eksploatować
            try:
                action_index, move, bit_state, valid_move_tensor = agent.select_action(
                    board
                )
                logger.debug(
                    f"Gra {games}, Ruch {game_moves}: Agent wybrał ruch {move} (indeks akcji {action_index})"
                )
            except Exception as e:
                logger.error(
                    f"Agent nie zdołał wybrać akcji w grze {games}, ruch {game_moves}: {e}"
                )
                # Przypisz ujemną nagrodę i zakończ grę
                reward = -10.0
                agent.remember(
                    priority=agent.MAX_PRIORITY,
                    state=bit_state if "bit_state" in locals() else None,
                    action=action_index if "action_index" in locals() else None,
                    reward=reward,
                    next_state=None,
                    done=True,
                    valid_moves=(
                        valid_move_tensor if "valid_move_tensor" in locals() else None
                    ),
                    next_valid_moves=None,
                )
                loss.append(agent.learn(debug=False))
                agent.decay_epsilon()
                final_score.append(reward)
                done = True
                break

            # Zapisz aktualny wynik planszy, aby obliczyć nagrodę po ruchu przeciwnika
            try:
                board_score_before = (
                    analysis["score"].relative.score(mate_score=10000) / 100
                )
                logger.debug(
                    f"Gra {games}, Ruch {game_moves}: Wynik planszy przed ruchem: {board_score_before}"
                )
            except AttributeError:
                board_score_before = 0.0
                logger.warning(
                    f"Gra {games}, Ruch {game_moves}: Brak dostępnego wyniku planszy przed ruchem."
                )

            # Białe (agent) wykonują ruch
            try:
                board.push(move)
                logger.debug(
                    f"Gra {games}, Ruch {game_moves}: Białe (agent) wykonują ruch {move}"
                )
            except Exception as e:
                logger.error(
                    f"Nie udało się wykonać ruchu {move} w grze {games}, ruch {game_moves}: {e}"
                )
                # Przypisz ujemną nagrodę i zakończ grę
                reward = -10.0
                agent.remember(
                    priority=agent.MAX_PRIORITY,
                    state=bit_state,
                    action=action_index,
                    reward=reward,
                    next_state=None,
                    done=True,
                    valid_moves=valid_move_tensor,
                    next_valid_moves=None,
                )
                loss.append(agent.learn(debug=False))
                agent.decay_epsilon()
                final_score.append(reward)
                done = True
                break

            # Sprawdź, czy gra została zakończona (szach-mat, pat, remis itp.) lub czy osiągnięto maksymalną liczbę ruchów
            done = board.result() != "*" or game_moves > max_game_moves

            if done:
                final_result = board.result()
                reward = calculate_reward(final_result)
                logger.debug(
                    f"Gra {games}: Zakończona po ruchu agenta z wynikiem {final_result}. Nagroda: {reward}"
                )

                # Zapisz doświadczenie w pamięci agenta
                agent.remember(
                    priority=agent.MAX_PRIORITY,
                    state=bit_state,
                    action=action_index,
                    reward=reward,
                    next_state=None,
                    done=done,
                    valid_moves=valid_move_tensor,
                    next_valid_moves=None,
                )

                # Przypisz nagrodę jako końcowy wynik planszy
                board_score_after = reward
                final_score.append(board_score_after)

            else:
                # Czarne (losowy przeciwnik) wykonują ruch
                try:
                    legal_moves = list(board.legal_moves)
                    if not legal_moves:
                        logger.warning(
                            f"Gra {games}, Ruch {game_moves}: Brak legalnych ruchów dla czarnych."
                        )
                        final_result = board.result()
                        reward = calculate_reward(final_result)
                        agent.remember(
                            priority=agent.MAX_PRIORITY,
                            state=bit_state,
                            action=action_index,
                            reward=reward,
                            next_state=None,
                            done=True,
                            valid_moves=valid_move_tensor,
                            next_valid_moves=None,
                        )
                        loss.append(agent.learn(debug=False))
                        agent.decay_epsilon()
                        final_score.append(reward)
                        done = True
                        break

                    black_move = random.choice(legal_moves)
                    board.push(black_move)
                    logger.debug(
                        f"Gra {games}, Ruch {game_moves}: Czarne (przeciwnik) wykonują ruch {black_move}"
                    )
                except Exception as e:
                    logger.error(
                        f"Nie udało się wybrać/wykonać ruchu czarnych w grze {games}, ruch {game_moves}: {e}"
                    )
                    reward = -10.0
                    agent.remember(
                        priority=agent.MAX_PRIORITY,
                        state=bit_state,
                        action=action_index,
                        reward=reward,
                        next_state=None,
                        done=True,
                        valid_moves=valid_move_tensor,
                        next_valid_moves=None,
                    )
                    loss.append(agent.learn(debug=False))
                    agent.decay_epsilon()
                    final_score.append(reward)
                    done = True
                    break

                # Analizuj planszę po ruchu czarnych
                try:
                    analysis = stockfish.analyse(board=board, limit=Limit(depth=5))
                    board_score_after = (
                        analysis["score"].relative.score(mate_score=10000) / 100
                    )
                    logger.debug(
                        f"Gra {games}, Ruch {game_moves}: Wynik planszy po ruchu czarnych: {board_score_after}"
                    )
                except Exception as e:
                    logger.error(
                        f"Analiza Stockfish nie powiodła się w grze {games}, ruch {game_moves}: {e}"
                    )
                    board_score_after = -10.0  # Przypisz domyślną karę

                # Sprawdź, czy gra została zakończona po ruchu czarnych
                done = board.result() != "*"

                # Przekształć aktualny stan planszy
                try:
                    next_bit_state = convert_state(board)
                    next_valid_move_tensor, _ = mask_and_valid_moves(board)
                    logger.debug(
                        f"Gra {games}, Ruch {game_moves}: Przekształcono kolejny stan planszy."
                    )
                except Exception as e:
                    logger.error(
                        f"Nie udało się przekształcić stanu lub maskować legalnych ruchów w grze {games}, ruch {game_moves}: {e}"
                    )
                    next_bit_state = None
                    next_valid_move_tensor = None

                # Oblicz nagrodę na podstawie wyników planszy
                try:
                    reward = calculate_reward(board.result(), board_score_after)
                    logger.debug(
                        f"Gra {games}, Ruch {game_moves}: Nagroda obliczona jako {reward}"
                    )
                except Exception as e:
                    logger.error(
                        f"Nie udało się obliczyć nagrody w grze {games}, ruch {game_moves}: {e}"
                    )
                    reward = -10.0

                # Zapisz doświadczenie w pamięci agenta
                try:
                    agent.remember(
                        priority=agent.MAX_PRIORITY,
                        state=bit_state,
                        action=action_index,
                        reward=reward,
                        next_state=next_bit_state,
                        done=done,
                        valid_moves=valid_move_tensor,
                        next_valid_moves=next_valid_move_tensor,
                    )
                    logger.debug(
                        f"Gra {games}, Ruch {game_moves}: Doświadczenie zapisane w pamięci."
                    )
                except Exception as e:
                    logger.error(
                        f"Nie udało się zapisać doświadczenia w grze {games}, ruch {game_moves}: {e}"
                    )

                # Trenuj model i zapisz stratę
                try:
                    step_loss = agent.learn(debug=False)
                    loss.append(step_loss)
                    logger.debug(
                        f"Gra {games}, Ruch {game_moves}: Krok treningowy zakończony stratą {step_loss}"
                    )
                except Exception as e:
                    logger.error(
                        f"Trening nie powiódł się w grze {games}, ruch {game_moves}: {e}"
                    )

                # Dostosuj epsilon (wskaźnik eksploracji)
                agent.decay_epsilon()
                logger.debug(f"Gra {games}, Ruch {game_moves}: Epsilon zmniejszony.")

            # Zapisz końcowy wynik gry, jeśli gra nie została zakończona w pętli
            if not done:
                try:
                    final_score.append(board_score_after)
                    logger.debug(
                        f"Gra {games}: Osiągnięto maksymalną liczbę ruchów. Końcowy wynik: {board_score_after}"
                    )
                except Exception as e:
                    logger.error(f"Nie udało się dodać końcowego wyniku dla gry {games}: {e}")
                    final_score.append(-10.0)

    # Wyświetl dyniki treningu po grach
    plot_training_results(final_score, loss, games, steps)

    elapsed_time = time.time() - start_time
    logger.info(
        f"Zakończono Q-learning z {games_to_play} grami w {elapsed_time:.2f} sekund."
    )
