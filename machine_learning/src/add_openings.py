import pandas as pd

def get_openings():
    #laduje baze danych z openingami i zwraca jako slownik (fen, move)

    opening_data = pd.read_csv('../datasets/fen_moves.tsv', delimiter='\t')
    fen_moves_dict = opening_data.groupby('FEN')['Move'].apply(list).to_dict()

    return fen_moves_dict
