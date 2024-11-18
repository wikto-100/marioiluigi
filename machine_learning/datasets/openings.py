#DATASET Z: https://github.com/lichess-org/chess-openings


import pandas as pd
import os
import chess.pgn
import io
from sklearn.model_selection import train_test_split


tsv_files = [f for f in os.listdir("./") if f.endswith('tsv')]

dataframes = []
for file in tsv_files:
    file_path = os.path.join("./", file)
    df = pd.read_csv(file_path, sep="\t")
    dataframes.append(df)

combined_data = pd.concat(dataframes, ignore_index=True)

output_file = "./all.tsv"

combined_data.to_csv(output_file, sep="\t", index=False)

pgn_list = combined_data['pgn'].tolist()

fen_moves = []
for pgn in pgn_list:
    game = chess.pgn.read_game(io.StringIO(pgn))
    if not game:
        continue
    board = game.board()
    for move in game.mainline_moves():
        fen_moves.append((board.fen(), str(move)))
        board.push(move)

fen_moves_df = pd.DataFrame(fen_moves, columns=['FEN', 'Move'])
fen_moves_output_file = "./fen_moves.tsv"
fen_moves_df.to_csv(fen_moves_output_file, sep="\t", index=False)

