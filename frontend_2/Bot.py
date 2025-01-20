from src import chess_agent
from src import train_utils
import chess

class Bot:
    def __init__(self, path):
        self.agent = chess_agent.ChessAgent(path)

    def move(self, state):
        board = chess.Board(state)
        return train_utils.choose_move(self.agent, board).uci()