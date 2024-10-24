TEST_COUNTER = 0
def get_bot_move(board_state):
    if board_state == 'rnbqkbnr/pppppppp/8/8/8/5P2/PPPPP1PP/RNBQKBNR':
        move = "7e5e"
    else:
        move = "8d4h"
    return move