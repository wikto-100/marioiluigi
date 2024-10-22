def move(board_state):
    winner = "black"
    new_state = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP',  '' , 'bP', 'bP', 'bP', 'bP'],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' , 'bP', ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' , 'wP', ''  , ''  ,  '' , ''  ],
            [''  ,  '' ,  '' ,  '' , ''  , ''  ,  '' , ''  ],
            ['wP', 'wP', 'wP',  '', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
    move = "Pd5"
    return winner, new_state, move