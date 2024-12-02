# agent.py

import os
import chess
import torch
import torch.nn.functional as F
import random
from model import LuigiCNN
from chess_utils import (
    index_to_move,
    move_to_index,
    board_to_tensor,
    get_action_mask
)
from mcts_interface import MCTSInterface
import logging
from torch.distributions import Categorical

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ChessAgent:
    def __init__(self, lr=1e-4, gamma=0.99, entropy_coef=0.01, agent_color=chess.WHITE, device='cpu', mcts_binary_path=None):
        """
        Inicjalizuje ChessAgent.

        Parametry:
        - lr (float): Współczynnik uczenia dla optymalizatora.
        - gamma (float): Współczynnik dyskontowania dla przyszłych nagród.
        - entropy_coef (float): Współczynnik regularyzacji entropii.
        - agent_color (chess.Color): Kolor agenta (chess.WHITE lub chess.BLACK).
        - device (str): Urządzenie do uruchamiania modelu ('cpu' lub 'cuda').
        - mcts_binary_path (str, opcjonalnie): Ścieżka do wykonywalnego pliku binarnego MCTS w C++. Jeśli None, MCTS jest wyłączony.
        """
        self.device = device
        self.action_channels = 1  # Zmieniono z 10 na 1
        self.model = LuigiCNN(action_channels=self.action_channels).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.gamma = gamma
        self.entropy_coef = entropy_coef
        self.agent_color = agent_color
        self.mcts_interface = MCTSInterface(mcts_binary_path=mcts_binary_path) if mcts_binary_path else None

        # Przechowywanie logarytmicznych prawdopodobieństw i nagród
        self.log_probs = []
        self.rewards = []


'''
    data = pd.read_csv('../../datasets/fen_moves.tsv', delimiter='\t')
    fen_moves_dict = data.groupby('FEN')['Move'].apply(list).to_dict()

    def move(self, board, epsilon=0.1):
        opening_moves = fen_moves_dict[board.fen()]
        if opening_moves:
            return random.choice(opening_moves)
        return select_move(self,board,epsilon)
'''





    def select_move(self, board, epsilon=0.1):
        """
        Wybiera ruch za pomocą polityki sieci i MCTS, jeśli jest dostępny, z wykorzystaniem strategii epsilon-zachłannej.

        Parametry:
        - board (chess.Board): Aktualna plansza gry.
        - epsilon (float): Prawdopodobieństwo wybrania losowego ruchu (strategia epsilon-zachłanna).

        Zwraca:
        - chess.Move lub None: Wybrany ruch lub None, jeśli brak dostępnych ruchów.
        """
        # Konwertuj aktualną planszę na tensor i uzyskaj maskę akcji za pomocą chess_utils
        state = board_to_tensor(board).unsqueeze(0).to(self.device)  # Dodaj wymiar batcha i przenieś na urządzenie
        action_mask = get_action_mask(board).unsqueeze(0).to(self.device)  # Dodaj wymiar batcha

        # Epsilon-zachłanna strategia: wybierz losowy ruch z prawdopodobieństwem epsilon
        if random.random() < epsilon:
            return self._select_random_move(board)

        # Użyj MCTS do wyboru ruchu, jeśli dostępne
        if self.mcts_interface:
            move = self._select_move_with_mcts(board, state, action_mask)
            if move:
                return move  # Ruch został pomyślnie wybrany przez MCTS
            else:
                self._select_move_with_policy(board, state, action_mask)
            
        # Użyj polityki sieci do wyboru ruchu
        return self._select_move_with_policy(board, state, action_mask)


    def _select_random_move(self, board):
        """
        Wybiera losowy, legalny ruch.

        Parametry:
        - board (chess.Board): Aktualna plansza gry.

        Zwraca:
        - chess.Move: Losowo wybrany ruch.
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            logger.warning("Brak dostępnych legalnych ruchów dla agenta.")
            return None
        selected_move = random.choice(legal_moves)
        # Przypisz neutralne log_prob (bez wkładu w gradient)
        # Ustawienie log_prob na 0.0 zapewnia, że nie wpływa na proces uczenia
        log_prob = torch.tensor(0.0, device=self.device)
        self.log_probs.append(log_prob)
        logger.debug(f"Losowo wybrany ruch: {board.san(selected_move)} z neutralnym prawdopodobieństwem {log_prob.item()}")
        return selected_move


    def _select_move_with_mcts(self, board, state, action_mask):
        """
        Wybiera ruch za pomocą silnika MCTS i loguje prawdopodobieństwo polityki sieciowej dla tego ruchu.

        Parametry:
        - board (chess.Board): Aktualna plansza gry.
        - state (torch.Tensor): Reprezentacja tensorowa aktualnego stanu planszy.
        - action_mask (torch.Tensor): Maska akcji wskazująca legalne ruchy.

        Zwraca:
        - chess.Move lub None: Wybrany ruch lub None, jeśli MCTS zawiedzie.
        """
        fen = board.fen()
        selected_move_uci = self.mcts_interface.get_move(fen)
        if selected_move_uci:
            try:
                selected_move = chess.Move.from_uci(selected_move_uci)
                if selected_move in board.legal_moves:
                    # Znajdź indeks ruchu za pomocą chess_utils
                    move_idx = move_to_index(selected_move)
                    logger.debug(f"Indeks ruchu wybranego przez MCTS: {move_idx}")

                    # Pobierz prawdopodobieństwa polityki sieciowej
                    with torch.no_grad():
                        self.model.eval()
                        output, _ = self.model(state, action_mask)  # Zakładając, że model zwraca politykę i wartość
                        # Przekształć wynik w [batch_size, action_channels, 4096]
                        output = output.view(-1, self.action_channels, 4096)
                        # Zamaskuj nielegalne ruchy
                        masked_output = output * action_mask
                        # Zastosuj softmax, aby uzyskać prawdopodobieństwa dla wszystkich akcji
                        action_probs = F.softmax(masked_output.view(-1), dim=0)
                    # Wyciągnij prawdopodobieństwo dla wybranego ruchu
                    move_prob = action_probs[move_idx]
                    # Zaloguj prawdopodobieństwo polityki sieciowej dla tego ruchu (odłączone, aby uniknąć śledzenia gradientu)
                    log_prob = torch.log(move_prob).detach()
                    self.log_probs.append(log_prob)
                    logger.debug(f"Ruch wybrany przez MCTS: {board.san(selected_move)} z prawdopodobieństwem sieci {move_prob.item()}")
                    return selected_move
                else:
                    logger.warning(f"MCTS zwrócił nielegalny ruch: {selected_move_uci}.")
            except ValueError:
                logger.warning(f"MCTS zwrócił nieprawidłowy ruch UCI: {selected_move_uci}.")
            except IndexError as e:
                logger.error(f"Błąd w move_to_index: {e}.")
            except Exception as e:
                logger.error(f"Nieoczekiwany błąd w wyborze ruchu przez MCTS: {e}.")
        else:
            logger.warning("MCTS nie zwrócił ruchu.")
        return None  # MCTS nie podał prawidłowego ruchu


    def _select_move_with_policy(self, board, state, action_mask):
        """
        Wybiera ruch na podstawie polityki sieci.

        Parametry:
        - board (chess.Board): Aktualna plansza gry.
        - state (torch.Tensor): Reprezentacja tensorowa aktualnego stanu planszy.
        - action_mask (torch.Tensor): Maska akcji wskazująca legalne ruchy.

        Zwraca:
        - chess.Move lub None: Wybrany ruch lub None, jeśli brak dostępnych legalnych ruchów.
        """
        self.model.train()  # Upewnij się, że model jest w trybie treningowym, aby śledzić gradienty
        output, _ = self.model(state, action_mask)
        # Przekształć wynik w [batch_size, action_channels, 4096]
        output = output.view(-1, self.action_channels, 4096)
        
        # Zastosuj maskowanie poprzez ustawienie logitów nielegalnych ruchów na -inf
        masked_output = output.clone()
        masked_output[action_mask == 0] = -1e9  # Efektywnie usuwa nielegalne ruchy z rozważań
        
        # Zastosuj softmax, aby uzyskać prawdopodobieństwa dla wszystkich akcji
        action_probs = F.softmax(masked_output.view(-1), dim=0)
        
        # Utwórz rozkład kategoryczny
        m = Categorical(action_probs)
        action = m.sample()
        log_prob = m.log_prob(action)  # Ten tensor wymaga gradientu

        move_idx = action.item()
        logger.debug(f"Wylosowany indeks ruchu: {move_idx}")

        # Sprawdź, czy move_idx jest w prawidłowym zakresie
        if move_idx < 0 or move_idx >= 4096:
            logger.error(f"Wylosowany indeks akcji {move_idx} jest poza zakresem (0-4095). Wybieranie losowego ruchu.")
            return self._select_random_move(board)

        try:
            selected_move = index_to_move(board, move_idx)
            if selected_move not in board.legal_moves:
                logger.warning(f"Sieć wybrała nielegalny ruch: {selected_move}. Zamiast tego wybieranie losowego ruchu.")
                return self._select_random_move(board)

            # Zaloguj prawdopodobieństwo polityki sieci dla wybranego ruchu
            move_prob = action_probs[move_idx]
            self.log_probs.append(log_prob)  # Zapisz log_prob z gradientem
            logger.debug(f"Sieć wybrała ruch: {board.san(selected_move)} z prawdopodobieństwem {move_prob.item()}")
            return selected_move

        except IndexError as e:
            logger.error(f"Błąd w index_to_move: {e}. Zamiast tego wybieranie losowego ruchu.")
            return self._select_random_move(board)
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd w index_to_move: {e}. Zamiast tego wybieranie losowego ruchu.")
            return self._select_random_move(board)



    def remember(self, reward):
        """
        Przechowuje otrzymaną nagrodę.

        Parametry:
        - reward (float): Nagroda otrzymana po wykonaniu akcji.
        """
        self.rewards.append(reward)

    def learn(self):
        """
        Wykonuje krok uczenia, aktualizując sieć neuronową na podstawie zapisanych logarytmów prawdopodobieństwa i nagród.
        """
        if not self.rewards:
            logger.debug("Brak nagród do nauki.")
            return  # Brak danych do nauki

        self.model.train()

        # Oblicz zdyskontowane nagrody
        discounted_rewards = []
        R = 0
        for r in reversed(self.rewards):
            R = r + self.gamma * R
            discounted_rewards.insert(0, R)

        discounted_rewards = torch.tensor(discounted_rewards, device=self.device)

        # Normalizacja zdyskontowanych nagród (opcjonalna)
        #if len(discounted_rewards) > 1:  # Sprawdź, czy są wystarczające dane do normalizacji
        #    mean = discounted_rewards.mean()
        #    std = discounted_rewards.std()
        #    if std > 0:
        #        discounted_rewards = (discounted_rewards - mean) / (std + 1e-9)

        # Upewnij się, że zdyskontowane nagrody mają włączone śledzenie gradientów
        # discounted_rewards = discounted_rewards.clone().detach()

        # Oblicz straty
        policy_losses = []
        entropy_losses = []
        for log_prob, reward in zip(self.log_probs, discounted_rewards):
            if log_prob.requires_grad:
                policy_losses.append(-log_prob * reward)
                # Opcjonalna regularizacja entropii
                entropy = -(torch.exp(log_prob) * log_prob)
                entropy_losses.append(entropy)

        if not policy_losses:
            logger.debug("Brak prawidłowych log_probs do nauki.")
            # Wyczyść zapisane nagrody i log_probs nawet jeśli nie ma danych do nauki
            self.log_probs = []
            self.rewards = []
            return

        # Sumowanie strat
        policy_loss = torch.stack(policy_losses).sum()
        entropy_loss = torch.stack(entropy_losses).sum() * self.entropy_coef if entropy_losses else 0
        total_loss = policy_loss + entropy_loss

        # Backpropagation (propagacja wsteczna)
        self.optimizer.zero_grad()
        total_loss.backward()
        # Ograniczenie gradientów dla stabilności
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        self.optimizer.step()

        # Wyczyść zapisane nagrody i log_probs
        self.log_probs = []
        self.rewards = []

        logger.debug("Parametry modelu zaktualizowane.")







    def save_model(self, filepath, episode=None, rewards_history=None):
        """
        Zapisuje stan modelu i optymalizatora do pliku.

        Parametry:
        - filepath (str): Ścieżka do zapisu modelu.
        - episode (int, opcjonalnie): Numer epizodu treningowego.
        - rewards_history (list, opcjonalnie): Historia nagród.
        """
        # Upewnij się, że katalog istnieje
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'gamma': self.gamma,
            'entropy_coef': self.entropy_coef,
            'agent_color': self.agent_color,
            'log_probs': self.log_probs,
            'rewards': self.rewards
        }
        if episode is not None:
            checkpoint['episode'] = episode
        if rewards_history is not None:
            checkpoint['rewards_history'] = rewards_history
        torch.save(checkpoint, filepath)
        logger.info(f"Model zapisany do {filepath}")

    def load_model(self, filepath):
        """
        Ładuje stan modelu i optymalizatora z pliku.

        Parametry:
        - filepath (str): Ścieżka do załadowania modelu.
        """
        if not os.path.isfile(filepath):
            logger.error(f"Plik punktu kontrolnego nie znaleziony w ścieżce: {filepath}")
            return

        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.gamma = checkpoint.get('gamma', self.gamma)
        self.entropy_coef = checkpoint.get('entropy_coef', self.entropy_coef)
        self.agent_color = checkpoint.get('agent_color', self.agent_color)
        self.log_probs = checkpoint.get('log_probs', [])
        self.rewards = checkpoint.get('rewards', [])
        logger.info(f"Model załadowany z {filepath}")

    def close_mcts(self):
        """
        Zamyka interfejs MCTS, jeśli istnieje.
        """
        if self.mcts_interface:
            self.mcts_interface.close()
            logger.info("Interfejs MCTS został zamknięty.")
