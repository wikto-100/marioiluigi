import pandas as pd
import os

"""
file_path = os.path.join(os.path.dirname(__file__), 'openings', 'opening_moves.tsv')
opening_data = pd.read_csv(file_path, delimiter='\t')
"""

os.chdir(os.path.dirname(__file__))

def get_openings():
    #laduje baze danych z openingami i zwraca jako slownik (fen, move)

    opening_data = pd.read_csv('./opening_moves.tsv', delimiter='\t')
    fen_moves_dict = opening_data.groupby('FEN')['Move'].apply(list).to_dict()

    return fen_moves_dict
