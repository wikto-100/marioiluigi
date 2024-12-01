import math
import random
#import ../../shared/rules_to_tensor.py
#import ../../shared/network_evaluation.py

class MCTSNode:
    """
    klasa reprezentujaca wezel w drzewie wyszukiwania mcts

    atrybuty:
        board (notacja fen, string) - stan planszy szachowej w danym wezle
        parent (MCTSNode) - wezel nadrzedny
        move (string) - ruch ktory doprowadzil do obecnego stanu planszy z parenta
        children (list) - lista dzieci wezla wynikajaca z legalnych ruchow
        visits (int) - liczba razy, ile razy ten wezel byl odwiedzany
        wins (int) - liczba wygranych dla tego wezla
        untried_moves (list) - lista ruchow ktore nie byly jeszcze wykonane
    """

    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = get_legal_moves(board)

    def is_fully_expanded(self):
        """
        returns:
            true jesli wezel w pelni rozwiniety
            false w przeciwnym wypadku
        """
        return len(self.untried_moves) == 0

    def best_child(self, exploration_weight=1.4):
        """
        znajduje najlepsze dziecko na podstawie rownania balansu i eksploracji (formula UCB)
        args:
            exploration_weight (float) - waga wspolczynnika eksploracji
                (wyzsze wartosci sklaniaja do czestszego badania nowych ruchow)
        returns:
            (MCTSNode) - wezel dziecka o najwyzszym wyniku
        """

        best_score = -float('inf')
        best_child = None
        for child in self.children:
            exploit = child.wins / child.visits
            explore = math.sqrt(math.log(self.visits) / child.visits)
            score = exploit + exploration_weight * explore
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self):
        """
        rozwija biezacy wezel przez dodanie jednego z nieprzebadanych ruchow jako dziecka.
        
        returns:
            nowo utworzony wezel dziecka
        """

        move = self.untried_moves.pop()
        new_board = apply_move(self.board, move)
        child_node = MCTSNode(new_board, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def update(self, result):
        """
        aktualizuje wezel na podstawie wyniku symulacji

        args:
            result (float) - wynik symulacji
        """

        self.visits += 1
        self.wins += result

def mcts(board, simulations=1000):
    """
    znajduje najlepszy ruch na podstawie danego stanu planszy korzystajac z algo mcts

    args:
        board (notacja fen) - aktualny stan planszy
        simulations (int) - liczba symulacji ktore zostana przeprowadzone aby odnalezc najlepszy ruch, domyslnie 1000

    zwraca:
        move (string) - najlepszy ruch
    """

    root = MCTSNode(board)

    for _ in range(simulations):
        node = root

        #1) selekcja - wybiermy najbardziej obiecujacy wezel az do pelnej ekspansji
        while not node.is_fully_expanded() and node.children:
            node = node.best_child()

        #2) ekspansja - tworzymy nowy wezel dziecka, jesli sa nieprzebadane ruchy
        if not node.is_fully_expanded():
            node = node.expand()

        #3) symulacja - wykonujemy symulacje losowych ruchow do konca gry
        current_board = node.board
        while not is_game_over(current_board):
            possible_moves = get_legal_moves(current_board)
            move = random.choice(possible_moves)
            current_board = apply_move(current_board, move)

        #ocena wyniku przez siec neuronowa
        result = network_evaluation(current_board)

        #4) aktualizacja - propagacja wyniku symulacji w gore drzewa
        while node is not None:
            node.update(result)
            node = node.parent

    return max(root.children, key=lambda child: child.visits).move

