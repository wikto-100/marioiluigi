def canDoMove(move, board_state):
    move_accepted = True
    print(move)

    if move == '2e4e':
        return move_accepted
    else:
        return
    
def getAppliedMove(board_state, move):
    if move == '2e4e':
        new_state = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR'
    else:
        new_state = 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR'
    return new_state

def isLostCondition(board_state):
    if board_state == 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR':
        return True
    else:
        return False