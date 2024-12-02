import logging

import numpy as np
import torch
import chess

from agent import ChessAgent
from environment import ChessEnvironment
from reward import calculate_in_game_reward, calculate_end_game_reward
import os

# Ustaw poziom logowania z zmiennej środowiskowej lub domyślnie na INFO
logging_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, logging_level, logging.INFO))  # Ustaw poziom logowania z zmiennej środowiskowej
logger = logging.getLogger(__name__)

def train_agent(num_episodes=1000, max_moves=100, agent_color=chess.WHITE, device='cpu',
                save_every=100, window_size=50, save_path='chess_agent_checkpoint.pth',
                best_save_path='best_chess_agent_checkpoint.pth',
                load_checkpoint=None, stockfish_path=None, mcts_binary_path=None,
                learning_rate=0.0001, gamma=0.95, entropy_coef=0.05,
                initial_epsilon=1.0, final_epsilon=0.1, decay_rate=0.7):
    """
    Trenuj agenta szachowego przez określoną liczbę epizodów, korzystając z epsilon-greedy.

    Dodatkowe funkcje:
    - Implementacja nowej funkcji nagrody, uwzględniającej oceny, materiał i pozycję.
    - Stopniowe zwiększanie głębokości Stockfisha.

    Zwraca:
    - rewards_history (list): Całkowite nagrody na epizod.
    - moving_avg (list): Średnia ruchoma nagród na przestrzeni epizodów.
    """
    # Inicjalizacja ChessAgent
    agent = ChessAgent(agent_color=agent_color, device=device, mcts_binary_path=mcts_binary_path,
                       lr=learning_rate, gamma=gamma, entropy_coef=entropy_coef)

    # Inicjalizacja ChessEnvironment
    env = ChessEnvironment(agent_color=agent_color, stockfish_path=stockfish_path)

    # Wczytaj checkpoint, jeśli podano
    if load_checkpoint:
        agent.load_model(load_checkpoint)
        checkpoint = torch.load(load_checkpoint, map_location=device)
        rewards_history = checkpoint.get('rewards_history', [])
        logger.info(f"Checkpoint wczytany z {load_checkpoint}")
    else:
        rewards_history = []
        logger.info("Brak wczytanego checkpointa. Rozpoczynanie treningu od zera.")

    # Inicjalizacja średniej ruchomej
    moving_avg = []
    for i in range(1, len(rewards_history) + 1):
        avg_reward = np.mean(rewards_history[max(0, i - window_size):i])
        moving_avg.append(avg_reward)

    # Inicjalizacja zmiennych
    start_episode = len(rewards_history) + 1
    epsilon = initial_epsilon
    current_depth = 5
    depth_update_interval = 10000

    try:
        for episode in range(start_episode, start_episode + num_episodes):
            print(f"--- Epizod {episode} ---")
            env.reset()
            move_count = 0
            total_reward = 0.0
            previous_eval = env.get_stockfish_evaluation()

            while not env.board.is_game_over() and move_count < max_moves:
                print(env.board)
                print("\nBieżący ruch:", move_count + 1)

                if env.board.turn == agent.agent_color:
                    # Ruch agenta
                    move = agent.select_move(env.board, epsilon=epsilon)

                    if move is None:
                        print("Brak dostępnych legalnych ruchów dla agenta.")
                        break

                    previous_board = env.board.copy()
                    env.board.push(move)
                    env.update_board(env.board)

                    last_move = move
                    current_eval = env.get_stockfish_evaluation()

                    # Oblicz nagrodę w trakcie gry
                    reward = calculate_in_game_reward(
                        previous_eval=previous_eval,
                        current_eval=current_eval,
                        agent_color=agent.agent_color,
                        previous_board=previous_board,
                        current_board=env.board.copy(),
                        last_move=last_move
                    )
                    total_reward += reward
                    agent.remember(reward)

                    # Nauka krokowa po każdym ruchu
                    agent.learn()

                    previous_eval = current_eval
                    move_count += 1

                else:
                    # Ruch przeciwnika (Stockfish)
                    move = env.get_opponent_move()
                    if move is None:
                        print("Brak dostępnych legalnych ruchów dla przeciwnika.")
                        break

                    env.board.push(move)
                    env.update_board(env.board)
                    move_count += 1

            # Nagroda końca gry
            game_result = env.board.result()
            end_game_reward = calculate_end_game_reward(agent.agent_color, game_result)
            total_reward += end_game_reward
            agent.remember(end_game_reward)

            # Końcowy krok nauki
            agent.learn()

            print(f"Nagroda końca gry: {end_game_reward}")
            print(f"Wynik końcowy: {game_result}")
            print(f"Całkowita nagroda: {total_reward}")

            rewards_history.append(total_reward)
            avg_reward = np.mean(rewards_history[-window_size:]) if len(rewards_history) >= window_size else np.mean(rewards_history)
            moving_avg.append(avg_reward)

            # Zapisz najlepszy model na podstawie średniej ruchomej
            if best_save_path and avg_reward > max(moving_avg[:-1], default=-float('inf')):
                agent.save_model(best_save_path, episode=episode, rewards_history=rewards_history)
                logger.info(f"Najlepszy model zapisany do {best_save_path}")

            # Okresowy zapis modelu
            if save_path and episode % save_every == 0:
                agent.save_model(filepath=save_path, episode=episode, rewards_history=rewards_history)
                logger.info(f"Checkpoint zapisany do {save_path}")

            # Redukcja epsilonu
            epsilon = max(final_epsilon, epsilon * decay_rate)

            # Okresowa aktualizacja głębokości Stockfisha
            if episode % depth_update_interval == 0:
                current_depth += 1
                env.set_depth(current_depth)
                logger.info(f"Głębokość Stockfisha zwiększona do {current_depth}")

    except KeyboardInterrupt:
        logger.info("Trening przerwany przez użytkownika.")
    except Exception as e:
        logger.error(f"Wystąpił błąd: {e}")
    finally:
        env.close()
        agent.close_mcts()
        logger.info("ChessEnvironment zamknięte.")

    return rewards_history, moving_avg
