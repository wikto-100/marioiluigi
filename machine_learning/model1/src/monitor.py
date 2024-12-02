import os
import argparse
from training import train_agent
from utils import plot_rewards
import chess

def main():
    dirname = os.path.dirname(__file__)
    # Domyślne ścieżki
    default_load_path = None  # os.path.join(dirname, 'models', 'chess_agent_checkpoint.pth')
    default_save_path = os.path.join(dirname,'..', 'models', 'chess_agent_checkpoint.pth')
    default_best_save_path = os.path.join(dirname, '..', 'best_models', 'best_chess_agent_checkpoint.pth')
    default_fig_path = os.path.join(dirname, 'training_progress.png')
    default_stockfish_path = os.path.join(dirname, '..', 'stockfish', 'stockfish-ubuntu-x86-64')
    default_mcts_path = None #os.path.join(dirname, 'mcts', 'mcts_engine')

    parser = argparse.ArgumentParser(description='Trenuj i monitoruj agenta szachowego')

    # Argumenty treningu
    parser.add_argument('--num_episodes', type=int, default=50, help='Liczba epizodów treningowych')
    parser.add_argument('--max_moves', type=int, default=100, help='Maksymalna liczba ruchów na grę')
    parser.add_argument('--agent_color', type=str, choices=['white', 'black'], default='white', help='Kolor agenta')
    parser.add_argument('--device', type=str, default='cuda', choices=['cpu', 'cuda'], help='Urządzenie do treningu')
    parser.add_argument('--save_every', type=int, default=100, help='Liczba epizodów pomiędzy zapisami modelu')
    parser.add_argument('--load_checkpoint', type=str, default=default_load_path, help='Ścieżka do wczytania wcześniej wytrenowanego modelu')

    # Argumenty wizualizacji
    parser.add_argument('--plot_window', type=int, default=10, help='Rozmiar okna dla wykresu średniej ruchomej')
    parser.add_argument('--save_plot', action='store_true', help='Zapisz wykres postępu treningu do pliku')
    parser.add_argument('--fig_path', type=str, default=default_fig_path, help='Ścieżka do zapisu wykresu postępu treningu')

    # Ścieżki
    parser.add_argument('--save_path', type=str, default=default_save_path, help='Ścieżka do zapisu wytrenowanego modelu')
    parser.add_argument('--best_save_path', type=str, default=default_best_save_path, help='Ścieżka do zapisu najlepszego modelu')
    parser.add_argument('--stockfish_path', type=str, default=default_stockfish_path, help='Ścieżka do wykonywalnego pliku Stockfish')
    parser.add_argument('--mcts_binary_path', type=str, default=default_mcts_path, help='Ścieżka do pliku binarnego silnika MCTS')

    args = parser.parse_args()

    # Konwersja koloru agenta na chess.Color
    agent_color = chess.WHITE if args.agent_color.lower() == 'white' else chess.BLACK

    # Rozpocznij trening
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

    # Wykres postępu treningu
    plot_rewards(
        rewards_history,
        moving_avg,
        window_size=args.plot_window,
        save_fig=args.save_plot,
        fig_path=args.fig_path
    )

if __name__ == "__main__":
    main()
