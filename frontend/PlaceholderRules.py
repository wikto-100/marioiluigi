def canDoMove(move, board_state):
    move_accepted = True
    print(move)

    if move == '2f3f' or move == '2g4g':
        return move_accepted
    else:
        return False
    
def getAppliedMove(board_state, move):
    if move == '2f3f':
        new_state = 'rnbqkbnr/pppppppp/8/8/8/5P2/PPPPP1PP/RNBQKBNR'
    elif move == '2g4g':
        new_state = 'rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR'
    elif move == '7e5e':
        new_state = 'rnbqkbnr/pppp1ppp/8/4p3/8/5P2/PPPPP1PP/RNBQKBNR'
    else:
        new_state = 'rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR'
    return new_state

def isLostCondition(board_state):
    if board_state == 'rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR':
        return True
    else:
        return False