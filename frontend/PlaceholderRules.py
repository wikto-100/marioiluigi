def try_move(source, target, board_state):
    move_accepted = True
    winner = None
    new_state = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' , 'wP', ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            ['wP', 'wP', 'wP',  '', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
    move = "Pd4"

    if source == (6,3) and target == (4,3):
        return move_accepted, winner, new_state, move
    else:
        return False, None, 0, 0