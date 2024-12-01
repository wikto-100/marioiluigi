# monitor.py

import os
import itertools
import json
import numpy as np
import chess
import argparse
from training import train_agent
from utils import plot_rewards, plot_hyperparameter_results

def main():
    dirname = os.path.dirname(__file__)
    # Domyślna ścieżka do załadowania modelu
    default_load_path = None
    default_save_path = os.path.join(dirname, 'models', 'chess_agent_checkpoint.pth')
    default_best_save_path = os.path.join(dirname, 'best_models', 'best_chess_agent_checkpoint.pth')
    default_fig_path = os.path.join(dirname, 'training_progress.png')
    default_stockfish_path = os.path.join(dirname, 'stockfish', 'stockfish-ubuntu-x86-64')
    
    parser = argparse.ArgumentParser(description='Trenuj, monitoruj i stroń hiperparametry agenta szachowego')
    
    # Wybór trybu
    parser.add_argument('--mode', type=str, choices=['train', 'tune'], default='train',
                        help='Tryb działania: "train" dla treningu i monitorowania, "tune" dla dostrojenia hiperparametrów')
    
    # Wspólne argumenty treningowe
    parser.add_argument('--num_episodes', type=int, default=500, help='Liczba epizodów treningowych')
    parser.add_argument('--max_moves', type=int, default=100, help='Maksymalna liczba ruchów w jednej grze')
    parser.add_argument('--agent_color', type=str, choices=['white', 'black'], default='white', help='Kolor agenta')
    parser.add_argument('--device', type=str, default='cpu', choices=['cpu', 'cuda'], help='Urządzenie do uruchomienia modelu')
    parser.add_argument('--save_every', type=int, default=100, help='Liczba epizodów między zapisami modelu')
    parser.add_argument('--load_checkpoint', type=str, default=default_load_path, help='Ścieżka do wczytania wcześniej wytrenowanego modelu')
    
    # Argumenty związane z wykresami
    parser.add_argument('--plot_window', type=int, default=50, help='Rozmiar okna dla wykresu średniej kroczącej')
    parser.add_argument('--save_plot', action='store_true', help='Czy zapisać wykres jako plik')
    parser.add_argument('--fig_path', type=str, default=default_fig_path, help='Ścieżka do zapisania wykresu treningowego')
    
    # Ścieżki
    parser.add_argument('--save_path', type=str, default=default_save_path, help='Ścieżka do zapisania wytrenowanego modelu')
    parser.add_argument('--best_save_path', type=str, default=default_best_save_path, help='Ścieżka do zapisania najlepszego modelu')
    parser.add_argument('--stockfish_path', type=str, default=default_stockfish_path, help='Ścieżka do pliku wykonywalnego Stockfish')
    parser.add_argument('--mcts_binary_path', type=str, default=None, help='Ścieżka do zewnętrznego pliku binarnego MCTS')
    
    # Argumenty dostrojenia hiperparametrów (tylko w trybie "tune")
    parser.add_argument('--learning_rates', type=float, nargs='+', default=[1e-3, 5e-4, 1e-4],
                        help='Lista współczynników uczenia do sprawdzenia podczas dostrojenia')
    parser.add_argument('--gammas', type=float, nargs='+', default=[0.95, 0.99, 0.995],
                        help='Lista wartości gamma do sprawdzenia podczas dostrojenia')
    parser.add_argument('--entropy_coefs', type=float, nargs='+', default=[0.0, 0.01, 0.05],
                        help='Lista współczynników entropii do sprawdzenia podczas dostrojenia')
    parser.add_argument('--initial_epsilons', type=float, nargs='+', default=[1.0, 0.9, 0.8],
                        help='Lista początkowych wartości epsilon do sprawdzenia podczas dostrojenia')
    parser.add_argument('--final_epsilons', type=float, nargs='+', default=[0.1, 0.05],
                        help='Lista końcowych wartości epsilon do sprawdzenia podczas dostrojenia')
    parser.add_argument('--decay_rates', type=float, nargs='+', default=[0.995, 0.99],
                        help='Lista współczynników rozkładu do sprawdzenia podczas dostrojenia')
    parser.add_argument('--window_size', type=int, default=50, help='Rozmiar okna średniej kroczącej podczas strojenia')
    parser.add_argument('--save_tuned_plot', action='store_true', help='Czy zapisać wykres dostrojenia hiperparametrów jako plik')
    parser.add_argument('--tuned_fig_path', type=str, default=os.path.join(dirname, 'hyperparameter_tuning_results.png'),
                        help='Ścieżka do zapisania wykresu dostrojenia hiperparametrów')
    parser.add_argument('--results_path', type=str, default='hyperparameter_tuning_results.json',
                        help='Ścieżka do zapisania wyników dostrojenia hiperparametrów')
    
    args = parser.parse_args()
    
    # Konwersja agent_color na chess.Color
    agent_color = chess.WHITE if args.agent_color.lower() == 'white' else chess.BLACK
    
    if args.mode == 'train':
        # Rozpoczęcie treningu
        rewards_history, moving_avg = train_agent(
            num_episodes=args.num_episodes, 
            max_moves=args.max_moves, 
            agent_color=agent_color, 
            device=args.device, 
            save_every=args.save_every, 
            save_path=args.save_path, 
            best_save_path=args.best_save_path, 
            load_checkpoint=args.load_checkpoint,
            stockfish_path=args.stockfish_path,
            mcts_binary_path=args.mcts_binary_path
        )
        # Tworzenie wykresu postępu treningu
        plot_rewards(
            rewards_history, 
            moving_avg, 
            window_size=args.plot_window, 
            save_fig=args.save_plot, 
            fig_path=args.fig_path
        )
    
    elif args.mode == 'tune':
        # Definiowanie kombinacji hiperparametrów przy użyciu Grid Search
        hyperparameter_combinations = list(itertools.product(
            args.learning_rates,
            args.gammas,
            args.entropy_coefs,
            args.initial_epsilons,
            args.final_epsilons,
            args.decay_rates
        ))
        
        total_combinations = len(hyperparameter_combinations)
        print(f"Liczba kombinacji hiperparametrów do sprawdzenia: {total_combinations}")
        
        # Inicjalizacja listy do przechowywania wyników dostrojenia
        tuning_results = []
        
        for idx, (lr, gamma, entropy_coef, initial_epsilon, final_epsilon, decay_rate) in enumerate(hyperparameter_combinations, 1):
            print(f"\n--- Zestaw hiperparametrów {idx}/{total_combinations} ---")
            print(f"Współczynnik uczenia: {lr}, Gamma: {gamma}, Współczynnik entropii: {entropy_coef}, "
                  f"Początkowy Epsilon: {initial_epsilon}, Końcowy Epsilon: {final_epsilon}, Współczynnik rozkładu: {decay_rate}")
            
            # Trenowanie agenta z bieżącymi hiperparametrami
            rewards_history, moving_avg = train_agent(
                num_episodes=args.num_episodes, 
                max_moves=args.max_moves, 
                agent_color=agent_color, 
                device=args.device, 
                save_path=None, 
                best_save_path=None, 
                load_checkpoint=args.load_checkpoint,
                stockfish_path=args.stockfish_path,
                mcts_binary_path=args.mcts_binary_path,
                learning_rate=lr,
                gamma=gamma,
                entropy_coef=entropy_coef,
                initial_epsilon=initial_epsilon,
                final_epsilon=final_epsilon,
                decay_rate=decay_rate
            )
            
            # Ocena wydajności (średnia nagroda z ostatnich args.plot_window epizodów)
            if len(moving_avg) >= args.plot_window:
                average_reward = np.mean(moving_avg[-args.plot_window:])
            else:
                average_reward = np.mean(moving_avg)
            
            print(f"Średnia nagroda z ostatnich {args.plot_window} epizodów: {average_reward}")
            
            # Przechowywanie wyników
            result_entry = {
                'learning_rate': lr,
                'gamma': gamma,
                'entropy_coef': entropy_coef,
                'initial_epsilon': initial_epsilon,
                'final_epsilon': final_epsilon,
                'decay_rate': decay_rate,
                'average_reward': average_reward
            }
            tuning_results.append(result_entry)
        
        # Zapisanie wyników dostrojenia do pliku JSON
        with open(args.results_path, 'w') as f:
            json.dump(tuning_results, f, indent=4)
        print(f"\nWyniki dostrojenia zapisane do {args.results_path}")
        
        # Tworzenie wykresu wyników dostrojenia
        plot_hyperparameter_results(
            results=tuning_results, 
            hyperparams=['learning_rate', 'gamma', 'entropy_coef', 'initial_epsilon', 'final_epsilon', 'decay_rate'], 
            metric='average_reward',
            save_fig=args.save_tuned_plot, 
            fig_path=args.tuned_fig_path
        )
        
        # Identyfikacja i raportowanie najlepszego zestawu hiperparametrów
        best_result = max(tuning_results, key=lambda x: x['average_reward'])
        print("\nNajlepszy zestaw hiperparametrów:")
        print(f"Współczynnik uczenia: {best_result['learning_rate']}")
        print(f"Gamma: {best_result['gamma']}")
        print(f"Współczynnik entropii: {best_result['entropy_coef']}")
        print(f"Początkowy Epsilon: {best_result['initial_epsilon']}")
        print(f"Końcowy Epsilon: {best_result['final_epsilon']}")
        print(f"Współczynnik rozkładu: {best_result['decay_rate']}")
        print(f"Średnia nagroda: {best_result['average_reward']}")
    
if __name__ == "__main__":
    main()
