import os
import random
import logging

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from src.luigi_cnn import LuigiCNN
from src.chess_utils import get_move_index, convert_state, mask_and_valid_moves
from mcts.mcts_interface import get_best_move as Mario_get_best_move

"""A"""
from src.openings.add_openings import get_openings
"""A"""


class ChessAgent:
    def __init__(self, input_model_path=None, name=None, use_openings=True):
        self.name = name
        
        """A"""
        if use_openings:
            self.openings_dict = get_openings()
        else:
            self.openings_dict = {}
        """A"""

        # Parametry eksploracji
        self.epsilon = 1
        self.epsilon_decay = 0.99
        self.epsilon_min = 0.01

        # Parametry treningu
        self.gamma = 0.5  # określa, czy agent preferuje długoterminowe nagrody czy natychmiastowe. 0 = zachłanne, 1 = długoterminowe
        self.learning_rate = 1e-03  # jak szybko sieć aktualizuje swoje wagi
        self.MEMORY_SIZE = 512  # ile kroków/ruchów/próbek przechowywać. Używane do treningu (doświadczenie odtwarzania)
        self.MAX_PRIORITY = 1e06  # maksymalny priorytet próbki w pamięci. Im wyższy priorytet, tym bardziej prawdopodobne, że próbka zostanie uwzględniona w treningu
        self.memory = []  # struktura danych pamięci
        self.batch_size = 16  # ile próbek uwzględnić w kroku treningowym
        
        # Parametry MCTS
        # Obs: aby nauczyć agenta mata w 5, bez MCTS zajmuje to ~1000 gier. Z mcts-prawdop. na 0.3, jest to ok. 100 gier
        # Więc MCTS jest rzeczywiście dobry
        self.mcts_move_prob = 0.3  # prawdopodobieństwo wyboru najlepszego ruchu za pomocą MCTS
        self.mcts_iterations = 100 # ile razy wykonać algorytm MCTS
        self.mcts_rollout_depth = 5 # jak głębokie są losowe symulacje w MCTS
        
        # **1. Wykryj i ustaw urządzenie (GPU, jeśli dostępne, w przeciwnym razie CPU)**
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logging.info(f"Używane urządzenie: {self.device}")

        # Inicjalizuj sieć polityki i przenieś ją na wybrane urządzenie
        self.policy_net = LuigiCNN().to(self.device)  # **2. Przenieś model na urządzenie**

        # Załaduj wytrenowany model, jeśli istnieje
        if input_model_path is not None and os.path.exists(input_model_path):
            self.policy_net.load_state_dict(
                torch.load(input_model_path, map_location=self.device)
            )  # **3. Upewnij się, że model jest załadowany na poprawne urządzenie**

        # Używamy średniokwadratowego błędu jako funkcji straty
        self.loss_function = nn.MSELoss()

        # Optymalizator Adam zapewnia adaptacyjną szybkość uczenia i podejście oparte na momentum, które może pomóc sieci neuronowej szybciej się uczyć i szybciej zbiegać do optymalnego zestawu parametrów minimalizujących funkcję kosztu lub straty
        self.optimizer = torch.optim.Adam(
            self.policy_net.parameters(), lr=self.learning_rate
        )

    def remember(
        self,
        priority,
        state,
        action,
        reward,
        next_state,
        done,
        valid_moves,
        next_valid_moves,
    ):
        # jeśli pamięć jest pełna, usuwamy element o najmniejszym priorytecie
        if len(self.memory) >= self.MEMORY_SIZE:
            min_value = self.MAX_PRIORITY
            min_index = 0
            for i, n in enumerate(self.memory):
                # priorytet jest przechowywany na pierwszej pozycji krotki
                if n[0] < min_value:
                    min_value = n[0]
                    min_index = i
            del self.memory[min_index]

        self.memory.append(
            (
                priority,
                state,
                action,
                reward,
                next_state,
                done,
                valid_moves,
                next_valid_moves,
            )
        )

    def select_action(self, board):
        bit_state = convert_state(board)
        valid_moves_tensor, valid_move_dict = mask_and_valid_moves(board)
        valid_moves_tensor = valid_moves_tensor.to(self.device)


        fen = board.fen()
        if fen in self.openings_dict:
            logging.info(f"uzycie ruchu otwarcia dla FEN: {fen}")
            opening_moves = self.openings_dict[fen]
            chosen_move = chess.Move.from_uci(random.choice(opening_moves))
            return get_move_index(chosen_move), chosen_move, bit_state, valid_moves_tensor
        else:
            logging.info(f"pozycja: {fen} nie znajduje sie w bazie otwarc")



        if random.uniform(0, 1) <= self.epsilon:
            if random.uniform(0, 1) <= self.mcts_move_prob:
                possible_mcts_moves = [move.uci() for move in valid_move_dict.values()]
                random.shuffle(possible_mcts_moves) # Obrzydliwy hack. napraw mcts. Mario na razie jest debilem
                chosen_move = Mario_get_best_move(
                    starting_fen=board.fen(),
                    iterations=self.mcts_iterations,
                    branching_factor=len(possible_mcts_moves),
                    root_moves=possible_mcts_moves,
                    max_depth=self.mcts_rollout_depth,
                )
                logging.info(f"Ruch MCTS: {chosen_move} fen przekazany: {board.fen()}")
            else:
                chosen_move = random.choice(list(valid_move_dict.values()))
        else:
            with torch.no_grad():
                tensor = (
                    torch.from_numpy(bit_state).float().unsqueeze(0).to(self.device)
                )
                policy_values = self.policy_net(tensor, valid_moves_tensor)
                chosen_move_index = policy_values.argmax(dim=1).item()

                chosen_move = valid_move_dict.get(
                    chosen_move_index, random.choice(list(board.legal_moves))
                )

        return get_move_index(chosen_move), chosen_move, bit_state, valid_moves_tensor

    def learn(self, debug=False):
        batch_size = self.batch_size

        # jeśli pamięć nie ma wystarczającej liczby próbek do wypełnienia partii, zwróć
        if len(self.memory) < batch_size:
            return

        priorities = [sample[0] for sample in self.memory]
        weights = np.array(priorities) / np.sum(priorities)

        minibatch_indexes = np.random.choice(
            len(self.memory), size=batch_size, replace=False, p=weights
        )
        minibatch = [self.memory[idx] for idx in minibatch_indexes]

        # Rozpakuj krotki w partii za pomocą zrozumień list dla szybszego przetwarzania
        state_list, state_valid_moves, action_list, reward_list, done_list = zip(
            *[
                (
                    bit_state,
                    state_valid_move.unsqueeze(0).to(self.device),
                    [action],
                    reward,
                    done,
                )
                for _, bit_state, action, reward, _, done, state_valid_move, _ in minibatch
            ]
        )

        # Filtruj następne stany, w których gra się nie zakończyła
        next_states = [
            (next_bit_state, next_state_valid_move.unsqueeze(0).to(self.device))
            for _, _, _, _, next_bit_state, done, _, next_state_valid_move in minibatch
            if not done
        ]

        if next_states:
            next_state_list, next_state_valid_moves = zip(*next_states)
            next_state_list = list(next_state_list)
            next_state_valid_moves = list(next_state_valid_moves)
        else:
            next_state_list = []
            next_state_valid_moves = []

        # state_valid_moves i next_state_valid_moves są już tensorami, wystarczy je połączyć
        state_valid_move_tensor = torch.cat(state_valid_moves, 0).to(
            self.device
        )  # **6. Przenieś tensor na urządzenie**
        next_state_valid_move_tensor = torch.cat(next_state_valid_moves, 0).to(
            self.device
        )  # **6. Przenieś tensor na urządzenie**

        # przekonwertuj wszystkie listy na tensory i przenieś na urządzenie
        state_tensor = (
            torch.from_numpy(np.array(state_list)).float().to(self.device)
        )  # **7. Przenieś tensor na urządzenie**
        action_list_tensor = torch.from_numpy(np.array(action_list, dtype=np.int64)).to(
            self.device
        )  # **7. Przenieś tensor na urządzenie**
        reward_list_tensor = (
            torch.from_numpy(np.array(reward_list)).float().to(self.device)
        )  # **7. Przenieś tensor na urządzenie**
        next_state_tensor = (
            torch.from_numpy(np.array(next_state_list)).float().to(self.device)
        )  # **7. Przenieś tensor na urządzenie**

        # utwórz tensor z
        bool_array = np.array([not x for x in done_list])
        not_done_mask = torch.tensor(bool_array, dtype=torch.bool).to(
            self.device
        )  # **7. Przenieś tensor na urządzenie**

        # oblicz oczekiwane nagrody dla każdego legalnego ruchu
        policy_action_values = self.policy_net(state_tensor, state_valid_move_tensor)

        # pobierz tylko oczekiwaną nagrodę za wybrany ruch (aby obliczyć stratę w stosunku do rzeczywistej nagrody)
        policy_action_values = policy_action_values.gather(1, action_list_tensor)

        # wartości docelowe to to, co chcemy, aby sieć przewidywała (nasze rzeczywiste wartości w funkcji straty)
        # wartości docelowe = nagroda + max_reward_in_next_state * gamma
        # gamma to współczynnik dyskonta i określa, czy agent preferuje długoterminowe nagrody czy natychmiastowe. 0 = zachłanne, 1 = długoterminowe
        max_reward_in_next_state = torch.zeros(batch_size, dtype=torch.double).to(
            self.device
        )  # **7. Przenieś tensor na urządzenie**

        with torch.no_grad():
            # jeśli stan jest końcowy (done = True, not_done_mask = False) max_reward_in_next_state pozostaje 0
            max_reward_in_next_state[not_done_mask] = self.policy_net(
                next_state_tensor, next_state_valid_move_tensor
            ).max(1)[0]

        target_action_values = (
            max_reward_in_next_state * self.gamma
        ) + reward_list_tensor
        target_action_values = target_action_values.unsqueeze(1)

        # strata jest obliczana między wartościami oczekiwanymi (przewidywanymi) a wartościami docelowymi (rzeczywistymi)
        loss = self.loss_function(policy_action_values, target_action_values)

        # Zaktualizuj priorytety próbek w pamięci na podstawie wielkości błędu (większy błąd = wyższy priorytet)
        priorities = (
            F.mse_loss(policy_action_values, target_action_values, reduction="none")
            .mean(dim=1)
            .detach()
            .cpu()
            .numpy()
        )
        for idx, priority in zip(minibatch_indexes, priorities):
            sample = list(self.memory[idx])
            sample[0] = priority
            self.memory[idx] = tuple(sample)

        # wyczyść gradienty wszystkich parametrów z poprzedniego kroku treningowego
        self.optimizer.zero_grad()

        # oblicz nowe gradienty straty w stosunku do wszystkich parametrów modelu, przechodząc przez sieć wstecz
        loss.backward()

        # dostosuj parametry modelu (wagi, przesunięcia) zgodnie z obliczonymi gradientami i szybkością uczenia
        self.optimizer.step()

        if debug:
            logging.debug("state_tensor shape %s", state_tensor.shape)
            logging.debug("\naction_list_tensor shape %s", action_list_tensor.shape)
            logging.debug(
                "\naction_list_tensor (wybrany ruch spośród 4096) %s", action_list_tensor
            )
            logging.debug(
                "\npolicy_action_values (oczekiwana nagroda za wybrany ruch) %s",
                policy_action_values,
            )
            logging.debug("\nnot_done_mask %s", not_done_mask)
            logging.debug("\ntarget_action_values %s", target_action_values)
            logging.debug("\nreward_list_tensor %s", reward_list_tensor)
            logging.debug("\nstrata: %s", loss)

        # zwróć stratę, aby można było wykreślić stratę na krok treningowy
        return float(loss)

    def decay_epsilon(self) -> None:
        """
        Zmniejsza współczynnik eksploracji epsilon, zapewniając, że nie spadnie poniżej epsilon_min.
        """
        old_epsilon = self.epsilon
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
        if old_epsilon != self.epsilon:
            logging.debug(f"Zmniejszono epsilon z {old_epsilon} do {self.epsilon}")

    def save_model(self, path: str) -> None:
        """
        Zapisuje słownik stanu sieci polityki do określonej ścieżki.

        Argumenty:
            path (str): Ścieżka do pliku, w którym zapisany zostanie model.
        """
        try:
            # Zapisz model do określonego urządzenia
            torch.save(self.policy_net.state_dict(), path)
            logging.info(f"Model zapisany pomyślnie w {path}")
        except Exception as e:
            logging.error(f"Nie udało się zapisać modelu w {path}: {e}")
