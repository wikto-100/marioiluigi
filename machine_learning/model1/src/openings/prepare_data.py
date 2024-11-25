#prepare_data.py


import pandas as pd
import chess
import sys
import os
import torch

sys.path.append(os.path.abspath('../'))

from chess_utils import board_to_tensor, move_to_index
from sklearn.model_selection import train_test_split

data = pd.read_csv('../../../datasets/fen_moves.tsv', delimiter='\t')

input_tensors = []
output_indices = []

for _, row in data.iterrows():
    fen, move = row['FEN'], row['Move']
    board = chess.Board(fen)

    input_tensor = board_to_tensor(board)
    input_tensors.append(input_tensor)

    move_index = move_to_index(chess.Move.from_uci(move))
    output_indices.append(move_index)

inputs = torch.stack(input_tensors)
targets = torch.tensor(output_indices)

train_inputs, val_inputs, train_targets, val_targets = train_test_split(
    inputs, targets, test_size=0.2, random_state=42
)

torch.save({
    'train_inputs': train_inputs,
    'val_inputs': val_inputs,
    'train_targets': train_targets,
    'val_targets': val_targets
}, "data_preprocessed.pt")

