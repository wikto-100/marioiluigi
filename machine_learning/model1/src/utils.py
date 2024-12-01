# utils.py

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_rewards(rewards_history, moving_avg, window_size=50, save_fig=False, fig_path='training_progress.png'):
    """
    Rysuje wykres nagród treningowych oraz ich średniej kroczącej.

    Parametry:
    - rewards_history (lista float): Całkowite nagrody z każdego epizodu.
    - moving_avg (lista float): Średnia krocząca nagród.
    - window_size (int): Rozmiar okna dla średniej kroczącej.
    - save_fig (bool): Czy zapisać wykres jako plik.
    - fig_path (str): Ścieżka do zapisania wykresu.
    """
    sns.set(style="whitegrid")  # Ulepszenie estetyki wykresu przy użyciu Seaborn
    episodes = np.arange(1, len(rewards_history) + 1)
    plt.figure(figsize=(12, 6))
    
    # Rysowanie całkowitych nagród
    plt.plot(episodes, rewards_history, label='Całkowita Nagroda', color='blue', alpha=0.6)
    
    # Rysowanie średniej kroczącej
    plt.plot(episodes, moving_avg, label=f'Średnia Nagroda ({window_size} epizodów)', color='orange', linewidth=2)
    
    # Ustawienia wykresu
    plt.xlabel('Epizod')
    plt.ylabel('Całkowita Nagroda')
    plt.title('Postępy Agenta w Procesie Uczenia')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    if save_fig:
        plt.savefig(fig_path)
        print(f"Wykres zapisany do {fig_path}")
    
    plt.show()

def plot_hyperparameter_results(results, hyperparams, metric='average_reward', save_fig=False, fig_path='hyperparameter_tuning_results.png'):
    """
    Rysuje wyniki dostrojenia hiperparametrów.
    
    Parametry:
    - results (lista dict): Każdy słownik zawiera hiperparametry i odpowiadającą im metrykę.
    - hyperparams (lista str): Nazwy strojonowanych hiperparametrów.
    - metric (str): Metryka wydajności do narysowania.
    - save_fig (bool): Czy zapisać wykres jako plik.
    - fig_path (str): Ścieżka do zapisania wykresu.
    """
    sns.set(style="whitegrid")
    
    # Konwersja wyników do uporządkowanych danych do rysowania
    data = {param: [] for param in hyperparams}
    data[metric] = []
    
    for entry in results:
        for param in hyperparams:
            data[param].append(entry[param])
        data[metric].append(entry[metric])
    
    # Rysowanie
    num_hyperparams = len(hyperparams)
    
    plt.figure(figsize=(6 * num_hyperparams, 6))
    
    for idx, param in enumerate(hyperparams, 1):
        plt.subplot(1, num_hyperparams, idx)
        sns.scatterplot(x=param, y=metric, data=data, hue=metric, palette='viridis', size=metric, legend=False)
        plt.title(f'{metric} vs {param}')
        plt.xlabel(param)
        plt.ylabel(metric)
    
    plt.tight_layout()
    
    if save_fig:
        plt.savefig(fig_path)
        print(f"Wyniki dostrojenia hiperparametrów zapisane do {fig_path}")
    
    plt.show()
