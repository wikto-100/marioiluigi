# training.py

import numpy as np
import torch
import chess
from agent import ChessAgent
from environment import ChessEnvironment
from reward import calculate_reward
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)  # Ustaw na DEBUG dla szczegółowych logów podczas testów
logger = logging.getLogger(__name__)

def train_agent(num_episodes=1000, max_moves=100, agent_color=chess.WHITE, device='cpu',
               save_every=100, window_size=50, save_path='chess_agent_checkpoint.pth', best_save_path='best_chess_agent_checkpoint.pth',
               load_checkpoint=None, stockfish_path=None, mcts_binary_path=None,
               learning_rate=0.0001, gamma=0.95, entropy_coef=0.05,
               initial_epsilon=1.0, final_epsilon=0.1, decay_rate=0.996):
    """
    Trenuje agenta szachowego przez określoną liczbę epizodów z wykorzystaniem strategii epsilon-zachłannej.

    Parametry:
    - num_episodes (int): Liczba epizodów treningowych.
    - max_moves (int): Maksymalna liczba ruchów na grę.
    - agent_color (chess.Color): Kolor agenta (chess.WHITE lub chess.BLACK).
    - device (str): Urządzenie do uruchamiania modelu ('cpu' lub 'cuda').
    - save_every (int): Częstotliwość (w epizodach) zapisywania punktu kontrolnego modelu.
    - save_path (str): Ścieżka do zapisu punktu kontrolnego modelu.
    - best_save_path (str): Ścieżka do zapisu najlepszego punktu kontrolnego modelu na podstawie średniej ruchomej.
    - load_checkpoint (str, opcjonalnie): Ścieżka do załadowania istniejącego punktu kontrolnego przed treningiem.
    - stockfish_path (str, opcjonalnie): Ścieżka do wykonywalnego pliku silnika Stockfish.
    - mcts_binary_path (str, opcjonalnie): Ścieżka do binarnego pliku MCTS, jeśli dotyczy.
    - learning_rate (float): Współczynnik uczenia dla optymalizatora.
    - gamma (float): Współczynnik dyskontowania przyszłych nagród.
    - entropy_coef (float): Współczynnik regularyzacji entropii.
    - initial_epsilon (float): Początkowa wartość epsilon w strategii epsilon-zachłannej.
    - final_epsilon (float): Minimalna wartość epsilon po procesie redukcji.
    - decay_rate (float): Mnożnik redukcji epsilon na epizod.

    Zwraca:
    - rewards_history (list): Lista całkowitych nagród na epizod.
    - moving_avg (list): Średnia ruchoma nagród w oknie epizodów.
    """
    # Inicjalizuj ChessAgent z hiperparametrami
    agent = ChessAgent(agent_color=agent_color, device=device, mcts_binary_path=mcts_binary_path,
                      lr=learning_rate, gamma=gamma, entropy_coef=entropy_coef)

    # Inicjalizuj ChessEnvironment
    env = ChessEnvironment(agent_color=agent_color, stockfish_path=stockfish_path)

    # Załaduj punkt kontrolny modelu, jeśli podano
    if load_checkpoint is not None:
        agent.load_model(load_checkpoint)
        checkpoint = torch.load(load_checkpoint, map_location=device)
        rewards_history = checkpoint.get('rewards_history', [])
        logger.info(f"Punkt kontrolny załadowany z {load_checkpoint}")
    else:
        rewards_history = []
        logger.info("Brak załadowanego punktu kontrolnego. Trening rozpoczyna się od zera.")

    # Oblicz początkową średnią ruchomą
    moving_avg = []
    for i in range(1, len(rewards_history) + 1):
        if i >= window_size:
            avg_reward = np.mean(rewards_history[i - window_size:i])
        else:
            avg_reward = np.mean(rewards_history[:i])
        moving_avg.append(avg_reward)

    # Określ początkowy epizod
    start_episode = len(rewards_history) + 1

    # Inicjalizuj epsilon dla strategii epsilon-zachłannej
    epsilon = initial_epsilon


    try:
        for episode in range(start_episode, start_episode + num_episodes):
            print(f"--- Epizod {episode} ---")
            state = env.reset()  # Resetuje środowisko i zwraca początkową ocenę
            board = env.board.copy()  # Aktualny stan planszy
            move_count = 0
            total_reward = 0.0

            # Inicjalizacja previous_eval do śledzenia
            previous_eval = env.get_stockfish_evaluation()

            while not board.is_game_over() and move_count < max_moves:
                print(board)
                print("\nAktualny ruch:", move_count + 1)

                if board.turn == agent.agent_color:
                    # Tura agenta
                    # Agent wybiera ruch za pomocą strategii epsilon-zachłannej
                    move = agent.select_move(board, epsilon=epsilon)

                    if move is None:
                        print("Brak dostępnych ruchów dla agenta.")
                        break

                    player = "Agent (Białe)" if agent.agent_color == chess.WHITE else "Agent (Czarne)"
                    print(f"{player} wykonuje ruch: {board.san(move)}")

                    # Zapisz previous_board przed wykonaniem ruchu
                    previous_board = board.copy()

                    # Wykonaj ruch
                    board.push(move)
                    env.update_board(board)  # Aktualizuj planszę w środowisku

                    # Zapisz last_move do obliczenia nagrody
                    last_move = move

                    # Pobierz ocenę pozycji po ruchu
                    current_eval = env.get_stockfish_evaluation()
                    if current_eval is not None:
                        print(f"Ocena Stockfish: {current_eval} centipawnów")
                    else:
                        print("Brak oceny od Stockfish.")

                    # Sprawdź, czy gra się zakończyła, i uzyskaj wynik
                    done = board.is_game_over()
                    game_result = board.result() if done else None

                    # Oblicz nagrodę za pomocą zaktualizowanej funkcji
                    reward = calculate_reward(
                        previous_eval=previous_eval,
                        current_eval=current_eval,
                        agent_color=agent.agent_color,
                        game_result=game_result,  # Przekaż wynik gry, jeśli gra się zakończyła
                        previous_board=previous_board,
                        current_board=board.copy(),
                        last_move=last_move
                    )
                    print(f"Nagroda: {reward} (znormalizowana)\n")

                    # Zapisz nagrodę
                    agent.remember(reward)
                    total_reward += reward

                    # Zaktualizuj poprzednią ocenę
                    previous_eval = current_eval

                    move_count += 1

                    if done:
                        print("Koniec gry.")
                        break

                else:
                    # Tura przeciwnika (Stockfish)
                    # Zapisz previous_board przed ruchem przeciwnika
                    previous_board = board.copy()

                    move = env.get_opponent_move(board)
                    if move is None:
                        print("Brak dostępnych ruchów dla przeciwnika.")
                        break

                    player = "Stockfish (Czarne)" if agent.agent_color == chess.WHITE else "Stockfish (Białe)"
                    print(f"{player} wykonuje ruch: {board.san(move)}")

                    # Wykonaj ruch
                    board.push(move)
                    env.update_board(board)  # Aktualizuj planszę w środowisku

                    # Zapisz last_move dla ewentualnej korekty nagrody
                    last_move = move

                    # Pobierz ocenę pozycji po ruchu przeciwnika
                    current_eval = env.get_stockfish_evaluation()

                    # Sprawdź, czy gra się zakończyła, i uzyskaj wynik
                    done = board.is_game_over()
                    game_result = board.result() if done else None

                    if done:
                        # Oblicz ostateczną nagrodę i dostosuj ostatnią nagrodę agenta
                        final_reward = calculate_reward(
                            previous_eval=previous_eval,
                            current_eval=current_eval,
                            agent_color=agent.agent_color,
                            game_result=game_result,
                            previous_board=previous_board,
                            current_board=board.copy(),
                            last_move=last_move
                        )
                        print(f"Ostateczna nagroda: {final_reward} (znormalizowana)\n")

                        if len(agent.rewards) > 0:
                            agent.rewards[-1] += final_reward
                            total_reward += final_reward
                        else:
                            # Pierwszy ruch w grze, agent jeszcze nie wykonał ruchu
                            agent.remember(final_reward)
                            total_reward += final_reward

                        print("Koniec gry.")
                        break

                    # Zaktualizuj poprzednią ocenę
                    previous_eval = current_eval

                    move_count += 1

            print("Ostateczny wynik:", board.result())
            print(f"Całkowita nagroda: {total_reward} (suma znormalizowanych nagród)")

            # Dodaj całkowitą nagrodę do historii
            rewards_history.append(total_reward)

            # Oblicz średnią ruchomą nagród
            if len(rewards_history) >= window_size:
                avg_reward = np.mean(rewards_history[-window_size:])
            else:
                avg_reward = np.mean(rewards_history)
            moving_avg.append(avg_reward)

            # Sprawdź, czy aktualna średnia jest najlepsza dotychczas
            if best_save_path is not None:
                if avg_reward > (np.max(moving_avg[:-1]) if len(moving_avg) > 1 else -float('inf')):
                    agent.save_model(best_save_path, episode=episode, rewards_history=rewards_history)
                    print(f"Zapisano nowy najlepszy model do {best_save_path}")

            # Trenuj agenta po grze
            agent.learn()
            print("Model zaktualizowany na podstawie doświadczeń.\n")

            if save_path is not None:
                # Zapisuj model co 'save_every' epizodów
                if episode % save_every == 0:
                    agent.save_model(filepath=save_path, episode=episode, rewards_history=rewards_history)
                    print(f"Punkt kontrolny modelu zapisany do {save_path}")

            # Zmniejsz epsilon (strategia epsilon-zachłanna)
            epsilon = max(final_epsilon, epsilon * decay_rate)

    except KeyboardInterrupt:
        print("Trening przerwany przez użytkownika.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        # Zamknij silnik Stockfish po treningu
        env.close()
        print("ChessEnvironment został zamknięty.")

    # Zwróć historię nagród i średnich ruchomych
    return rewards_history, moving_avg
